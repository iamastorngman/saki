(() => {
  const key = "saki-watchlist";
  const getList = () => { try { return JSON.parse(localStorage.getItem(key) || "[]"); } catch { return []; } };
  const saveList = list => localStorage.setItem(key, JSON.stringify(list));
  function updateButtons() {
    document.querySelectorAll("[data-watchlist]").forEach(btn => {
      const id = Number(btn.dataset.watchlist);
      const active = getList().some(x => x.id === id);
      btn.textContent = active ? "✓ In watchlist" : "＋ Add to watchlist";
      btn.classList.toggle("is-saved", active);
    });
  }
  document.addEventListener("click", event => {
    const btn = event.target.closest("[data-watchlist]");
    if (!btn) return;
    const id = Number(btn.dataset.watchlist), list = getList();
    const index = list.findIndex(x => x.id === id);
    if (index >= 0) list.splice(index, 1);
    else list.push({id, title: btn.dataset.title, poster: btn.dataset.poster});
    saveList(list); updateButtons();
  });
  const section = document.getElementById("continue-section");
  const grid = document.getElementById("continue-grid");
  if (section && grid) {
    let progress = {};
    try { progress = JSON.parse(localStorage.getItem("saki-progress") || "{}"); } catch {}
    const entries = Object.values(progress).filter(x => x.percent > 2 && x.percent < 96).slice(-8).reverse();
    if (entries.length) {
      section.classList.remove("hidden");
      grid.innerHTML = entries.map(x => '<a class="anime-card" href="' + x.url + '">' +
        (x.poster ? '<img loading="lazy" src="' + x.poster + '" alt="">' : '<div class="poster-placeholder">SAKI</div>') +
        '<div class="card-info"><strong>' + escapeHtml(x.title) + '</strong><small>' + Math.round(x.percent) + '% watched</small></div></a>').join("");
    }
  }
  function escapeHtml(s) { return String(s || "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }
  updateButtons();
})();