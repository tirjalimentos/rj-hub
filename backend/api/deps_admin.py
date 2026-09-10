"""
Dependência de autenticação para rotas de Super-Admin.

Composta em cima de api.deps.get_current_user (que já garante que o
token é válido) — aqui só adicionamos a checagem extra de "esse
e-mail está na lista de administradores?". Fica num arquivo separado
de api/deps.py de propósito, pra não precisar editar aquele arquivo
(que já está em produção/uso) só pra adicionar algo que só as rotas
de admin usam.
"""

from fastapi import Depends, HTTPException

from api.deps import get_current_user
from models.auth import UsuarioAutenticado
from services.admin_service import eh_administrador


def get_current_admin(
    usuario: UsuarioAutenticado = Depends(get_current_user),
) -> UsuarioAutenticado:
    if not eh_administrador(usuario.email):
        raise HTTPException(
            status_code=403,
            detail="Acesso restrito a administradores do RJ HUB.",
        )
    return usuario
