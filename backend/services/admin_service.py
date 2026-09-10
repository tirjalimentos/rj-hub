"""
Regras de negócio do painel de Super-Admin — gerenciamento de grupos
de acesso e de quem pertence a cada um.

Complementa permissoes_service.py (que só LÊ, pra decidir o que cada
usuário pode ver). Este aqui ESCREVE — cria/edita/apaga grupos e
atribuições. Separado por responsabilidade: um é consultado a cada
requisição de qualquer usuário; o outro só é chamado por admins.
"""

from db.database import SessionLocal
from db.models_db import (
    AdministradorDB,
    EspecialistaDB,
    GrupoDB,
    GrupoEspecialistaDB,
    UsuarioGrupoDB,
)


def eh_administrador(email: str) -> bool:
    db = SessionLocal()
    try:
        return db.get(AdministradorDB, email) is not None
    finally:
        db.close()


def listar_grupos() -> list[dict]:
    """Cada grupo, com a lista de especialista_id que ele libera."""
    db = SessionLocal()
    try:
        grupos = db.query(GrupoDB).all()
        resultado = []
        for grupo in grupos:
            especialistas = (
                db.query(GrupoEspecialistaDB.especialista_id)
                .filter_by(grupo_id=grupo.id)
                .all()
            )
            resultado.append({
                "id": grupo.id,
                "nome": grupo.nome,
                "especialistas": [e[0] for e in especialistas],
            })
        return resultado
    finally:
        db.close()


def criar_grupo(grupo_id: str, nome: str) -> None:
    db = SessionLocal()
    try:
        if db.get(GrupoDB, grupo_id):
            raise ValueError(f"Já existe um grupo com o id '{grupo_id}'.")
        db.add(GrupoDB(id=grupo_id, nome=nome))
        db.commit()
    finally:
        db.close()


def deletar_grupo(grupo_id: str) -> None:
    db = SessionLocal()
    try:
        grupo = db.get(GrupoDB, grupo_id)
        if grupo is None:
            raise ValueError(f"Grupo '{grupo_id}' não encontrado.")
        db.query(GrupoEspecialistaDB).filter_by(grupo_id=grupo_id).delete()
        db.query(UsuarioGrupoDB).filter_by(grupo_id=grupo_id).delete()
        db.delete(grupo)
        db.commit()
    finally:
        db.close()


def definir_especialistas_do_grupo(grupo_id: str, especialista_ids: list[str]) -> None:
    """Substitui por completo a lista de especialistas que esse grupo libera."""
    db = SessionLocal()
    try:
        if db.get(GrupoDB, grupo_id) is None:
            raise ValueError(f"Grupo '{grupo_id}' não encontrado.")

        for especialista_id in especialista_ids:
            if db.get(EspecialistaDB, especialista_id) is None:
                raise ValueError(f"Especialista '{especialista_id}' não encontrado.")

        db.query(GrupoEspecialistaDB).filter_by(grupo_id=grupo_id).delete()
        for especialista_id in especialista_ids:
            db.add(GrupoEspecialistaDB(grupo_id=grupo_id, especialista_id=especialista_id))
        db.commit()
    finally:
        db.close()


def listar_usuarios() -> list[dict]:
    """Cada e-mail que já foi atribuído a algum grupo, com a lista de grupo_id dele."""
    db = SessionLocal()
    try:
        emails = {row.usuario_email for row in db.query(UsuarioGrupoDB.usuario_email).distinct()}
        resultado = []
        for email in sorted(emails):
            grupos = db.query(UsuarioGrupoDB.grupo_id).filter_by(usuario_email=email).all()
            resultado.append({"email": email, "grupos": [g[0] for g in grupos]})
        return resultado
    finally:
        db.close()


def definir_grupos_do_usuario(email: str, grupo_ids: list[str]) -> None:
    """Substitui por completo a lista de grupos aos quais esse e-mail pertence."""
    db = SessionLocal()
    try:
        for grupo_id in grupo_ids:
            if db.get(GrupoDB, grupo_id) is None:
                raise ValueError(f"Grupo '{grupo_id}' não encontrado.")

        db.query(UsuarioGrupoDB).filter_by(usuario_email=email).delete()
        for grupo_id in grupo_ids:
            db.add(UsuarioGrupoDB(usuario_email=email, grupo_id=grupo_id))
        db.commit()
    finally:
        db.close()


# ---------------------------------------------------------------
# Administradores — quem tem acesso ao próprio painel de Super-Admin.
# Eixo separado de Grupo/UsuarioGrupo (ver AdministradorDB em
# db/models_db.py): alguém pode ser admin sem estar em nenhum grupo
# de chat, e vice-versa.
# ---------------------------------------------------------------

def listar_administradores() -> list[str]:
    db = SessionLocal()
    try:
        rows = db.query(AdministradorDB).all()
        return sorted(row.usuario_email for row in rows)
    finally:
        db.close()


def adicionar_administrador(email: str) -> None:
    db = SessionLocal()
    try:
        if db.get(AdministradorDB, email):
            raise ValueError(f"'{email}' já é Super-Admin.")
        db.add(AdministradorDB(usuario_email=email))
        db.commit()
    finally:
        db.close()


def remover_administrador(email: str) -> None:
    db = SessionLocal()
    try:
        row = db.get(AdministradorDB, email)
        if row is None:
            raise ValueError(f"'{email}' não é Super-Admin.")
        db.delete(row)
        db.commit()
    finally:
        db.close()
