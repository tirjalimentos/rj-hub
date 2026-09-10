"""
Regras de negócio da autenticação via Google Workspace (SSO).

Fluxo:
1. Usuário clica em "Entrar com Google" no frontend.
2. Frontend manda o navegador pra GET /auth/login (backend).
3. Backend redireciona pro Google, que autentica o usuário.
4. Google chama de volta GET /auth/callback com um código.
5. Trocamos o código pelos dados do usuário (e-mail, nome, foto).
6. Validamos que o e-mail pertence ao domínio autorizado da empresa.
7. Emitimos um JWT próprio do RJ HUB — o frontend usa esse token daqui
   pra frente em todas as chamadas à API (Authorization: Bearer <token>).

Esse service não sabe nada de HTTP (isso é responsabilidade das rotas
em api/routes/auth.py) — só orquestra o OAuth e o JWT.
"""

from datetime import datetime, timedelta, timezone

import jwt
from authlib.integrations.starlette_client import OAuth

from core.config import (
    GOOGLE_ALLOWED_DOMAIN,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    JWT_EXPIRE_MINUTES,
    JWT_SECRET_KEY,
)
from models.auth import UsuarioAutenticado

_oauth = OAuth()
_oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


def get_google_client():
    """
    Retorna o client OAuth do Google já configurado. Falha com uma
    mensagem clara se as credenciais não foram configuradas, em vez
    de um erro genérico do Authlib.
    """
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise RuntimeError(
            "GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET não configurados. "
            "Ver CONTEXTO_PROJETO.md, seção 6, para como criar as "
            "credenciais no Google Cloud Console."
        )
    return _oauth.google


def validar_dominio(email: str) -> None:
    """Levanta PermissionError se o e-mail não pertencer ao domínio autorizado."""
    if not GOOGLE_ALLOWED_DOMAIN:
        return  # sem restrição configurada — qualquer conta Google passa
    dominio = email.split("@")[-1].lower()
    if dominio != GOOGLE_ALLOWED_DOMAIN.lower():
        raise PermissionError(
            f"Acesso restrito a contas do domínio @{GOOGLE_ALLOWED_DOMAIN}."
        )


def gerar_token(usuario: UsuarioAutenticado) -> str:
    expira_em = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "email": usuario.email,
        "nome": usuario.nome,
        "foto": usuario.foto,
        "exp": expira_em,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")


def decodificar_token(token: str) -> UsuarioAutenticado:
    """Levanta PermissionError se o token for inválido ou tiver expirado."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError as erro:
        raise PermissionError(
            "Sessão inválida ou expirada. Faça login novamente."
        ) from erro

    return UsuarioAutenticado(
        email=payload["email"], nome=payload["nome"], foto=payload.get("foto")
    )
