/* ================================================================
   RJ HUB — app.js
   Arquivo principal. Responsável apenas por iniciar o sistema:
   registrar a ordem de inicialização dos módulos.
   Nunca deve conter regras de negócio ou renderização direta.
   ================================================================ */

console.log("🚀 RJ HUB iniciado!");

// ----------------------------------------------------------------
// Busca os dados reais na API. Se a API estiver indisponível, mantém
// o fallback local (SPECIALISTS_MOCK, já carregado por padrão em
// data.js) e avisa no console — a interface nunca fica quebrada.
//
// A Biblioteca só é buscada se window.IS_ADMIN for true (decidido
// por verificarAdmin() em admin.js, chamado ANTES desta função) —
// a rota exige Super-Admin agora (unificada com a Base de
// Conhecimento), então pedir pra quem não é admin só gastaria uma
// chamada pra receber 403 à toa.
// ----------------------------------------------------------------
async function carregarDadosIniciais(){
  const conversasRecentes = await buscarConversas(5);
  renderSidebarRecentConversations(conversasRecentes || []);

  const chamadas = [
    buscarEspecialistas(),
    buscarWorkspaces(),
    buscarConversas(),
    buscarConversasFavoritas(),
  ];
  if (window.IS_ADMIN) {
    chamadas.push(buscarCategoriasBiblioteca(), buscarDocumentosRecentes());
  }

  const [
    especialistasApi,
    workspacesApi,
    conversasApi,
    conversasFavoritasApi,
    categoriasApi,
    documentosApi,
  ] = await Promise.all(chamadas);

  if (especialistasApi && especialistasApi.length) {
    SPECIALISTS = especialistasApi;
    console.log(`✅ ${SPECIALISTS.length} especialistas carregados da API.`);
  } else {
    console.warn("⚠️ API indisponível para especialistas — usando SPECIALISTS_MOCK.");
  }

  if (workspacesApi && workspacesApi.length) {
    WORKSPACES = workspacesApi;
    console.log(`✅ ${WORKSPACES.length} workspaces carregados da API.`);
  } else {
    console.warn("⚠️ API indisponível para workspaces — usando WORKSPACES_MOCK.");
  }

  if (window.IS_ADMIN) {
    // Admin: dado real (mesmo se vier vazio — biblioteca_service.py já
    // devolve [] quando não há documento nenhum, isso é válido).
    LIB_CATS = categoriasApi || [];
    LIB_RECENT = documentosApi || [];
  } else {
    // Usuário comum nunca vê a Biblioteca (item da sidebar escondido) —
    // zera em vez de usar o mock, pra nunca mostrar documento fictício
    // caso a view seja alcançada por algum caminho que eu não previ.
    LIB_CATS = [];
    LIB_RECENT = [];
  }

  if (conversasApi && conversasApi.length) {
    CONVERSATIONS = conversasApi;
  } else {
    CONVERSATIONS = []; // dado real agora — lista vazia é um estado válido (usuário sem conversas ainda), não motivo pra mock
  }

  if (conversasFavoritasApi && conversasFavoritasApi.length) {
    CONVERSATIONS_FAVORITAS = conversasFavoritasApi;
  } else {
    console.warn("⚠️ API indisponível para conversas favoritas — usando CONVERSATIONS_FAVORITAS_MOCK.");
  }

  // Garante que currentWorkspace aponte para um objeto da lista em uso agora
  currentWorkspace = WORKSPACES.find(w => w.id === currentWorkspace.id) || WORKSPACES[0];
}

async function init(){
  // Interface geral (sidebar, navegação, breadcrumb, busca da topbar)
  initAuth();
  initUI();

  // Usuário real logado — precisa vir cedo: alimenta a saudação da
  // Home, o rodapé da sidebar, o card de Perfil em Configurações, e
  // as iniciais do avatar no chat (ver aplicarUsuarioNaInterface em
  // workspace.js).
  const usuarioAtual = await buscarUsuarioAtual();
  aplicarUsuarioNaInterface(usuarioAtual);

  // Confirma se o usuário é Super-Admin ANTES de carregar dados —
  // decide se a Biblioteca é buscada (ver carregarDadosIniciais) e já
  // revela os itens "Super-Admin"/"Biblioteca" na sidebar se for o caso.
  await verificarAdmin();

  // Interações que não dependem dos dados ainda carregados
  initEspecialistasSearch();
  initFavoriteToggle();
  initChat();

  // Busca os dados reais antes de renderizar/inicializar qualquer coisa que dependa deles
  await carregarDadosIniciais();

  // Seletor de workspace e configurações: precisam do WORKSPACES já resolvido
  initWorkspaceSelector();
  initConfig();

  // Views que dependem de SPECIALISTS/WORKSPACES já carregados
  renderHomeForWorkspace();
  renderAllSpecialists('');

  // Views com dados próprios, já reais
  renderLibrary();
  renderConversations();
  renderHomeRecentConversation();
  renderDashboard();

  // Monta as 5 abas do painel de Super-Admin (só se window.IS_ADMIN)
  await inicializarPainelAdmin();
}

document.addEventListener('DOMContentLoaded', init);
