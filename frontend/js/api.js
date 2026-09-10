/* ================================================================
   RJ HUB — api.js
   Camada de comunicação com o backend FastAPI.
   Centraliza todas as chamadas HTTP reais (especialistas, workspaces,
   biblioteca, conversas, dashboard, chat, autenticação).
   ================================================================ */

const API = "http://127.0.0.1:8000";

// Monta o header Authorization pras rotas que exigem login (ver
// auth.js). Rotas que ainda não exigem login simplesmente ignoram
// esse header quando presente — não tem problema mandar sempre.
function _authHeaders(){
  const token = typeof getToken === "function" ? getToken() : null;
  return token ? { "Authorization": `Bearer ${token}` } : {};
}

async function buscarEspecialistas(){
  try {
    const resposta = await fetch(`${API}/especialistas`, { headers: _authHeaders() });
    const dados = await resposta.json();

    console.log("Especialistas recebidos:");
    console.table(dados);

    return dados;
  } catch (erro) {
    console.error("Erro ao buscar especialistas (API pode estar offline):", erro);
    return null;
  }
}

async function buscarWorkspaces(){
  try {
    const resposta = await fetch(`${API}/workspaces`, { headers: _authHeaders() });
    const dados = await resposta.json();

    console.log("Workspaces recebidos:");
    console.table(dados);

    return dados;
  } catch (erro) {
    console.error("Erro ao buscar workspaces (API pode estar offline):", erro);
    return null;
  }
}

// Exige Super-Admin agora (unificada com a Base de Conhecimento —
// mesma proteção de /biblioteca/recentes, ver biblioteca.py). Usada
// em app.js (carregarDadosIniciais) quando window.IS_ADMIN é true —
// a grade de categorias na tela foi removida no reskin, mas a
// chamada continua alimentando LIB_CATS (ver biblioteca.js).
async function buscarCategoriasBiblioteca(){
  try {
    const resposta = await fetch(`${API}/biblioteca/categorias`, { headers: _authHeaders() });
    if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
    return await resposta.json();
  } catch (erro) {
    console.error("Erro ao buscar categorias da biblioteca (API offline, sem permissão, ou sem login):", erro);
    return null;
  }
}

// Exige Super-Admin agora (unificada com a Base de Conhecimento —
// mostra os documentos de verdade usados pelo chat, não mais uma
// lista de metadados desconectada). Usuário comum nunca chama isso
// (o item "Biblioteca" da sidebar fica escondido pra quem não é
// admin — ver admin.js).
async function buscarDocumentosRecentes(){
  try {
    const resposta = await fetch(`${API}/biblioteca/recentes`, { headers: _authHeaders() });
    if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
    return await resposta.json();
  } catch (erro) {
    console.error("Erro ao buscar documentos recentes (API offline, sem permissão, ou sem login):", erro);
    return null;
  }
}

// `limit`, quando informado, pede só as N conversas mais recentes —
// usado pela sidebar da Parte B. Sem argumento, mantém o
// comportamento antigo (lista completa, usada pela view "Conversas").
// Exige login agora — o backend devolve tudo (Super-Admin) ou só as
// próprias conversas (usuário comum), dependendo de quem está logado.
async function buscarConversas(limit){
  try {
    const url = limit ? `${API}/conversas?limit=${limit}` : `${API}/conversas`;
    const resposta = await fetch(url, { headers: _authHeaders() });
    if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
    return await resposta.json();
  } catch (erro) {
    console.error("Erro ao buscar conversas (API offline ou sem login):", erro);
    return null;
  }
}

async function buscarConversasFavoritas(){
  try {
    const resposta = await fetch(`${API}/conversas/favoritas`, { headers: _authHeaders() });
    if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
    return await resposta.json();
  } catch (erro) {
    console.error("Erro ao buscar conversas favoritas (API pode estar offline):", erro);
    return null;
  }
}

// Exige login agora — escopo por permissão: Super-Admin vê os
// números de todo mundo, usuário comum só os próprios.
async function buscarDashboardStats(){
  try {
    const resposta = await fetch(`${API}/dashboard/stats`, { headers: _authHeaders() });
    if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
    return await resposta.json();
  } catch (erro) {
    console.error("Erro ao buscar indicadores do dashboard (API offline ou sem login):", erro);
    return null;
  }
}

async function buscarDashboardBars(){
  try {
    const resposta = await fetch(`${API}/dashboard/bars`, { headers: _authHeaders() });
    if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);
    return await resposta.json();
  } catch (erro) {
    console.error("Erro ao buscar gráfico do dashboard (API offline ou sem login):", erro);
    return null;
  }
}

