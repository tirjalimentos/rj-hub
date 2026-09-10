"""
Ponto de entrada da API do RJ HUB.
Responsável apenas por criar a aplicação e registrar as rotas —
nenhuma regra de negócio deve viver aqui.

Rodar localmente:
    cd backend
    python -m venv venv
    source venv/bin/activate   (Windows: venv\\Scripts\\activate)
    pip install -r requirements.txt
    uvicorn main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from api.routes.auth import router as auth_router
from api.routes.biblioteca import router as biblioteca_router
from api.routes.chat import router as chat_router
from api.routes.conversas import router as conversas_router
from api.routes.dashboard import router as dashboard_router
from api.routes.especialistas import router as especialistas_router
from api.routes.workspaces import router as workspaces_router
from api.routes.admin import router as admin_router
from core.config import APP_NAME, APP_VERSION, CORS_ORIGINS, SESSION_SECRET_KEY

app = FastAPI(title=APP_NAME, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exigida pelo Authlib para guardar o "state"/"nonce" do OAuth durante
# o redirecionamento pro Google e de volta (ver api/routes/auth.py).
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)

app.include_router(especialistas_router)
app.include_router(workspaces_router)
app.include_router(biblioteca_router)
app.include_router(conversas_router)
app.include_router(dashboard_router)
app.include_router(chat_router)
app.include_router(auth_router)
app.include_router(admin_router)


@app.get("/")
def root():
    return {"status": "ok", "app": APP_NAME, "version": APP_VERSION}
