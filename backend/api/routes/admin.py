"""
Rotas HTTP do painel de Super-Admin.
Responsável apenas por receber a requisição e delegar aos services —
nenhuma regra de negócio deve viver aqui.

Toda rota aqui exige get_current_admin (login + e-mail na lista de
administradores) — ver api/deps_admin.py.
"""

import io

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from api.deps_admin import get_current_admin
from models.admin import (
    AdministradorCriar,
    AdministradorOut,
    GrupoCriar,
    GrupoEspecialistasAtualizar,
    GrupoOut,
    UsuarioGruposAtualizar,
    UsuarioOut,
)
from models.auth import UsuarioAutenticado
from models.conhecimento import DocumentoConhecimento
from models.especialista import Especialista, EspecialistaCriar
from services import admin_service
from services.conhecimento_service import (
    criar_documento,
    deletar_documento,
    exportar_documentos_zip,
    listar_documentos,
)
from services.especialistas_service import (
    buscar_especialista,
    criar_especialista,
    deletar_especialista,
    listar_especialistas,
)
from services.extracao_texto import ExtracaoTextoError, extrair_texto

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin)],
)


# --- Especialistas (leitura simples, sem filtro de permissão — admin vê tudo) ---

@router.get("/especialistas", response_model=list[Especialista])
def admin_listar_especialistas():
    return listar_especialistas()


@router.post("/especialistas", response_model=Especialista, status_code=201)
def admin_criar_especialista(payload: EspecialistaCriar):
    try:
        return criar_especialista(payload.id, payload.nome, payload.icone, payload.desc)
    except ValueError as erro:
        raise HTTPException(status_code=409, detail=str(erro))


# 404 se o especialista não existe, 409 se existe mas está bloqueado
# por alguma dependência (documentos, grupo, workspace, conversas —
# ver deletar_especialista). A checagem de existência fica aqui na
# rota porque é a única forma de diferenciar "não existe" (404) de
# "existe mas está bloqueado" (409) sem inventar uma hierarquia de
# exceções nova só pra isso — buscar_especialista já existe e é só
# leitura, não é regra de negócio nova.
@router.delete("/especialistas/{especialista_id}", status_code=204)
def admin_deletar_especialista(especialista_id: str):
    if buscar_especialista(especialista_id) is None:
        raise HTTPException(status_code=404, detail=f"Especialista '{especialista_id}' não encontrado.")
    try:
        deletar_especialista(especialista_id)
    except ValueError as erro:
        raise HTTPException(status_code=409, detail=str(erro))


# --- Grupos ---

@router.get("/grupos", response_model=list[GrupoOut])
def admin_listar_grupos():
    return admin_service.listar_grupos()


@router.post("/grupos", response_model=GrupoOut, status_code=201)
def admin_criar_grupo(payload: GrupoCriar):
    try:
        admin_service.criar_grupo(payload.id, payload.nome)
    except ValueError as erro:
        raise HTTPException(status_code=409, detail=str(erro))
    return {"id": payload.id, "nome": payload.nome, "especialistas": []}


@router.delete("/grupos/{grupo_id}", status_code=204)
def admin_deletar_grupo(grupo_id: str):
    try:
        admin_service.deletar_grupo(grupo_id)
    except ValueError as erro:
        raise HTTPException(status_code=404, detail=str(erro))


@router.put("/grupos/{grupo_id}/especialistas", response_model=GrupoOut)
def admin_definir_especialistas_do_grupo(grupo_id: str, payload: GrupoEspecialistasAtualizar):
    try:
        admin_service.definir_especialistas_do_grupo(grupo_id, payload.especialista_ids)
    except ValueError as erro:
        raise HTTPException(status_code=404, detail=str(erro))

    grupo = next((g for g in admin_service.listar_grupos() if g["id"] == grupo_id), None)
    return grupo


# --- Usuários (atribuição a grupos) ---

@router.get("/usuarios", response_model=list[UsuarioOut])
def admin_listar_usuarios():
    return admin_service.listar_usuarios()


@router.put("/usuarios/{email}/grupos", response_model=UsuarioOut)
def admin_definir_grupos_do_usuario(email: str, payload: UsuarioGruposAtualizar):
    try:
        admin_service.definir_grupos_do_usuario(email, payload.grupos)
    except ValueError as erro:
        raise HTTPException(status_code=404, detail=str(erro))
    return {"email": email, "grupos": payload.grupos}


# --- Administradores (quem tem acesso a este próprio painel) ---

@router.get("/administradores", response_model=list[AdministradorOut])
def admin_listar_administradores():
    return [{"email": email} for email in admin_service.listar_administradores()]


@router.post("/administradores", response_model=AdministradorOut, status_code=201)
def admin_adicionar_administrador(payload: AdministradorCriar):
    try:
        admin_service.adicionar_administrador(payload.email)
    except ValueError as erro:
        raise HTTPException(status_code=409, detail=str(erro))
    return {"email": payload.email}


@router.delete("/administradores/{email}", status_code=204)
def admin_remover_administrador(
    email: str, usuario: UsuarioAutenticado = Depends(get_current_admin)
):
    # Sem essa checagem, um Super-Admin sozinho poderia se remover e
    # trancar todo mundo (inclusive ele mesmo) fora do painel — só dá
    # pra remover outro e-mail, nunca o próprio.
    if email == usuario.email:
        raise HTTPException(
            status_code=400,
            detail="Você não pode remover seu próprio acesso de Super-Admin.",
        )
    try:
        admin_service.remover_administrador(email)
    except ValueError as erro:
        raise HTTPException(status_code=404, detail=str(erro))


# --- Documentos da base de conhecimento ---

@router.get("/especialistas/{especialista_id}/documentos", response_model=list[DocumentoConhecimento])
def admin_listar_documentos(especialista_id: str):
    return listar_documentos(especialista_id)


# Backup manual — só leitura, não apaga nada (ver conhecimento_
# service.exportar_documentos_zip). StreamingResponse em vez de
# response_model porque a resposta é binário (.zip), não JSON.
@router.get("/especialistas/{especialista_id}/documentos/exportar")
def admin_exportar_documentos(especialista_id: str):
    if buscar_especialista(especialista_id) is None:
        raise HTTPException(status_code=404, detail=f"Especialista '{especialista_id}' não encontrado.")

    conteudo_zip = exportar_documentos_zip(especialista_id)
    nome_arquivo = f"documentos_{especialista_id}.zip"

    return StreamingResponse(
        io.BytesIO(conteudo_zip),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{nome_arquivo}"'},
    )


@router.post(
    "/especialistas/{especialista_id}/documentos/upload",
    response_model=DocumentoConhecimento,
    status_code=201,
)
async def admin_upload_documento(
    especialista_id: str,
    arquivo: UploadFile = File(...),
    titulo: str | None = None,
):
    conteudo_bytes = await arquivo.read()

    try:
        texto = extrair_texto(arquivo.filename, conteudo_bytes)
    except ExtracaoTextoError as erro:
        raise HTTPException(status_code=422, detail=str(erro))

    titulo_final = titulo or arquivo.filename

    try:
        documento = criar_documento(especialista_id, titulo_final, texto)
    except ValueError as erro:
        raise HTTPException(status_code=404, detail=str(erro))

    return documento


@router.delete("/documentos/{documento_id}", status_code=204)
def admin_deletar_documento(documento_id: int):
    try:
        deletar_documento(documento_id)
    except ValueError as erro:
        raise HTTPException(status_code=404, detail=str(erro))