// Retorna { email, nome, foto } do usuário logado, ou null se não
// estiver logado ou a sessão tiver expirado (usa auth.js pra saber
// se há token, e o próprio backend valida se ele ainda é válido).
async function buscarUsuarioAtual(){
  if (typeof estaLogado === "function" && !estaLogado()) return null;

  try {
    const resposta = await fetch(`${API}/auth/me`, { headers: _authHeaders() });
    if (!resposta.ok) return null;
    return await resposta.json();
  } catch (erro) {
    console.error("Erro ao buscar usuário logado (API pode estar offline):", erro);
    return null;
  }
}

// Envia a pergunta + histórico da conversa pro motor de IA real e
// retorna o objeto completo { resposta, documentos_usados }. Antes
// devolvia só o texto (dados.resposta) — mudou pra também expor
// documentos_usados, que alimenta o painel de contexto do chat.
// Retorna null se der qualquer erro (API offline, sem login, chave
// não configurada, especialista inválido etc.) — quem chama decide
// o que fazer nesse caso (ver chat.js).
async function enviarMensagemChat(especialistaId, mensagens){
  try {
    const resposta = await fetch(`${API}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ..._authHeaders() },
      body: JSON.stringify({ especialista_id: especialistaId, mensagens }),
    });

    if (!resposta.ok) {
      const erroBody = await resposta.json().catch(() => ({}));
      throw new Error(erroBody.detail || `HTTP ${resposta.status}`);
    }

    return await resposta.json();
  } catch (erro) {
    console.error("Erro ao consultar o motor de IA (API offline, sem login, sem chave configurada, ou erro da Anthropic):", erro);
    return null;
  }
}

/* ================================================================
   Painel de Super-Admin (rotas /admin/*, todas exigem que o usuário
   logado esteja na tabela `administradores` — ver deps_admin.py no
   backend). Todas retornam null (leitura) ou false (escrita) em
   caso de erro, incluindo 403 quando o usuário não é admin — quem
   chama decide o que fazer (admin.js usa isso pra saber se deve
   mostrar o item da sidebar).
   ================================================================ */

// ---------------- Grupos ----------------
async function adminListarGrupos(){
  try {
    const resposta = await fetch(`${API}/admin/grupos`, { headers: _authHeaders() });
    if (!resposta.ok) return null;
    return await resposta.json();
  } catch (erro) {
    console.error("Erro ao buscar grupos (admin) — API offline ou sem permissão:", erro);
    return null;
  }
}

async function adminCriarGrupo(id, nome){
  try {
    const resposta = await fetch(`${API}/admin/grupos`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ..._authHeaders() },
      body: JSON.stringify({ id, nome }),
    });
    if (!resposta.ok) {
      const erroBody = await resposta.json().catch(() => ({}));
      throw new Error(erroBody.detail || `HTTP ${resposta.status}`);
    }
    return await resposta.json();
  } catch (erro) {
    console.error("Erro ao criar grupo:", erro);
    return null;
  }
}

async function adminDeletarGrupo(grupoId){
  try {
    const resposta = await fetch(`${API}/admin/grupos/${grupoId}`, {
      method: 'DELETE',
      headers: _authHeaders(),
    });
    return resposta.ok;
  } catch (erro) {
    console.error("Erro ao excluir grupo:", erro);
    return false;
  }
}

async function adminDefinirEspecialistasDoGrupo(grupoId, especialistaIds){
  try {
    const resposta = await fetch(`${API}/admin/grupos/${grupoId}/especialistas`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ..._authHeaders() },
      body: JSON.stringify({ especialista_ids: especialistaIds }),
    });
    if (!resposta.ok) return null;
    return await resposta.json();
  } catch (erro) {
    console.error("Erro ao atualizar especialistas do grupo:", erro);
    return null;
  }
}

// ---------------- Usuários (atribuição a grupos) ----------------
async function adminListarUsuarios(){
  try {
    const resposta = await fetch(`${API}/admin/usuarios`, { headers: _authHeaders() });
    if (!resposta.ok) return null;
    return await resposta.json();
  } catch (erro) {
    console.error("Erro ao buscar usuários (admin):", erro);
    return null;
  }
}

async function adminDefinirGruposDoUsuario(email, grupoIds){
  try {
    const resposta = await fetch(`${API}/admin/usuarios/${encodeURIComponent(email)}/grupos`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', ..._authHeaders() },
      body: JSON.stringify({ grupos: grupoIds }),
    });
    if (!resposta.ok) return null;
    return await resposta.json();
  } catch (erro) {
    console.error("Erro ao atualizar grupos do usuário:", erro);
    return null;
  }
}

// ---------------- Base de conhecimento (documentos por especialista) ----------------
async function adminListarDocumentos(especialistaId){
  try {
    const resposta = await fetch(`${API}/admin/especialistas/${especialistaId}/documentos`, { headers: _authHeaders() });
    if (!resposta.ok) return null;
    return await resposta.json();
  } catch (erro) {
    console.error("Erro ao buscar documentos (admin):", erro);
    return null;
  }
}

// multipart/form-data — NÃO define Content-Type manualmente (o
// navegador precisa gerar o boundary sozinho; setar à mão quebra o
// upload). titulo vai como query string porque a rota (admin.py) o
// recebe como parâmetro simples, não como campo do form.
async function adminUploadDocumento(especialistaId, arquivo, titulo){
  try {
    const formData = new FormData();
    formData.append('arquivo', arquivo);

    let url = `${API}/admin/especialistas/${especialistaId}/documentos/upload`;
    if (titulo) url += `?titulo=${encodeURIComponent(titulo)}`;

    const resposta = await fetch(url, {
      method: 'POST',
      headers: { ..._authHeaders() },
      body: formData,
    });

    if (!resposta.ok) {
      const erroBody = await resposta.json().catch(() => ({}));
      throw new Error(erroBody.detail || `HTTP ${resposta.status}`);
    }

    return await resposta.json();
  } catch (erro) {
    console.error("Erro ao enviar documento:", erro);
    return null;
  }
}

async function adminDeletarDocumento(documentoId){
  try {
    const resposta = await fetch(`${API}/admin/documentos/${documentoId}`, {
      method: 'DELETE',
      headers: _authHeaders(),
    });
    return resposta.ok;
  } catch (erro) {
    console.error("Erro ao excluir documento:", erro);
    return false;
  }
}

// ---------------- Especialistas (todos, sem filtro de RBAC — só admin) ----------------
async function adminListarEspecialistas(){
  try {
    const resposta = await fetch(`${API}/admin/especialistas`, { headers: _authHeaders() });
    if (!resposta.ok) return null;
    return await resposta.json();
  } catch (erro) {
    console.error("Erro ao buscar especialistas (admin):", erro);
    return null;
  }
}

async function adminCriarEspecialista(id, nome, icone, desc){
  try {
    const resposta = await fetch(`${API}/admin/especialistas`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ..._authHeaders() },
      body: JSON.stringify({ id, nome, icone, desc }),
    });
    if (!resposta.ok) {
      const erroBody = await resposta.json().catch(() => ({}));
      throw new Error(erroBody.detail || `HTTP ${resposta.status}`);
    }
    return await resposta.json();
  } catch (erro) {
    console.error("Erro ao criar especialista:", erro);
    return null;
  }
}

// ---------------- Administradores ----------------
async function adminListarAdministradores(){
  try {
    const resposta = await fetch(`${API}/admin/administradores`, { headers: _authHeaders() });
    if (!resposta.ok) return null;
    return await resposta.json();
  } catch (erro) {
    console.error("Erro ao buscar administradores:", erro);
    return null;
  }
}

async function adminAdicionarAdministrador(email){
  try {
    const resposta = await fetch(`${API}/admin/administradores`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ..._authHeaders() },
      body: JSON.stringify({ email }),
    });
    if (!resposta.ok) {
      const erroBody = await resposta.json().catch(() => ({}));
      throw new Error(erroBody.detail || `HTTP ${resposta.status}`);
    }
    return await resposta.json();
  } catch (erro) {
    console.error("Erro ao promover administrador:", erro);
    return null;
  }
}

async function adminRemoverAdministrador(email){
  try {
    const resposta = await fetch(`${API}/admin/administradores/${encodeURIComponent(email)}`, {
      method: 'DELETE',
      headers: _authHeaders(),
    });
    return resposta.ok;
  } catch (erro) {
    console.error("Erro ao remover administrador:", erro);
    return false;
  }
}

// Retorna `true` se excluído. Se bloqueado (documentos, grupo,
// workspace ou conversas vinculados — ver especialistas_service.
// deletar_especialista no backend) ou se der erro, retorna a
// mensagem (string) explicando o motivo, em vez de só `false` como
// os outros deletes — aqui o motivo do bloqueio importa pro Admin
// saber o que resolver antes de tentar de novo.
async function adminDeletarEspecialista(especialistaId){
  try {
    const resposta = await fetch(`${API}/admin/especialistas/${especialistaId}`, {
      method: 'DELETE',
      headers: _authHeaders(),
    });
    if (resposta.ok) return true;

    const erroBody = await resposta.json().catch(() => ({}));
    return erroBody.detail || `HTTP ${resposta.status}`;
  } catch (erro) {
    console.error("Erro ao excluir especialista (API pode estar offline):", erro);
    return "Não foi possível conectar à API.";
  }
}

// Baixa o .zip com todos os documentos do especialista (um .txt por
// documento) — backup manual, não apaga nada no banco. Resposta é
// binário, não JSON, então monta um link temporário e clica nele
// programaticamente, do jeito que o navegador espera pra iniciar o
// download.
async function adminExportarDocumentos(especialistaId){
  try {
    const resposta = await fetch(`${API}/admin/especialistas/${especialistaId}/documentos/exportar`, {
      headers: _authHeaders(),
    });
    if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`);

    const blob = await resposta.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `documentos_${especialistaId}.zip`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);

    return true;
  } catch (erro) {
    console.error("Erro ao exportar documentos:", erro);
    return false;
  }
}
