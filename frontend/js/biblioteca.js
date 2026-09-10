/* ================================================================
   RJ HUB — biblioteca.js
   Renderiza a Biblioteca de Documentos: lista de documentos.

   A grade de categorias (POP, Políticas...) foi removida nesta
   rodada de reskin, seguindo o protótipo aprovado — LIB_CATS/
   LIB_CATS_MOCK continuam existindo em data.js e a API ainda é
   consultada em app.js (buscarCategoriasBiblioteca), só não há
   mais elemento na tela pra exibir isso. Se quiser trazer de volta,
   é só reintroduzir a chamada de renderLibraryCategories() aqui.
   ================================================================ */

function renderLibraryRecent(){
  document.getElementById('libRecent').innerHTML = LIB_RECENT.map(d => `
    <div class="doc">
      <div class="doc-icon">${d.icon}</div>
      <div><h3>${d.nome}</h3><p>${d.area} · ${d.quando}</p></div>
      <span style="margin-left:auto;color:#aaa">⋮</span>
    </div>
  `).join('');
}

function renderLibrary(){
  renderLibraryRecent();
}
