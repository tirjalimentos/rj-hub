"""
Conexão com o banco de dados (SQLite).
Só configuração de conexão aqui — nenhuma regra de negócio,
nenhum modelo de tabela.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Caminho do arquivo SQLite. Em produção isso pode virar uma variável
# de ambiente lendo uma URL de Postgres, sem precisar mudar mais nada
# além desta linha.
DATABASE_URL = "sqlite:///./rjhub.db"

# check_same_thread=False é necessário só para SQLite + FastAPI
# (várias requisições podem usar threads diferentes).
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency do FastAPI: abre uma sessão por requisição e garante
    que ela é fechada no final, mesmo se der erro.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
