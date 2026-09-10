/* ================================================================
   RJ HUB — admin.js
   Painel de Super-Admin: Grupos, Usuários, Base de Conhecimento,
   Especialistas e Administradores.

   Controle de acesso em 2 tempos:
   1. verificarAdmin() roda BEM CEDO no init() (antes de
      carregarDadosIniciais) — tenta ler /admin/grupos; se vier null
      (403 = não é admin, ou API offline), window.IS_ADMIN fica false
      e os itens "Super-Admin"/"Biblioteca" da sidebar continuam
      escondidos (index.html já começa com display:none neles). Isso
      cedo de propósito: carregarDadosIniciais() só busca a Biblioteca
      se window.IS_ADMIN for true — evita chamada 403 desperdiçada
      pra quem não é admin.
   2. inicializarPainelAdmin() roda depois, só monta as 5 abas se
      window.IS_ADMIN já foi confirmado true no passo 1.
   ================================================================ */

let ADMIN_GRUPOS = [];
let ADMIN_USUARIOS = [];
let ADMIN_ADMINISTRADORES = [];
let ADMIN_ESPECIALISTA_ATUAL = null;

// Lista COMPLETA de especialistas (sem filtro de RBAC — via
// /admin/especialistas), separada de SPECIALISTS (que é filtrada
// pelo grupo do usuário logado, usada em Home/Dashboard/chat). O
// painel de Admin (aba Especialistas, select da Base de
// Conhecimento, checklist de vínculo em Grupos) sempre usa esta
// lista: um especialista recém-criado ainda não pertence a nenhum
// grupo, então SPECIALISTS não o traria — e seria impossível
// vinculá-lo a um grupo pela própria tela de Grupos.
let ADMIN_ESPECIALISTAS_TODOS = [];

const ADMIN_TAB_PANEL_MAP = {
  grupos: 'adminTabGrupos',
  usuarios: 'adminTabUsuarios',
  conhecimento: 'adminTabConhecimento',
  especialistas: 'adminTabEspecialistas',
  administradores: 'adminTabAdministradores',
};

// ---------------- Checklist genérico (grupos <-> especialistas / usuário <-> grupos) ----------------
function buildChecklistHTML(itens, selecionados){
  return `
    <div class="admin-checklist-grid">
      ${itens.map(({ id, label }) => `
        <label class="admin-check-opt">
          <input type="checkbox" value="${id}" ${selecionados.includes(id) ? 'checked' : ''}>
          ${label}
        </label>
      `).join('')}
    </div>
  `;
}

// ---------------- Aba: Grupos ----------------
function renderAdminGrupos(){
  const container = document.getElementById('adminGruposList');
  if (!container) return;

  if (!ADMIN_GRUPOS.length) {
    container.innerHTML = `<div class="empty-note">Nenhum grupo criado ainda.</div>`;
    return;
  }

  container.innerHTML = ADMIN_GRUPOS.map(g => `
    <div class="card admin-item">
      <div class="admin-item-head">
        <div>
          <h3>${g.nome}</h3>
          <p class="admin-item-sub">id: ${g.id} · ${g.especialistas.length} especialista${g.especialistas.length === 1 ? '' : 's'}</p>
        </div>
        <div class="admin-item-actions">
          <button class="filter" data-admin-edit-grupo="${g.id}">Editar especialistas</button>
          <button class="filter admin-danger" data-admin-del-grupo="${g.id}">Excluir</button>
        </div>
      </div>
      <div class="admin-checklist" id="grupoChecklist-${g.id}" style="display:none"></div>
    </div>
  `).join('');
}

async function recarregarGrupos(){
  const grupos = await adminListarGrupos();
  ADMIN_GRUPOS = grupos || [];
  renderAdminGrupos();
}

