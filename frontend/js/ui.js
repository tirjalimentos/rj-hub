/* ================================================================
   RJ HUB — ui.js
   Responsável por: sidebar, troca de views, menu mobile,
   responsividade e efeitos visuais gerais da interface.
   Não contém dados nem regras de negócio.
   ================================================================ */

const sidebar = document.getElementById('sidebar');
const sbOverlay = document.getElementById('sbOverlay');
const menuToggle = document.getElementById('menuToggle');
const viewTitle = document.getElementById('viewTitle');
const crumbMain = document.getElementById('crumbMain');
const crumbSub = document.getElementById('crumbSub');

const VIEW_LABELS = {
  home:'Início',
  specialists:'Especialistas',
  library:'Biblioteca',
  conversations:'Conversas',
  dashboard:'Dashboard',
  settings:'Configurações',
  chat:'Especialista',
};

function closeSidebarMobile(){
  sidebar.classList.remove('open');
  sbOverlay.classList.remove('open');
}

// Escreve o breadcrumb da topbar em 2 partes ("Início" sempre em
// negrito + o nome da seção atual, se não for a Home). chat.js usa
// isso também (openChat) pra mostrar "Início › Especialista de X".
function setBreadcrumb(subLabel){
  crumbMain.textContent = 'Início';
  if (subLabel) {
    crumbSub.textContent = subLabel;
    viewTitle.classList.add('has-sub');
  } else {
    crumbSub.textContent = '';
    viewTitle.classList.remove('has-sub');
  }
}

// Troca a view ativa. Extraído do listener de clique da sidebar para
// que outros módulos (ex: chat.js, ao abrir a view de chat) também
// possam navegar para uma view sem precisar simular um clique.
// activeBtn é opcional — passa o .sb-item que deve ficar destacado
// (a view de chat, por exemplo, usa o item "Especialistas").
function showView(view, activeBtn){
  document.querySelectorAll('.sb-item').forEach(b => b.classList.remove('active'));
  if (activeBtn) activeBtn.classList.add('active');

  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.getElementById('view-' + view).classList.add('active');

  const label = VIEW_LABELS[view];
  setBreadcrumb(view === 'home' ? null : label);

  closeSidebarMobile();
}

// ---------------- Navegação da sidebar (troca de views) ----------------
function initSidebarNavigation(){
  document.querySelectorAll('.sb-item').forEach(btn => {
    btn.addEventListener('click', () => showView(btn.dataset.view, btn));
  });

  menuToggle.addEventListener('click', () => {
    sidebar.classList.add('open');
    sbOverlay.classList.add('open');
  });
  sbOverlay.addEventListener('click', closeSidebarMobile);
}

// ---------------- Links "Ver todas/os →" da Home ----------------
function initHomeQuickLinks(){
  const seeConversations = document.getElementById('seeAllConversationsLink');
  const seeSpecialists = document.getElementById('seeAllSpecialistsLink');

  if (seeConversations) {
    seeConversations.addEventListener('click', (e) => {
      e.preventDefault();
      const btn = document.querySelector('.sb-item[data-view="conversations"]');
      showView('conversations', btn);
    });
  }
  if (seeSpecialists) {
    seeSpecialists.addEventListener('click', (e) => {
      e.preventDefault();
      const btn = document.querySelector('.sb-item[data-view="specialists"]');
      showView('specialists', btn);
    });
  }
}

// ---------------- Botão "⌕ Busca" da topbar ----------------
// Substitui a antiga busca global da Home (removida no reskin) —
// leva pra Especialistas com o campo de busca em foco. Busca de
// verdade (cross-view, documentos inclusos) fica pra uma próxima
// rodada, quando houver endpoint de busca no backend.
function initTopSearch(){
  const topSearchBtn = document.getElementById('topSearchBtn');
  if (!topSearchBtn) return;

  topSearchBtn.addEventListener('click', () => {
    const btn = document.querySelector('.sb-item[data-view="specialists"]');
    showView('specialists', btn);
    const specSearch = document.getElementById('specSearch');
    if (specSearch) setTimeout(() => specSearch.focus(), 150);
  });
}

// ---------------- Ponto de entrada do módulo (chamado por app.js) ----------------
function initUI(){
  initSidebarNavigation();
  initHomeQuickLinks();
  initTopSearch();
}
