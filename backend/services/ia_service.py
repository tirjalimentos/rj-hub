"""
Motor de IA real por trás de cada especialista.
Usa a API da Anthropic (Claude) para gerar respostas com base no
contexto (nome + área de atuação) do especialista selecionado, e
agora também nos documentos relevantes da base de conhecimento
(conhecimento_service.py) para a pergunta feita.

Antes dessa etapa, o chat era 100% simulado com templates fixos
(REPLIES / QA_REPLIES no frontend). Esse service é o que substitui
essa simulação por uma resposta real.
"""

from fastapi import HTTPException

from anthropic import Anthropic, APIConnectionError, APIStatusError

from core.config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL
from models.conhecimento import DocumentoConhecimento
from services.conhecimento_service import buscar_contexto_relevante
from services.especialistas_service import buscar_especialista

_client: Anthropic | None = None


def _get_client() -> Anthropic:
    """
    Cria o client da Anthropic sob demanda (não na importação do módulo),
    para dar um erro claro só quando o chat for realmente usado — não
    quando o backend simplesmente sobe.
    """
    global _client
    if _client is None:
        if not ANTHROPIC_API_KEY:
            raise RuntimeError(
                "ANTHROPIC_API_KEY não configurada. Defina essa variável de "
                "ambiente antes de usar o chat (ver CONTEXTO_PROJETO.md, seção 6)."
            )
        _client = Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def _montar_bloco_documentos(documentos: list[DocumentoConhecimento]) -> str:
    blocos = []
    for doc in documentos:
        blocos.append(f"### {doc.titulo}\n{doc.conteudo}")
    return "\n\n".join(blocos)


def _montar_system_prompt(especialista, documentos: list[DocumentoConhecimento]) -> str:
    base = (
        f"Você é o Especialista de {especialista.nome} do RJ HUB, a plataforma "
        f"corporativa de Inteligência Artificial da RJ Alimentos. "
        f"Sua área de atuação: {especialista.desc} "
        f"Responda sempre em português do Brasil, de forma direta, profissional "
        f"e objetiva — como um colega experiente dessa área conversando com "
        f"outro funcionário da empresa, nunca como um assistente genérico.\n\n"
        f"Formate a resposta em Markdown sempre que isso ajudar a leitura: use "
        f"### para títulos de seção, listas (- ou 1.) para passos ou itens "
        f"múltiplos, **negrito** para destacar termos e prazos importantes, e "
        f"blocos de código (```) para comandos, códigos ou trechos técnicos. "
        f"Não force estrutura em respostas curtas ou puramente conversacionais "
        f"(uma confirmação simples, uma pergunta de esclarecimento) — reserve "
        f"títulos e listas para quando o conteúdo de fato tiver múltiplos "
        f"passos, itens ou seções distintas, do jeito que um documento bem "
        f"escrito usaria."
    )

    if documentos:
        bloco_documentos = _montar_bloco_documentos(documentos)
        return (
            f"{base}\n\n"
            f"Abaixo estão trechos de documentos internos da RJ Alimentos "
            f"relevantes para a pergunta do usuário. Use-os como fonte "
            f"principal da sua resposta, sempre que forem aplicáveis. Não "
            f"invente informação que não esteja nos documentos nem no seu "
            f"conhecimento geral confiável — se os documentos não cobrirem "
            f"o que foi perguntado, seja honesto sobre essa limitação.\n\n"
            f"--- DOCUMENTOS RELEVANTES ---\n{bloco_documentos}\n--- FIM DOS DOCUMENTOS ---"
        )

    return (
        f"{base} "
        f"Você ainda não tem documentos internos indexados relevantes para "
        f"esta pergunta. Se a resposta exigir um dado específico que você "
        f"não tem como saber (um número exato, um documento específico, um "
        f"processo interno detalhado), seja honesto sobre essa limitação em "
        f"vez de inventar informação."
    )


def _extrair_texto(resposta) -> str:
    """
    Percorre todos os blocos de `resposta.content` e junta só os do tipo
    "text". Necessário porque, quando o modelo usa extended thinking,
    `resposta.content[0]` pode ser um bloco de raciocínio (ThinkingBlock,
    sem atributo `.text`) em vez do texto final — pegar direto
    `resposta.content[0].text` quebra nesse caso.
    """
    partes = [
        bloco.text
        for bloco in resposta.content
        if getattr(bloco, "type", None) == "text"
    ]
    return "\n".join(partes).strip()


def gerar_resposta(
    especialista_id: str, mensagens: list[dict]
) -> tuple[str, list[DocumentoConhecimento]]:
    """
    Gera a resposta do especialista para o histórico de mensagens dado.
    `mensagens` já vem no formato esperado pela API da Anthropic:
    [{"role": "user"|"assistant", "content": "..."}, ...]

    Retorna (texto_da_resposta, documentos_usados) — os documentos são
    devolvidos pra quem chamou (api/routes/chat.py) poder expor no
    ChatResponse.documentos_usados, alimentando o painel de contexto do
    frontend. Antes essa lista era calculada aqui e descartada depois
    de montar o prompt; agora ela sobe até a resposta HTTP.
    """
    especialista = buscar_especialista(especialista_id)
    if especialista is None:
        raise ValueError(f"Especialista '{especialista_id}' não encontrado.")

    client = _get_client()

    # A pergunta mais recente (última mensagem do usuário) é o que
    # orienta a busca de contexto na base de conhecimento.
    ultima_pergunta = mensagens[-1]["content"] if mensagens else ""
    documentos_relevantes = buscar_contexto_relevante(especialista_id, ultima_pergunta)

    system_prompt = _montar_system_prompt(especialista, documentos_relevantes)

    try:
        resposta = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1024,
            system=system_prompt,
            messages=mensagens,
        )
    except APIStatusError as e:
        # Erro 529 = "Anthropic sobrecarregada" (overloaded). Sem esse
        # tratamento específico, virava um 502 genérico no frontend,
        # confundindo com falha de configuração do backend.
        if e.status_code == 529:
            raise HTTPException(
                status_code=503,
                detail=(
                    "O serviço de IA está temporariamente sobrecarregado. "
                    "Tente novamente em alguns instantes."
                ),
            )
        raise HTTPException(
            status_code=503,
            detail=f"Erro ao consultar o serviço de IA (status {e.status_code}).",
        )
    except APIConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Não foi possível conectar ao serviço de IA. Tente novamente em instantes.",
        )

    return _extrair_texto(resposta), documentos_relevantes
