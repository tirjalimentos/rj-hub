/* ================================================================
   RJ HUB — config.js
   Configurações: tema, idioma e workspace padrão.
   ================================================================ */

function initThemeOptions(){
  document.querySelectorAll('.theme-opt').forEach(opt => {
    opt.addEventListener('click', () => {
      document.querySelectorAll('.theme-opt').forEach(o => o.classList.remove('selected'));
      opt.classList.add('selected');
    });
  });
}

function populateDefaultWorkspaceSelect(){
  const defaultWsSelect = document.getElementById('defaultWsSelect');
  defaultWsSelect.innerHTML = WORKSPACES.map(w => `<option value="${w.id}">Workspace ${w.nome}</option>`).join('');
}

function initConfig(){
  initThemeOptions();
  populateDefaultWorkspaceSelect();
}
