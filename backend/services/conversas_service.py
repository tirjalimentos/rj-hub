"""
Regras de negócio relacionadas a Conversas.

Dado real agora: cada linha de `conversas` representa um par
(usuário, especialista), atualizado a cada troca de mensagem real no
chat — não mais linhas semeadas manualmente com texto pronto. Ver
ConversaDB em db/models_db.py e registrar_interacao() abaixo (chamada
por api/routes/chat.py a cada resposta bem-sucedida).

icon/nome do especialista não ficam salvos na tabela de conversa —
são buscados em EspecialistaDB na hora de montar a resposta, pra
nunca mostrar um ícone/nome desatualizado se o especialista mudar.
"""

from datetime import datetime, timedelta

from db.database import SessionLocal
from db.models_db import ConversaDB, ConversaFavoritaDB, EspecialistaDB
from models.conversa import Conversa


def _humanizar_quando(dt: datetime) -> str:
    """Converte um datetime real em texto de exibição tipo 'há 18 minutos'."""
    agora = datetime.utcnow()
    delta = agora - dt

    segundos = delta.total_seconds()
    if segundos < 60:
        return "agora"
    minutos = int(segundos // 60)
    if minutos < 60:
        return f"há {minutos} minuto{'s' if minutos != 1 else ''}"
    horas = int(minutos // 60)
    if horas < 24:
        return f"há {horas} hora{'s' if horas != 1 else ''}"
    dias = int(horas // 24)
    if dias == 1:
        return "Ontem"
    if dias < 7:
        return f"há {dias} dias"
    semanas = int(dias // 7)
    return f"há {semanas} semana{'s' if semanas != 1 else ''}"


def _para_schema(row: ConversaDB, especialista: EspecialistaDB | None) -> Conversa:
    return Conversa(
        icon=especialista.icone if especialista else "🤖",
        nome=especialista.nome if especialista else row.especialista_id,
        id=row.especialista_id,
        preview=row.preview,
        quando=_humanizar_quando(row.atualizado_em),
    )


def listar_conversas(usuario_email: str) -> list[Conversa]:
    """
    Sempre filtrado pelo e-mail de quem está pedindo — conversa é
    dado pessoal, ninguém vê o histórico de chat de outra pessoa
    (diferente do Dashboard, que o Super-Admin pode ver agregado).
    """
    db = SessionLocal()
    try:
        rows = (
            db.query(ConversaDB)
            .filter_by(usuario_email=usuario_email)
            .order_by(ConversaDB.atualizado_em.desc())
            .all()
        )
        especialistas = {e.id: e for e in db.query(EspecialistaDB).all()}
        return [_para_schema(row, especialistas.get(row.especialista_id)) for row in rows]
    finally:
        db.close()


def listar_conversas_favoritas() -> list[str]:
    db = SessionLocal()
    try:
        rows = db.query(ConversaFavoritaDB).all()
        return [row.label for row in rows]
    finally:
        db.close()


# ---------------------------------------------------------------
# Escrita — chamada por api/routes/chat.py a cada resposta bem
# sucedida do motor de IA. "Upsert": se já existe uma conversa desse
# usuário com esse especialista, atualiza; senão, cria uma nova.
# ---------------------------------------------------------------
def registrar_interacao(usuario_email: str, especialista_id: str, pergunta: str) -> None:
    db = SessionLocal()
    try:
        row = (
            db.query(ConversaDB)
            .filter_by(usuario_email=usuario_email, especialista_id=especialista_id)
            .first()
        )
        agora = datetime.utcnow()

        if row is None:
            row = ConversaDB(
                usuario_email=usuario_email,
                especialista_id=especialista_id,
                preview=pergunta[:280],
                total_mensagens=1,
                criado_em=agora,
                atualizado_em=agora,
            )
            db.add(row)
        else:
            row.preview = pergunta[:280]
            row.total_mensagens += 1
            row.atualizado_em = agora

        db.commit()
    finally:
        db.close()


# ---------------------------------------------------------------
# Leitura agregada — usada pelo Dashboard (services/dashboard_service.py)
# pra montar o gráfico de uso por especialista e o total de conversas
# recentes, com ou sem filtro por usuário conforme quem está pedindo
# é Super-Admin (vê tudo) ou usuário comum (só o próprio uso).
# ---------------------------------------------------------------
def contar_mensagens_por_especialista(usuario_email: str | None) -> dict[str, int]:
    """
    usuario_email=None -> agrega de TODOS os usuários (visão de
    Super-Admin). Passando um e-mail, agrega só as conversas daquele
    usuário (visão de usuário comum).
    """
    db = SessionLocal()
    try:
        query = db.query(ConversaDB)
        if usuario_email is not None:
            query = query.filter_by(usuario_email=usuario_email)

        resultado: dict[str, int] = {}
        for row in query.all():
            resultado[row.especialista_id] = resultado.get(row.especialista_id, 0) + row.total_mensagens
        return resultado
    finally:
        db.close()


def contar_conversas_na_semana(usuario_email: str | None) -> int:
    db = SessionLocal()
    try:
        limite = datetime.utcnow() - timedelta(days=7)
        query = db.query(ConversaDB).filter(ConversaDB.atualizado_em >= limite)
        if usuario_email is not None:
            query = query.filter_by(usuario_email=usuario_email)
        return query.count()
    finally:
        db.close()