// ---------------- Aba: Usuários ----------------
function renderAdminUsuarios(){
  const container = document.getElementById('adminUsuariosList');
  if (!container) return;

  if (!ADMIN_USUARIOS.length) {
    container.innerHTML = `<div class="empty-note">Nenhum usuário com grupos atribuídos ainda.</div>`;
    return;
  }

  container.innerHTML = ADMIN_USUARIOS.map(u => `
    <div class="card admin-item">
      <div class="admin-item-head">
        <div>
          <h3>${u.email}</h3>
          <p class="admin-item-sub">${u.grupos.length ? u.grupos.join(', ') : 'sem grupos'}</p>
        </div>
        <div class="admin-item-actions">
          <button class="filter" data-admin-edit-usuario="${u.email}">Editar grupos</button>
          <button class="filter admin-danger" data-admin-remover-usuario="${u.email}">Remover acesso</button>
        </div>
      </div>
      <div class="admin-checklist" id="usuarioChecklist-${u.email}" style="display:none"></div>
    </div>
  `).join('');
}

async function recarregarUsuarios(){
  const usuarios = await adminListarUsuarios();
  ADMIN_USUARIOS = usuarios || [];
  renderAdminUsuarios();
}

// ---------------- Aba: Base de Conhecimento ----------------
function populateAdminEspecialistaSelect(){
  const select = document.getElementById('adminEspecialistaSelect');
  if (!select) return;

  select.innerHTML = ADMIN_ESPECIALISTAS_TODOS.map(s => `<option value="${s.id}">${s.icone} ${s.nome}</option>`).join('');
  select.addEventListener('change', () => carregarDocumentosDoEspecialista(select.value));
}

async function carregarDocumentosDoEspecialista(especialistaId){
  ADMIN_ESPECIALISTA_ATUAL = especialistaId;
  const docs = await adminListarDocumentos(especialistaId);
  renderAdminDocumentos(docs || []);
}

function renderAdminDocumentos(docs){
  const container = document.getElementById('adminDocumentosList');
  if (!container) return;

  if (!docs.length) {
    container.innerHTML = `<div class="card"><div class="doc"><p>Nenhum documento cadastrado pra este especialista ainda.</p></div></div>`;
    return;
  }

  container.innerHTML = `
    <div class="card">
      ${docs.map(d => `
        <div class="doc">
          <div class="doc-icon">DOC</div>
          <div style="flex:1;min-width:0;"><h3>${d.titulo}</h3><p>${d.conteudo.length.toLocaleString('pt-BR')} caracteres</p></div>
          <button class="filter admin-danger" data-admin-del-doc="${d.id}">Excluir</button>
        </div>
      `).join('')}
    </div>
  `;
}

// ---------------- Aba: Especialistas ----------------
function renderAdminEspecialistas(){
  const container = document.getElementById('adminEspecialistasList');
  if (!container) return;

  if (!ADMIN_ESPECIALISTAS_TODOS.length) {
    container.innerHTML = `<div class="empty-note">Nenhum especialista cadastrado ainda.</div>`;
    return;
  }

  container.innerHTML = ADMIN_ESPECIALISTAS_TODOS.map(s => `
    <div class="card admin-item">
      <div class="admin-item-head">
        <div>
          <h3>${s.icone} ${s.nome}</h3>
          <p class="admin-item-sub">id: ${s.id} · ${s.desc}</p>
        </div>
        <div class="admin-item-actions">
          <button class="filter" data-admin-export-docs="${s.id}">Exportar documentos</button>
          <button class="filter admin-danger" data-admin-del-especialista="${s.id}">Excluir</button>
        </div>
      </div>
    </div>
  `).join('');
}

