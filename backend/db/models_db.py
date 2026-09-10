"""
Modelos de tabela (SQLAlchemy) — representam o banco de dados.
Não confundir com backend/models/*.py, que são os schemas Pydantic
usados na API. São dois mundos separados de propósito:
- models/         -> formato dos dados que trafegam pela API
- db/models_db.py -> formato dos dados que moram no banco

O service é quem converte de um pro outro.
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from db.database import Base


class EspecialistaDB(Base):
    __tablename__ = "especialistas"

    id = Column(String, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    icone = Column(String, nullable=False)
    desc = Column(String, nullable=False)
    docs = Column(Integer, nullable=False, default=0)
    proc = Column(Integer, nullable=False, default=0)
    atualizado = Column(String, nullable=False)
    favorito = Column(Boolean, nullable=False, default=False)
    status = Column(String, nullable=False, default="ok")


class WorkspaceDB(Base):
    __tablename__ = "workspaces"

    id = Column(String, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    icone = Column(String, nullable=False)

    membros = relationship(
        "WorkspaceMembroDB",
        order_by="WorkspaceMembroDB.ordem",
        cascade="all, delete-orphan",
    )


class WorkspaceMembroDB(Base):
    """Tabela de associação: qual especialista pertence a qual workspace, e em que ordem."""

    __tablename__ = "workspace_membros"

    id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False)
    especialista_id = Column(String, ForeignKey("especialistas.id"), nullable=False)
    ordem = Column(Integer, nullable=False, default=0)


class CategoriaDocumentoDB(Base):
    __tablename__ = "categorias_documento"

    id = Column(Integer, primary_key=True, autoincrement=True)
    icon = Column(String, nullable=False)
    nome = Column(String, nullable=False)
    qtd = Column(String, nullable=False)


class DocumentoDB(Base):
    __tablename__ = "documentos_recentes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    icon = Column(String, nullable=False)
    nome = Column(String, nullable=False)
    area = Column(String, nullable=False)
    tag = Column(String, nullable=False)
    quando = Column(String, nullable=False)


class ConversaDB(Base):
    """
    Uma linha por par (usuário, especialista) — não uma por mensagem.
    Toda vez que POST /chat é chamado com sucesso, services/conversas_
    service.registrar_interacao() faz um "upsert": se já existe uma
    conversa desse usuário com esse especialista, atualiza (preview,
    total_mensagens, atualizado_em); senão, cria uma nova.

    icon/nome do especialista NÃO ficam duplicados aqui de propósito
    (evita dado desatualizado se o especialista mudar de nome/ícone
    depois) — o service busca isso em EspecialistaDB na hora de montar
    a resposta da API.
    """

    __tablename__ = "conversas"

    pk = Column(Integer, primary_key=True, autoincrement=True)
    usuario_email = Column(String, nullable=False, index=True)
    especialista_id = Column(String, ForeignKey("especialistas.id"), nullable=False, index=True)
    preview = Column(String, nullable=False)
    total_mensagens = Column(Integer, nullable=False, default=0)
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)
    atualizado_em = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)


class ConversaFavoritaDB(Base):
    __tablename__ = "conversas_favoritas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    label = Column(String, nullable=False)


class DashboardStatDB(Base):
    __tablename__ = "dashboard_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    icon = Column(String, nullable=False)
    bg = Column(String, nullable=False)
    num = Column(String, nullable=False)
    lab = Column(String, nullable=False)


class DashboardBarDB(Base):
    __tablename__ = "dashboard_bars"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String, nullable=False)
    val = Column(Integer, nullable=False)


class DocumentoConhecimentoDB(Base):
    """
    Base de conhecimento real por trás de cada especialista — o
    conteúdo de texto que o motor de IA (ia_service.py) consulta
    antes de responder. Não confundir com DocumentoDB (biblioteca):
    aquele é só metadado de exibição pra view Biblioteca; este guarda
    o texto de verdade, associado a um especialista específico.
    """

    __tablename__ = "documentos_conhecimento"

    id = Column(Integer, primary_key=True, autoincrement=True)
    especialista_id = Column(String, ForeignKey("especialistas.id"), nullable=False, index=True)
    titulo = Column(String, nullable=False)
    # Text em vez de String: sem limite de tamanho prático, pensado
    # pra caber o conteúdo real de um documento (não só um rótulo curto).
    conteudo = Column(Text, nullable=False)
    # Usado pela Biblioteca (unificada com esta tabela) pra mostrar
    # "Atualizado há X dias" com dado real, não texto fixo.
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)


# ---------------------------------------------------------------
# Sistema de permissões (Grupos/Papéis) — validado na variante
# "Especialista Único" e portado para o projeto principal.
#
# Desenho: Grupo é uma camada independente do Workspace. O Workspace
# continua sendo só agrupamento de navegação; o Grupo é quem decide
# quais especialistas uma pessoa pode efetivamente conversar. Uma
# pessoa pode pertencer a mais de um grupo (por isso duas tabelas de
# associação muitos-para-muitos, não uma FK direta em nenhum sentido).
# ---------------------------------------------------------------


class GrupoDB(Base):
    __tablename__ = "grupos"

    id = Column(String, primary_key=True, index=True)
    nome = Column(String, nullable=False)


class GrupoEspecialistaDB(Base):
    """Quais especialistas um grupo libera para quem pertence a ele."""

    __tablename__ = "grupo_especialistas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    grupo_id = Column(String, ForeignKey("grupos.id"), nullable=False, index=True)
    especialista_id = Column(String, ForeignKey("especialistas.id"), nullable=False)


class UsuarioGrupoDB(Base):
    """A quais grupos um usuário (identificado pelo e-mail do login Google) pertence."""

    __tablename__ = "usuario_grupos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_email = Column(String, nullable=False, index=True)
    grupo_id = Column(String, ForeignKey("grupos.id"), nullable=False)


class AdministradorDB(Base):
    """
    Lista de e-mails com acesso de Super-Admin (gerenciar grupos,
    permissões e documentos pelo próprio portal).

    Separado de Grupo/UsuarioGrupo de propósito: ser admin é um eixo
    diferente de "quais especialistas posso conversar" — uma pessoa
    pode ser admin sem estar em nenhum grupo de chat, e vice-versa.
    """

    __tablename__ = "administradores"

    usuario_email = Column(String, primary_key=True, index=True)
