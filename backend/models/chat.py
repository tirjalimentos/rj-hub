"""
Modelos de dados do Chat.
Apenas estrutura de dados — nenhuma lógica de negócio aqui.
"""

from typing import Literal

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    especialista_id: str
    # Histórico da conversa, do mais antigo pro mais recente. A última
    # mensagem deve ser sempre do usuário (é a pergunta a responder).
    mensagens: list[ChatMessage]


class DocumentoUsado(BaseModel):
    """
    Versão enxuta de DocumentoConhecimento (models/conhecimento.py) —
    só o suficiente para o painel de contexto do frontend mostrar
    quais documentos embasaram a resposta, sem expor o conteúdo
    completo do documento na resposta do chat.
    """
    id: int
    titulo: str


class ChatResponse(BaseModel):
    resposta: str
    # Documentos que o ia_service.py de fato usou no system prompt
    # desta resposta (pode vir vazio, quando nenhum documento foi
    # considerado relevante o suficiente para a pergunta).
    documentos_usados: list[DocumentoUsado] = []