// Especialista criado precisa refletir em dois lugares diferentes,
// cada um lendo sua própria lista:
// - SPECIALISTS (filtrada por RBAC) alimenta Home/busca de
//   especialistas — só muda de verdade quando o especialista novo
//   for vinculado a um grupo (aba Grupos), não imediatamente aqui.
// - ADMIN_ESPECIALISTAS_TODOS (sem filtro, /admin/especialistas)
//   alimenta a aba Especialistas, o select da Base de Conhecimento
//   e o checklist de vínculo em Grupos — precisa mostrar o
//   especialista recém-criado na hora, mesmo sem grupo ainda.
async function recarregarEspecialistasGlobal(){
  const dados = await buscarEspecialistas();
  if (dados && dados.length) SPECIALISTS = dados;

  const todos = await adminListarEspecialistas();
  ADMIN_ESPECIALISTAS_TODOS = todos || [];

  renderAllSpecialists(document.getElementById('specSearch')?.value || '');
  renderHomeForWorkspace();
  populateAdminEspecialistaSelect();
  renderAdminEspecialistas();
}

// ---------------- Aba: Administradores ----------------
function renderAdminAdministradores(){
  const container = document.getElementById('adminAdministradoresList');
  if (!container) return;

  if (!ADMIN_ADMINISTRADORES.length) {
    container.innerHTML = `<div class="empty-note">Nenhum administrador cadastrado.</div>`;
    return;
  }

  const souEu = window.USUARIO_ATUAL ? window.USUARIO_ATUAL.email : null;

  container.innerHTML = ADMIN_ADMINISTRADORES.map(a => `
    <div class="card admin-item">
      <div class="admin-item-head">
        <div>
          <h3>${a.email}${a.email === souEu ? ' <span class="admin-item-sub">(você)</span>' : ''}</h3>
        </div>
        <div class="admin-item-actions">
          ${a.email === souEu
            ? ''
            : `<button class="filter admin-danger" data-admin-remover-admin="${a.email}">Remover</button>`
          }
        </div>
      </div>
    </div>
  `).join('');
}

async function recarregarAdministradores(){
  const administradores = await adminListarAdministradores();
  ADMIN_ADMINISTRADORES = administradores || [];
  renderAdminAdministradores();
}

