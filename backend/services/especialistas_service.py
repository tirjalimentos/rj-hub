"""
Regras de negócio relacionadas aos Especialistas.
Antes: retornava uma lista mockada em memória.
Agora: consulta o banco de dados (SQLite) via SQLAlchemy.

As rotas em api/routes/especialistas.py não mudaram nada — elas não
sabem, e não precisam saber, que a fonte dos dados mudou.
"""

from db.database import SessionLocal
from db.models_db import (
    ConversaDB,
    EspecialistaDB,
    DocumentoConhecimentoDB,
    GrupoEspecialistaDB,
    WorkspaceMembroDB,
)
from models.especialista import Especialista


def _para_schema(row: EspecialistaDB) -> Especialista:
    """Converte uma linha do banco (EspecialistaDB) no schema da API (Especialista)."""
    return Especialista(
        id=row.id,
        nome=row.nome,
        icone=row.icone,
        desc=row.desc,
        docs=row.docs,
        proc=row.proc,
        atualizado=row.atualizado,
        favorito=row.favorito,
        status=row.status,
    )


def listar_especialistas() -> list[Especialista]:
    db = SessionLocal()
    try:
        rows = db.query(EspecialistaDB).all()
        return [_para_schema(row) for row in rows]
    finally:
        db.close()


def buscar_especialista(especialista_id: str) -> Especialista | None:
    db = SessionLocal()
    try:
        row = db.get(EspecialistaDB, especialista_id)
        return _para_schema(row) if row else None
    finally:
        db.close()


# ---------------------------------------------------------------
# Escrita — usado pelo painel de Super-Admin (api/routes/admin.py).
# A leitura acima continua sendo usada por qualquer fluxo normal do
# app; esta função só é chamada em rota protegida por get_current_admin.
# ---------------------------------------------------------------
def criar_especialista(id: str, nome: str, icone: str, desc: str) -> Especialista:
    db = SessionLocal()
    try:
        if db.get(EspecialistaDB, id):
            raise ValueError(f"Já existe um especialista com o id '{id}'.")

        row = EspecialistaDB(
            id=id,
            nome=nome,
            icone=icone,
            desc=desc,
            docs=0,
            proc=0,
            atualizado="agora",
            favorito=False,
            status="ok",
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return _para_schema(row)
    finally:
        db.close()


# Exclusão bloqueia (não deleta em cascata) se o especialista tiver
# qualquer dependência viva — documentos na Base de Conhecimento,
# vínculo com grupo, presença em workspace, ou histórico de
# conversas. Decisão deliberada: excluir em cascata apagaria dado
# (documentos, histórico) sem confirmação explícita do que está
# sendo perdido; bloquear obriga o Admin a limpar cada dependência
# antes, uma de cada vez, e sabendo exatamente o que está fazendo.
# A rota (api/routes/admin.py) já garante que o especialista existe
# antes de chamar esta função (via buscar_especialista).
def deletar_especialista(id: str) -> None:
    db = SessionLocal()
    try:
        row = db.get(EspecialistaDB, id)
        if row is None:
            raise ValueError(f"Especialista '{id}' não encontrado.")

        qtd_docs = db.query(DocumentoConhecimentoDB).filter_by(especialista_id=id).count()
        if qtd_docs:
            raise ValueError(
                f"Especialista possui {qtd_docs} documento(s) na Base de Conhecimento. "
                "Remova os documentos antes de excluir (você pode exportá-los "
                "primeiro como backup, na própria aba Especialistas)."
            )

        qtd_grupos = db.query(GrupoEspecialistaDB).filter_by(especialista_id=id).count()
        if qtd_grupos:
            raise ValueError(
                f"Especialista está vinculado a {qtd_grupos} grupo(s). "
                "Desvincule-o na aba Grupos antes de excluir."
            )

        qtd_workspaces = db.query(WorkspaceMembroDB).filter_by(especialista_id=id).count()
        if qtd_workspaces:
            raise ValueError(
                f"Especialista pertence a {qtd_workspaces} workspace(s). "
                "Remova-o dos workspaces antes de excluir."
            )

        qtd_conversas = db.query(ConversaDB).filter_by(especialista_id=id).count()
        if qtd_conversas:
            raise ValueError(
                f"Especialista possui {qtd_conversas} conversa(s) registrada(s). "
                "Não é possível excluir um especialista com histórico de conversas."
            )

        db.delete(row)
        db.commit()
    finally:
        db.close()
