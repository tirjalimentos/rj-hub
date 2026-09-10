"""
Rotas HTTP de autenticação (SSO com Google Workspace).
Só recebe requisição, chama o auth_service, e traduz erros em
respostas HTTP — nenhuma regra de negócio (OAuth, JWT) vive aqui.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from api.deps import get_current_user
from core.config import FRONTEND_URL
from models.auth import UsuarioAutenticado
from services.auth_service import gerar_token, get_google_client, validar_dominio

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login(request: Request):
    google = get_google_client()
    redirect_uri = str(request.url_for("auth_callback"))
    return await google.authorize_redirect(request, redirect_uri)


@router.get("/callback", name="auth_callback")
async def auth_callback(request: Request):
    google = get_google_client()
    try:
        token = await google.authorize_access_token(request)
    except Exception as erro:
        raise HTTPException(
            status_code=401, detail=f"Falha na autenticação com o Google: {erro}"
        )

    info = token.get("userinfo") or {}
    email = info.get("email")
    nome = info.get("name", email)
    foto = info.get("picture")

    if not email:
        raise HTTPException(status_code=401, detail="Google não retornou um e-mail válido.")

    try:
        validar_dominio(email)
    except PermissionError as erro:
        raise HTTPException(status_code=403, detail=str(erro))

    usuario = UsuarioAutenticado(email=email, nome=nome, foto=foto)
    jwt_token = gerar_token(usuario)

    # O token vai no fragmento da URL (#token=...), não na query string:
    # fragmentos não são enviados ao servidor nem ficam em logs de acesso.
    # O frontend lê esse fragmento, guarda o token, e passa a mandá-lo em
    # todas as chamadas seguintes via header Authorization: Bearer <token>.
    return RedirectResponse(f"{FRONTEND_URL}/#token={jwt_token}")


@router.get("/me", response_model=UsuarioAutenticado)
def me(usuario: UsuarioAutenticado = Depends(get_current_user)):
    return usuario