// ---------------- Eventos (delegados + estáticos) ----------------
function initAdminEvents(){
  // Troca de aba
  document.querySelectorAll('.admin-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.admin-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      document.querySelectorAll('.admin-tab-panel').forEach(p => p.classList.remove('active'));
      document.getElementById(ADMIN_TAB_PANEL_MAP[tab.dataset.adminTab]).classList.add('active');
    });
  });

  // Criar grupo
  document.getElementById('adminCriarGrupoBtn')?.addEventListener('click', async () => {
    const idInput = document.getElementById('adminNovoGrupoId');
    const nomeInput = document.getElementById('adminNovoGrupoNome');
    const id = idInput.value.trim();
    const nome = nomeInput.value.trim();
    if (!id || !nome) { alert('Preencha o id e o nome do grupo.'); return; }

    const resultado = await adminCriarGrupo(id, nome);
    if (resultado === null) { alert('Não foi possível criar o grupo. O id já existe?'); return; }

    idInput.value = ''; nomeInput.value = '';
    await recarregarGrupos();
  });

  // Abrir formulário de novo usuário
  document.getElementById('adminAdicionarUsuarioBtn')?.addEventListener('click', () => {
    const input = document.getElementById('adminNovoUsuarioEmail');
    const email = input.value.trim().toLowerCase();
    if (!email || !email.includes('@')) { alert('Digite um e-mail válido.'); return; }

    const box = document.getElementById('adminNovoUsuarioBox');
    box.style.display = 'block';
    box.innerHTML = `
      <p class="admin-item-sub" style="margin-bottom:10px;">Grupos para <strong>${email}</strong>:</p>
      ${buildChecklistHTML(ADMIN_GRUPOS.map(g => ({ id: g.id, label: g.nome })), [])}
      <button class="open-btn admin-save-btn" data-admin-save-novo-usuario="${email}">Salvar</button>
    `;
  });

  // Upload de documento
  document.getElementById('adminUploadBtn')?.addEventListener('click', async () => {
    const fileInput = document.getElementById('adminUploadFile');
    const tituloInput = document.getElementById('adminUploadTitulo');
    const status = document.getElementById('adminUploadStatus');
    const arquivo = fileInput.files[0];

    if (!arquivo) { alert('Escolha um arquivo .pdf ou .docx.'); return; }
    if (!ADMIN_ESPECIALISTA_ATUAL) { alert('Escolha um especialista primeiro.'); return; }

    status.textContent = 'Enviando e extraindo texto...';
    const resultado = await adminUploadDocumento(ADMIN_ESPECIALISTA_ATUAL, arquivo, tituloInput.value.trim());

    if (resultado === null) {
      status.textContent = 'Falha ao enviar. Verifique se é .pdf ou .docx com texto (não escaneado) e tente de novo.';
      return;
    }

    status.textContent = `"${resultado.titulo}" adicionado com sucesso.`;
    fileInput.value = '';
    tituloInput.value = '';
    carregarDocumentosDoEspecialista(ADMIN_ESPECIALISTA_ATUAL);
  });

  // Criar especialista
  document.getElementById('adminCriarEspecialistaBtn')?.addEventListener('click', async () => {
    const idInput = document.getElementById('adminNovoEspId');
    const iconeInput = document.getElementById('adminNovoEspIcone');
    const nomeInput = document.getElementById('adminNovoEspNome');
    const descInput = document.getElementById('adminNovoEspDesc');

    const id = idInput.value.trim();
    const icone = iconeInput.value.trim();
    const nome = nomeInput.value.trim();
    const desc = descInput.value.trim();

    if (!id || !icone || !nome || !desc) { alert('Preencha id, ícone, nome e descrição.'); return; }

    const resultado = await adminCriarEspecialista(id, nome, icone, desc);
    if (resultado === null) { alert('Não foi possível criar o especialista. O id já existe?'); return; }

    idInput.value = ''; iconeInput.value = ''; nomeInput.value = ''; descInput.value = '';
    await recarregarEspecialistasGlobal();
    alert(`Especialista "${resultado.nome}" criado. Pra ele ficar visível pra alguém, vincule ele a um grupo na aba Grupos.`);
  });

  // Promover administrador
  document.getElementById('adminPromoverBtn')?.addEventListener('click', async () => {
    const input = document.getElementById('adminNovoAdminEmail');
    const email = input.value.trim().toLowerCase();
    if (!email || !email.includes('@')) { alert('Digite um e-mail válido.'); return; }

    const resultado = await adminAdicionarAdministrador(email);
    if (resultado === null) { alert('Não foi possível promover. Esse e-mail já é Super-Admin?'); return; }

    input.value = '';
    await recarregarAdministradores();
  });

  // Delegação: botões dentro de cards renderizados dinamicamente
  document.addEventListener('click', async (e) => {
    // ---- Grupos: expandir/recolher checklist de especialistas ----
    const editGrupoBtn = e.target.closest('[data-admin-edit-grupo]');
    if (editGrupoBtn) {
      const grupoId = editGrupoBtn.dataset.adminEditGrupo;
      const box = document.getElementById(`grupoChecklist-${grupoId}`);
      const grupo = ADMIN_GRUPOS.find(g => g.id === grupoId);
      if (box.style.display === 'none') {
        box.innerHTML = buildChecklistHTML(
          ADMIN_ESPECIALISTAS_TODOS.map(s => ({ id: s.id, label: `${s.icone} ${s.nome}` })),
          grupo.especialistas
        ) + `<button class="open-btn admin-save-btn" data-admin-save-grupo="${grupoId}">Salvar</button>`;
        box.style.display = 'block';
      } else {
        box.style.display = 'none';
      }
      return;
    }

    // ---- Grupos: salvar especialistas selecionados ----
    const salvarGrupoBtn = e.target.closest('[data-admin-save-grupo]');
    if (salvarGrupoBtn) {
      const grupoId = salvarGrupoBtn.dataset.adminSaveGrupo;
      const box = document.getElementById(`grupoChecklist-${grupoId}`);
      const ids = Array.from(box.querySelectorAll('input[type="checkbox"]:checked')).map(i => i.value);

      const resultado = await adminDefinirEspecialistasDoGrupo(grupoId, ids);
      if (resultado === null) { alert('Não foi possível salvar. Tente novamente.'); return; }
      await recarregarGrupos();
      return;
    }

    // ---- Grupos: excluir ----
    const delGrupoBtn = e.target.closest('[data-admin-del-grupo]');
    if (delGrupoBtn) {
      const grupoId = delGrupoBtn.dataset.adminDelGrupo;
      if (!confirm(`Excluir o grupo "${grupoId}"? Isso remove o acesso de todos os usuários vinculados a ele.`)) return;

      const ok = await adminDeletarGrupo(grupoId);
      if (!ok) { alert('Não foi possível excluir o grupo.'); return; }
      await recarregarGrupos();
      return;
    }

    // ---- Usuários: expandir/recolher checklist de grupos ----
    const editUsuarioBtn = e.target.closest('[data-admin-edit-usuario]');
    if (editUsuarioBtn) {
      const email = editUsuarioBtn.dataset.adminEditUsuario;
      const box = document.getElementById(`usuarioChecklist-${email}`);
      const usuario = ADMIN_USUARIOS.find(u => u.email === email);
      if (box.style.display === 'none') {
        box.innerHTML = buildChecklistHTML(
          ADMIN_GRUPOS.map(g => ({ id: g.id, label: g.nome })),
          usuario.grupos
        ) + `<button class="open-btn admin-save-btn" data-admin-save-usuario="${email}">Salvar</button>`;
        box.style.display = 'block';
      } else {
        box.style.display = 'none';
      }
      return;
    }

    // ---- Usuários: salvar grupos selecionados ----
    const salvarUsuarioBtn = e.target.closest('[data-admin-save-usuario]');
    if (salvarUsuarioBtn) {
      const email = salvarUsuarioBtn.dataset.adminSaveUsuario;
      const box = document.getElementById(`usuarioChecklist-${email}`);
      const ids = Array.from(box.querySelectorAll('input[type="checkbox"]:checked')).map(i => i.value);

      const resultado = await adminDefinirGruposDoUsuario(email, ids);
      if (resultado === null) { alert('Não foi possível salvar. Tente novamente.'); return; }
      await recarregarUsuarios();
      return;
    }

    // ---- Usuários: salvar novo usuário (formulário no topo) ----
    const salvarNovoUsuarioBtn = e.target.closest('[data-admin-save-novo-usuario]');
    if (salvarNovoUsuarioBtn) {
      const email = salvarNovoUsuarioBtn.dataset.adminSaveNovoUsuario;
      const box = document.getElementById('adminNovoUsuarioBox');
      const ids = Array.from(box.querySelectorAll('input[type="checkbox"]:checked')).map(i => i.value);
      if (ids.length === 0) { alert('Selecione pelo menos 1 grupo.'); return; }

      const resultado = await adminDefinirGruposDoUsuario(email, ids);
      if (resultado === null) { alert('Não foi possível adicionar o usuário.'); return; }

      box.style.display = 'none';
      document.getElementById('adminNovoUsuarioEmail').value = '';
      await recarregarUsuarios();
      return;
    }

    // ---- Usuários: remover acesso (esvazia os grupos) ----
    const removerUsuarioBtn = e.target.closest('[data-admin-remover-usuario]');
    if (removerUsuarioBtn) {
      const email = removerUsuarioBtn.dataset.adminRemoverUsuario;
      if (!confirm(`Remover o acesso de "${email}"? Ele deixa de pertencer a todos os grupos (não conversa com nenhum especialista até ser adicionado de novo).`)) return;

      const resultado = await adminDefinirGruposDoUsuario(email, []);
      if (resultado === null) { alert('Não foi possível remover o acesso.'); return; }
      await recarregarUsuarios();
      return;
    }

    // ---- Documentos: excluir ----
    const delDocBtn = e.target.closest('[data-admin-del-doc]');
    if (delDocBtn) {
      const docId = delDocBtn.dataset.adminDelDoc;
      if (!confirm('Excluir este documento da base de conhecimento?')) return;

      const ok = await adminDeletarDocumento(docId);
      if (!ok) { alert('Não foi possível excluir o documento.'); return; }
      carregarDocumentosDoEspecialista(ADMIN_ESPECIALISTA_ATUAL);
      return;
    }

    // ---- Administradores: remover ----
    const removerAdminBtn = e.target.closest('[data-admin-remover-admin]');
    if (removerAdminBtn) {
      const email = removerAdminBtn.dataset.adminRemoverAdmin;
      if (!confirm(`Remover o acesso de Super-Admin de "${email}"?`)) return;

      const ok = await adminRemoverAdministrador(email);
      if (!ok) { alert('Não foi possível remover. Alguns erros comuns: você tentou remover a si mesmo, ou o e-mail não é admin.'); return; }
      await recarregarAdministradores();
      return;
    }

    // ---- Especialistas: exportar documentos (backup, não apaga nada) ----
    const exportDocsBtn = e.target.closest('[data-admin-export-docs]');
    if (exportDocsBtn) {
      const especialistaId = exportDocsBtn.dataset.adminExportDocs;
      const textoOriginal = exportDocsBtn.textContent;
      exportDocsBtn.disabled = true;
      exportDocsBtn.textContent = 'Exportando...';

      const ok = await adminExportarDocumentos(especialistaId);
      if (!ok) alert('Não foi possível exportar os documentos.');

      exportDocsBtn.disabled = false;
      exportDocsBtn.textContent = textoOriginal;
      return;
    }

    // ---- Especialistas: excluir ----
    const delEspecialistaBtn = e.target.closest('[data-admin-del-especialista]');
    if (delEspecialistaBtn) {
      const especialistaId = delEspecialistaBtn.dataset.adminDelEspecialista;
      if (!confirm(`Excluir o especialista "${especialistaId}"? Essa ação não pode ser desfeita.`)) return;

      const resultado = await adminDeletarEspecialista(especialistaId);
      if (resultado !== true) {
        alert(resultado || 'Não foi possível excluir o especialista.');
        return;
      }
      await recarregarEspecialistasGlobal();
      return;
    }
  });
}

