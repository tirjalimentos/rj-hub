"""
Regras de negócio relacionadas à Biblioteca de Documentos.

Unificada com a Base de Conhecimento (DocumentoConhecimentoDB) —
antes eram 2 tabelas desconectadas (CategoriaDocumentoDB/DocumentoDB
tinham linhas semeadas manualmente, sem relação nenhuma com o que o
Super-Admin sobe de verdade pros especialistas). Agora a Biblioteca
mostra exatamente os mesmos documentos que alimentam o chat — não
existe mais duplicidade de dado.

Rota protegida por get_current_admin (ver api/routes/biblioteca.py):
só Super-Admin vê a Biblioteca agora, porque o conteúdo real de um
documento pode ser sensível — decisão tomada junto com o pedido de
unificação.
"""

from datetime import datetime

from db.database import SessionLocal
from db.models_db import DocumentoConhecimentoDB, EspecialistaDB
from models.documento import CategoriaDocumento, Documento


def listar_categorias() -> list[CategoriaDocumento]:
    """
    "Categoria" aqui é cada especialista — cada um com a contagem de
    documentos da própria Base de Conhecimento associados a ele.
    """
    db = SessionLocal()
    try:
        especialistas = db.query(EspecialistaDB).all()
        resultado = []
        for especialista in especialistas:
            qtd = (
                db.query(DocumentoConhecimentoDB)
                .filter_by(especialista_id=especialista.id)
                .count()
            )
            resultado.append(
                CategoriaDocumento(
                    icon=especialista.icone,
                    nome=especialista.nome,
                    qtd=f"{qtd} documento{'s' if qtd != 1 else ''}",
                )
            )
        return resultado
    finally:
        db.close()


def listar_documentos_recentes() -> list[Documento]:
    db = SessionLocal()
    try:
        rows = (
            db.query(DocumentoConhecimentoDB)
            .order_by(DocumentoConhecimentoDB.criado_em.desc())
            .all()
        )
        especialistas = {e.id: e for e in db.query(EspecialistaDB).all()}

        resultado = []
        for row in rows:
            especialista = especialistas.get(row.especialista_id)
            resultado.append(Documento(
                icon=especialista.icone if especialista else "📄",
                nome=row.titulo,
                area=especialista.nome if especialista else row.especialista_id,
                tag="Base de Conhecimento",
                quando=_humanizar_data(row.criado_em),
            ))
        return resultado
    finally:
        db.close()


def _humanizar_data(dt) -> str:
    agora = datetime.utcnow()
    dias = (agora - dt).days
    if dias <= 0:
        return "Atualizado hoje"
    if dias == 1:
        return "Atualizado ontem"
    return f"Atualizado há {dias} dias"
