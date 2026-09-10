/* ================================================================
   RJ HUB — especialistas.js
   Renderiza todos os especialistas: busca, filtros, cards e
   controle de favoritos.
   ================================================================ */

// ---------------- View "Todos os Especialistas" ----------------
function renderAllSpecialists(filter){
  const term = (filter || '').toLowerCase();
  const list = SPECIALISTS.filter(s =>
    !term || s.nome.toLowerCase().includes(term) || s.desc.toLowerCase().includes(term)
  );
  document.getElementById('allSpecialistsGrid').innerHTML = list.length
    ? list.map(specCardHTML).join('')
    : `<div class="empty-note" style="grid-column:1/-1;">Nenhum especialista encontrado para "${filter}".</div>`;
}

function initEspecialistasSearch(){
  const specSearch = document.getElementById('specSearch');
  specSearch.addEventListener('input', (e) => renderAllSpecialists(e.target.value));
}

// ---------------- Toggle de favorito (delegado globalmente) ----------------
function initFavoriteToggle(){
  document.addEventListener('click', (e) => {
    const favBtn = e.target.closest('[data-fav]');
    if(favBtn){
      const s = SPECIALISTS.find(x => x.id === favBtn.dataset.fav);
      s.favorito = !s.favorito;
      renderHomeForWorkspace();
      renderAllSpecialists(document.getElementById('specSearch').value);
    }
  });
}
