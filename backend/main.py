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
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from api.routes.auth import router as auth_router
from api.routes.biblioteca import router as biblioteca_router
from api.routes.chat import router as chat_router
from api.routes.conversas import router as conversas_router
from api.routes.dashboard import router as dashboard_router
from api.routes.especialistas import router as especialistas_router
from api.routes.workspaces import router as workspaces_router
from api.routes.admin import router as admin_router
from core.config import APP_NAME, APP_VERSION, CORS_ORIGINS, INITIAL_ADMIN_EMAIL, SESSION_SECRET_KEY
from db.database import Base, SessionLocal, engine
from db.models_db import AdministradorDB

app = FastAPI(title=APP_NAME, version=APP_VERSION)

# Cria as tabelas que ainda não existem no banco, toda vez que o app
# sobe. create_all() só cria o que falta — nunca altera nem apaga
# tabela já existente, então é seguro rodar sempre (inclusive na sua
# máquina local, onde as tabelas já existem: aqui ele não faz nada).
# Isso é essencial na Render: no plano Free o disco é temporário, e o
# banco começa zerado a cada subida do serviço — sem isso, a primeira
# chamada que tocasse qualquer tabela quebrava com "no such table".
# Funciona porque, a essa altura do arquivo, todos os routers acima já
# foram importados — e cada um deles, através dos services, já
# importou db/models_db.py, o que registra todas as tabelas no Base
# antes desta linha rodar.
Base.metadata.create_all(bind=engine)

# Garante que INITIAL_ADMIN_EMAIL (se configurado) sempre existe como
# Super-Admin — resolve o "ovo e galinha" de precisar já ser admin pra
# promover alguém pelo próprio painel. Idempotente (só insere se ainda
# não existir), então é seguro rodar em toda subida do app, inclusive
# quando o e-mail já está la (não faz nada nesse caso).
if INITIAL_ADMIN_EMAIL:
    db = SessionLocal()
    try:
        if db.get(AdministradorDB, INITIAL_ADMIN_EMAIL) is None:
            db.add(AdministradorDB(usuario_email=INITIAL_ADMIN_EMAIL))
            db.commit()
    finally:
        db.close()

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


@app.get("/health")
def health():
    return {"status": "ok", "app": APP_NAME, "version": APP_VERSION}


# Serve o frontend (HTML/CSS/JS) a partir do mesmo serviço da API — um
# único deploy na Render, sem precisar de CORS entre dois domínios
# nem de um segundo serviço só pra arquivo estático (decisão tomada na
# migração pra nuvem, ver CONTEXTO_PROJETO.md). "../frontend" porque o
# Root Directory configurado na Render é "backend" — os dois ficam
# lado a lado na raiz do repositório.
#
# Precisa ser a ÚLTIMA coisa registrada no app: StaticFiles com
# html=True vira um "pega tudo" pra qualquer caminho não reconhecido
# antes dele — se viesse ANTES das rotas de API acima, ele "roubaria"
# essas rotas em vez de deixar a API responder. html=True faz "/"
# servir frontend/index.html automaticamente.
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
