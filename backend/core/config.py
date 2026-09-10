"""
Configurações centrais da aplicação.
Nunca colocar lógica de negócio aqui — apenas parâmetros.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Carrega variáveis do arquivo .env (se existir) para o ambiente do
# processo, ANTES de qualquer os.environ.get() abaixo. Isso substitui
# a necessidade de rodar "set VARIAVEL=valor" manualmente a cada nova
# sessão de terminal — o .env fica salvo na pasta backend/ e é lido
# sozinho toda vez que o backend sobe.
#
# O caminho é montado explicitamente a partir da localização deste
# arquivo (backend/core/config.py -> backend/.env), em vez de deixar
# o python-dotenv "descobrir" sozinho o .env a partir do diretório de
# trabalho atual. A descoberta automática depende de como e de onde o
# processo foi iniciado (uvicorn com --reload usa um subprocesso, por
# exemplo) e pode falhar silenciosamente sem erro nenhum — com o
# caminho explícito, o comportamento é sempre o mesmo, não importa
# de onde o comando foi rodado.
#
# Se uma variável já estiver definida no ambiente (ex: setada via
# "set" na sessão atual, ou em produção via variável de ambiente real
# do servidor), ela tem prioridade sobre o .env — load_dotenv() não
# sobrescreve o que já existir, por padrão.
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

APP_NAME = "RJ HUB API"
APP_VERSION = "0.1.0"

# Origens autorizadas a consumir a API (frontend local por enquanto).
# Em produção, substituir pelo domínio real da RJ Alimentos.
CORS_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:8080",
    "http://localhost:8080",
]

# Motor de IA (Anthropic / Claude) por trás dos especialistas.
# A chave NUNCA fica no código — sempre lida de variável de ambiente
# (agora via .env, ver seção acima). Como configurar, ver
# CONTEXTO_PROJETO.md, seção 6.
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL = "claude-sonnet-5"

# Autenticação via SSO (Google Workspace). Credenciais criadas no
# Google Cloud Console — ver CONTEXTO_PROJETO.md, seção 6, pro passo
# a passo. Também nunca ficam no código.
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

# Restringe o login a um domínio específico (ex: "rjalimentos.com.br").
# Deixe em branco/não configurada para aceitar qualquer conta Google
# durante os primeiros testes do piloto.
GOOGLE_ALLOWED_DOMAIN = os.environ.get("GOOGLE_ALLOWED_DOMAIN")

# Chave usada pra assinar o JWT próprio do RJ HUB (emitido depois do
# login com Google). TROQUE o valor padrão via variável de ambiente
# antes de expor a API fora da sua máquina.
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "troque-esta-chave-em-producao")
JWT_EXPIRE_MINUTES = 60 * 8  # sessão dura 8 horas

# Chave usada pela SessionMiddleware do Starlette, exigida pelo Authlib
# pra guardar o "state"/"nonce" do OAuth durante o redirecionamento.
# Também deve ser trocada via variável de ambiente em produção.
SESSION_SECRET_KEY = os.environ.get("SESSION_SECRET_KEY", "troque-esta-chave-em-producao")

# URL do frontend, para onde o backend redireciona depois do login
# com Google (com o token no fragmento da URL).
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://127.0.0.1:8080")
