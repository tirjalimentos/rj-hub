"""
Rota HTTP do Chat.
Responsável apenas por receber a requisição, traduzir erros do
service em códigos HTTP apropriados, e devolver a resposta —
nenhuma regra de negócio (prompt, chamada à IA) deve viver aqui.

Exige login (SSO Google) — é a rota mais sensível/custosa do backend
(chama a API paga da Anthropic), por isso foi a primeira a ser
protegida.

Também checa o sistema de permissões por grupo: mesmo que alguém
descubra o ID de um especialista fora da sua lista de acesso (ex:
vendo a rede do navegador de outra pessoa), a rota barra a tentativa
de conversar com ele. Isso é redundante com o filtro que já existe em
GET /especialistas (que nem mostra o card pra quem não tem acesso),
mas essa camada extra aqui é o que garante a restrição de verdade —
a listagem filtrada é só uma questão de UX, não de segurança.
"""

from fastapi import APIRouter, Depends, HTTPException

from api.deps import get_current_user
from models.auth import UsuarioAutenticado
from models.chat import ChatRequest, ChatResponse, DocumentoUsado
from services.conversas_service import registrar_interacao
from services.ia_service import gerar_resposta
from services.permissoes_service import usuario_tem_acesso

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def post_chat(payload: ChatRequest, usuario: UsuarioAutenticado = Depends(get_current_user)):
    if not usuario_tem_acesso(usuario.email, payload.especialista_id):
        raise HTTPException(
            status_code=403,
            detail="Você não tem acesso a este especialista.",
        )

    mensagens = [m.model_dump() for m in payload.mensagens]

    try:
        resposta, documentos_relevantes = gerar_resposta(payload.especialista_id, mensagens)
    except ValueError as erro:
        raise HTTPException(status_code=404, detail=str(erro))
    except RuntimeError as erro:
        raise HTTPException(status_code=503, detail=str(erro))
    except HTTPException:
        # Erros já tratados dentro de ia_service.py (ex: 529 da
        # Anthropic, falha de conexão) já vêm como HTTPException com
        # o status e a mensagem certos — repassa direto, sem embrulhar
        # de novo num 502 genérico.
        raise
    except Exception as erro:
        raise HTTPException(status_code=502, detail=f"Erro ao consultar o motor de IA: {erro}")

    # Grava a conversa de verdade (upsert por usuário+especialista) —
    # ver services/conversas_service.py. Feito depois da IA responder
    # com sucesso: uma pergunta que falhou (erro 503/502 acima) não
    # vira "conversa" nenhuma, pra não distorcer Dashboard/histórico
    # com tentativas que não geraram resposta de verdade.
    ultima_pergunta = payload.mensagens[-1].content if payload.mensagens else ""
    registrar_interacao(usuario.email, payload.especialista_id, ultima_pergunta)

    return ChatResponse(
        resposta=resposta,
        documentos_usados=[
            DocumentoUsado(id=doc.id, titulo=doc.titulo) for doc in documentos_relevantes
        ],
    )
