"""
Regras de negócio do sistema de permissões (Grupos/Papéis).

Independente do Workspace: o Workspace é só agrupamento de
navegação; este service é quem decide, de verdade, quais
especialistas um e-mail específico pode ver e conversar.

Regra padrão: NEGAR por padrão. Se o e-mail não pertence a nenhum
grupo, a lista retornada é vazia — mais seguro do que liberar tudo
até alguém lembrar de restringir.
"""

from db.database import SessionLocal
from db.models_db import GrupoEspecialistaDB, UsuarioGrupoDB


def especialistas_visiveis_para(email: str) -> list[str]:
    """
    Retorna a lista de IDs de especialista que esse e-mail pode ver,
    a partir dos grupos aos quais ele pertence. Lista vazia = sem
    acesso a nenhum especialista (e-mail não está em nenhum grupo,
    ou os grupos aos quais pertence não liberam nada ainda).
    """
    db = SessionLocal()
    try:
        grupo_ids = [
            row.grupo_id
            for row in db.query(UsuarioGrupoDB).filter_by(usuario_email=email).all()
        ]
        if not grupo_ids:
            return []

        especialista_ids = (
            db.query(GrupoEspecialistaDB.especialista_id)
            .filter(GrupoEspecialistaDB.grupo_id.in_(grupo_ids))
            .distinct()
            .all()
        )
        return [row[0] for row in especialista_ids]
    finally:
        db.close()


def usuario_tem_acesso(email: str, especialista_id: str) -> bool:
    """
    Atalho pra checar acesso a um único especialista específico —
    útil, por exemplo, na rota /chat, pra barrar quem tentar
    conversar com um especialista que não está entre os visíveis
    pra ele (mesmo que descubra o ID por fora da interface).
    """
    return especialista_id in especialistas_visiveis_para(email)
