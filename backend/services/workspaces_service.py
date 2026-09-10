"""
Regras de negócio relacionadas aos Workspaces.
Antes: retornava uma lista mockada em memória.
Agora: consulta o banco de dados (SQLite) via SQLAlchemy.

As rotas em api/routes/workspaces.py não mudam nada — elas não
sabem, e não precisam saber, que a fonte dos dados mudou.
"""

from db.database import SessionLocal
from db.models_db import WorkspaceDB
from models.workspace import Workspace


def _para_schema(row: WorkspaceDB) -> Workspace:
    """Converte uma linha do banco (WorkspaceDB) no schema da API (Workspace)."""
    return Workspace(
        id=row.id,
        nome=row.nome,
        icone=row.icone,
        # row.membros já vem ordenado (relationship ordena por "ordem");
        # aqui só extraímos os ids de especialista de cada associação.
        membros=[m.especialista_id for m in row.membros],
    )


def listar_workspaces() -> list[Workspace]:
    db = SessionLocal()
    try:
        rows = db.query(WorkspaceDB).all()
        return [_para_schema(row) for row in rows]
    finally:
        db.close()


def buscar_workspace(workspace_id: str) -> Workspace | None:
    db = SessionLocal()
    try:
        row = db.get(WorkspaceDB, workspace_id)
        return _para_schema(row) if row else None
    finally:
        db.close()
