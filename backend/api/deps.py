"""
Dependencies HTTP compartilhadas entre rotas.
Hoje só a de autenticação — qualquer rota que precise exigir login
declara `usuario: UsuarioAutenticado = Depends(get_current_user)`.
"""

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from models.auth import UsuarioAutenticado
from services.auth_service import decodificar_token

_bearer = HTTPBearer()


def get_current_user(
    credenciais: HTTPAuthorizationCredentials = Depends(_bearer),
) -> UsuarioAutenticado:
    try:
        return decodificar_token(credenciais.credentials)
    except PermissionError as erro:
        raise HTTPException(status_code=401, detail=str(erro))
