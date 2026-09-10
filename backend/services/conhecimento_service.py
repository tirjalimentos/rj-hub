"""
Regras de negócio da Base de Conhecimento.
Guarda o texto completo dos documentos de cada especialista e sabe
selecionar, para uma pergunta específica, quais desses documentos
são relevantes o suficiente para entrar no contexto do motor de IA.

Relevância aqui é por contagem simples de palavras em comum entre a
pergunta e o documento (título pesa mais que o corpo) — não usa
embeddings nem busca vetorial. Para o volume esperado (dezenas de
documentos por especialista), isso é suficiente e evita depender de
um serviço externo ou de infraestrutura extra só para isso. Se o
volume crescer muito (centenas+), vale revisitar essa escolha.
"""

import io
import re
import zipfile

from db.database import SessionLocal
from db.models_db import DocumentoConhecimentoDB, EspecialistaDB
from models.conhecimento import DocumentoConhecimento

# Palavras curtas demais (artigos, preposições etc.) não ajudam a
# medir relevância e só adicionam ruído — são ignoradas na busca.
_PALAVRAS_IGNORADAS = {
    "de", "da", "do", "das", "dos", "para", "por", "com", "sem", "que",
    "uma", "um", "uns", "umas", "como", "qual", "quais", "quando",
    "onde", "porque", "pra", "sobre", "meu", "minha", "seu", "sua", "não",
}

_TITULO_PESO = 3  # ocorrência no título vale mais do que no corpo do texto


def _para_schema(row: DocumentoConhecimentoDB) -> DocumentoConhecimento:
    return DocumentoConhecimento(
        id=row.id,
        especialista_id=row.especialista_id,
        titulo=row.titulo,
        conteudo=row.conteudo,
    )


def _extrair_palavras_chave(texto: str) -> list[str]:
    palavras = re.findall(r"\w+", texto.lower())
    return [p for p in palavras if len(p) >= 3 and p not in _PALAVRAS_IGNORADAS]


def listar_documentos(especialista_id: str) -> list[DocumentoConhecimento]:
    db = SessionLocal()
    try:
        rows = (
            db.query(DocumentoConhecimentoDB)
            .filter_by(especialista_id=especialista_id)
            .all()
        )
        return [_para_schema(row) for row in rows]
    finally:
        db.close()


def buscar_contexto_relevante(
    especialista_id: str, pergunta: str, limite: int = 4
) -> list[DocumentoConhecimento]:
    """
    Retorna até `limite` documentos do especialista mais relevantes
    para a pergunta, ordenados do mais para o menos relevante.
    Retorna lista vazia se nenhum documento tiver palavras em comum
    com a pergunta (o ia_service decide o que fazer nesse caso).
    """
    palavras_chave = set(_extrair_palavras_chave(pergunta))
    if not palavras_chave:
        return []

    documentos = listar_documentos(especialista_id)

    pontuados = []
    for doc in documentos:
        palavras_titulo = set(_extrair_palavras_chave(doc.titulo))
        palavras_corpo = set(_extrair_palavras_chave(doc.conteudo))

        pontuacao = (
            len(palavras_chave & palavras_titulo) * _TITULO_PESO
            + len(palavras_chave & palavras_corpo)
        )
        if pontuacao > 0:
            pontuados.append((pontuacao, doc))

    pontuados.sort(key=lambda item: item[0], reverse=True)
    return [doc for _, doc in pontuados[:limite]]


# ---------------------------------------------------------------
# Escrita — usado pelo painel de Super-Admin (api/routes/admin.py).
# As funções acima (leitura) continuam sendo usadas por qualquer
# fluxo de chat normal; estas aqui só são chamadas em rotas
# protegidas por get_current_admin.
# ---------------------------------------------------------------


def criar_documento(especialista_id: str, titulo: str, conteudo: str) -> DocumentoConhecimento:
    db = SessionLocal()
    try:
        if db.get(EspecialistaDB, especialista_id) is None:
            raise ValueError(f"Especialista '{especialista_id}' não encontrado.")

        row = DocumentoConhecimentoDB(
            especialista_id=especialista_id, titulo=titulo, conteudo=conteudo
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return _para_schema(row)
    finally:
        db.close()


def deletar_documento(documento_id: int) -> None:
    db = SessionLocal()
    try:
        row = db.get(DocumentoConhecimentoDB, documento_id)
        if row is None:
            raise ValueError(f"Documento {documento_id} não encontrado.")
        db.delete(row)
        db.commit()
    finally:
        db.close()


# Exportação em massa — só leitura, não apaga nada do banco. Serve
# como backup manual antes de limpar a Base de Conhecimento de um
# especialista (por exemplo, pra desbloquear sua exclusão em
# especialistas_service.deletar_especialista, que exige zero
# documentos vinculados).
def exportar_documentos_zip(especialista_id: str) -> bytes:
    documentos = listar_documentos(especialista_id)

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as arquivo_zip:
        for indice, doc in enumerate(documentos, start=1):
            arquivo_zip.writestr(_nome_arquivo_seguro(doc.titulo, indice), doc.conteudo)

    return buffer.getvalue()


# Prefixa com índice pra evitar colisão entre documentos com título
# igual, e remove caracteres que quebram nome de arquivo em
# Windows/Linux (o usuário do projeto trabalha em Windows).
def _nome_arquivo_seguro(titulo: str, indice: int) -> str:
    limpo = re.sub(r'[\\/*?:"<>|]', "", titulo).strip() or "documento"
    return f"{indice:02d}_{limpo}.txt"