// ---------------- Passo 1: só descobre se é admin (roda cedo) ----------------
// Sem endpoint dedicado "sou admin?" no backend — reaproveita a
// própria leitura de /admin/grupos pra decidir. window.IS_ADMIN fica
// disponível pra app.js decidir se busca a Biblioteca ou não.
async function verificarAdmin(){
  const grupos = await adminListarGrupos();
  window.IS_ADMIN = grupos !== null;

  if (window.IS_ADMIN) {
    ADMIN_GRUPOS = grupos;
    const adminItem = document.getElementById('sbAdminItem');
    const libItem = document.getElementById('sbLibraryItem');
    if (adminItem) adminItem.style.display = '';
    if (libItem) libItem.style.display = '';
  }

  return window.IS_ADMIN;
}

// ---------------- Passo 2: monta as abas (só se já é admin) ----------------
async function inicializarPainelAdmin(){
  if (!window.IS_ADMIN) return;

  const usuarios = await adminListarUsuarios();
  ADMIN_USUARIOS = usuarios || [];

  const administradores = await adminListarAdministradores();
  ADMIN_ADMINISTRADORES = administradores || [];

  const todosEspecialistas = await adminListarEspecialistas();
  ADMIN_ESPECIALISTAS_TODOS = todosEspecialistas || [];

  renderAdminGrupos();
  renderAdminUsuarios();
  renderAdminAdministradores();
  renderAdminEspecialistas();
  populateAdminEspecialistaSelect();
  if (ADMIN_ESPECIALISTAS_TODOS.length) carregarDocumentosDoEspecialista(ADMIN_ESPECIALISTAS_TODOS[0].id);

  initAdminEvents();
}
