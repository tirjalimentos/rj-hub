/* ================================================================
   RJ HUB — workspace.js
   Responsável pelo Workspace: troca de workspace (agora vive no
   workspace-pill da topbar, visível em todas as views) e pela
   renderização do grid de especialistas da Home.
   ================================================================ */

const wsBtn = document.getElementById('wsBtn');
const wsMenu = document.getElementById('wsMenu');
const wsBtnLabel = document.getElementById('wsBtnLabel');

// ---------------- Identidade real do usuário logado ----------------
// Chamada por app.js assim que GET /auth/me responde. Substitui todo
// o "Pedro Almeida"/"PA" hardcoded que existia em index.html (sidebar,
// Configurações, saudação da Home) pelo nome/e-mail reais de quem
// logou. window.USUARIO_ATUAL fica exposto globalmente pra chat.js
// usar as iniciais certas no avatar das mensagens (ver getUserInitials
// em chat.js).
function aplicarUsuarioNaInterface(usuario){
  if (!usuario) return; // /auth/me falhou (token expirado, API offline) — mantém o que já estava na tela
  window.USUARIO_ATUAL = usuario;

  const primeiroNome = usuario.nome.split(' ')[0];
  const iniciais = usuario.nome.split(' ').filter(Boolean).slice(0, 2).map(p => p[0].toUpperCase()).join('');

  const hora = new Date().getHours();
  const saudacao = hora < 12 ? 'Bom dia' : hora < 18 ? 'Boa tarde' : 'Boa noite';
  const eyebrow = document.getElementById('homeEyebrow');
  if (eyebrow) eyebrow.textContent = `${saudacao}, ${primeiroNome}`;

  // Rodapé da sidebar
  const sbAvatar = document.getElementById('sbFootAvatar');
  const sbNome = document.getElementById('sbFootNome');
  const sbEmail = document.getElementById('sbFootEmail');
  if (sbAvatar) sbAvatar.textContent = iniciais;
  if (sbNome) sbNome.textContent = usuario.nome;
  if (sbEmail) sbEmail.textContent = usuario.email;

  // Card de Perfil em Configurações
  const perfilAvatar = document.getElementById('perfilAvatar');
  const perfilNome = document.getElementById('perfilNome');
  const perfilEmail = document.getElementById('perfilEmail');
  if (perfilAvatar) perfilAvatar.textContent = iniciais;
  if (perfilNome) perfilNome.textContent = usuario.nome;
  if (perfilEmail) perfilEmail.textContent = usuario.email;
}

// ---------------- Menu de seleção de workspace (workspace-pill) ----------------
function renderWsMenu(){
  wsMenu.innerHTML = WORKSPACES.map(w => `
    <button class="ws-option ${w.id === currentWorkspace.id ? 'selected':''}" data-ws="${w.id}">
      <span>${w.icone}</span> Workspace ${w.nome}
    </button>
  `).join('');
}

function initWorkspaceSelector(){
  renderWsMenu();

  wsBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    wsMenu.classList.toggle('open');
  });
  document.addEventListener('click', (e) => {
    if(!e.target.closest('.ws-selector')){
      wsMenu.classList.remove('open');
    }
  });
  wsMenu.addEventListener('click', (e) => {
    const opt = e.target.closest('[data-ws]');
    if(!opt) return;
    currentWorkspace = WORKSPACES.find(w => w.id === opt.dataset.ws);
    wsBtnLabel.textContent = 'Workspace ' + currentWorkspace.nome;
    renderWsMenu();
    wsMenu.classList.remove('open');
    renderHomeForWorkspace();
  });
}

// ---------------- Card de especialista (Home e Especialistas) ----------------
// Estrutura no padrão do protótipo (.card.specialist). O favorito
// continua sendo o botão de estrela (data-fav já usado por
// initFavoriteToggle em especialistas.js — não muda). O campo
// s.status (ok/review) que antes virava uma status-pill separada
// agora mapeia pro texto "● Online"/"● Em revisão" no rodapé do card.
function specCardHTML(s){
  const statusLabel = s.status === 'ok' ? '● Online' : '● Em revisão';
  const statusClass = s.status === 'ok' ? '' : 'status-review';
  return `
    <div class="card specialist" data-id="${s.id}">
      <div>
        <div class="card-top">
          <div class="specialist-icon">${s.icone}</div>
          <button class="star ${s.favorito ? 'on':''}" data-fav="${s.id}" aria-label="Favoritar ${s.nome}">★</button>
        </div>
        <h3>${s.nome}</h3>
        <p>${s.desc}</p>
      </div>
      <div class="card-footer">
        <span class="status ${statusClass}">${statusLabel}</span>
        <button class="open-btn" data-open="${s.id}">Conversar</button>
      </div>
    </div>`;
}

// ---------------- Grid de especialistas do workspace atual (Home) ----------------
function renderWorkspaceGrid(){
  const membros = SPECIALISTS.filter(s => currentWorkspace.membros.includes(s.id));

  const gridTitle = document.getElementById('wsGridTitle');
  if (gridTitle) gridTitle.textContent = 'Especialistas · Workspace ' + currentWorkspace.nome;

  const badge = document.getElementById('homeHeroBadge');
  if (badge) {
    const plural = membros.length === 1 ? 'disponível' : 'disponíveis';
    badge.textContent = `● ${membros.length} especialista${membros.length === 1 ? '' : 's'} ${plural}`;
  }

  document.getElementById('wsSpecialistsGrid').innerHTML = membros.length
    ? membros.map(specCardHTML).join('')
    : `<div class="empty-note" style="grid-column:1/-1;">Nenhum especialista neste workspace ainda.</div>`;
}

// ---------------- Atualização completa da Home ----------------
function renderHomeForWorkspace(){
  renderWorkspaceGrid();
}
