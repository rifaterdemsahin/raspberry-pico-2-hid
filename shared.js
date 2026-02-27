// Shared navigation, search, and debug mode logic
// Used by all stage pages via <script src="../shared.js"></script>

(async function () {
  // Resolve correct base path (one level up from stage pages)
  const isRoot = !location.pathname.match(/\/\d_/);
  const base = isRoot ? '' : '../';

  let ALL_ITEMS = [];

  async function loadMenus() {
    try {
      const res = await fetch(base + 'menus.json');
      const data = await res.json();
      buildDebugBar(data.debug_menu, base);
      buildContentNav(data.content_menu, base);
      ALL_ITEMS = [...data.debug_menu, ...data.content_menu];
      initSearch(base);
    } catch (e) {
      console.warn('Could not load menus.json', e);
    }
  }

  function buildDebugBar(items, base) {
    const bar = document.getElementById('debug-bar');
    if (!bar) return;
    const label = document.createElement('span');
    label.className = 'debug-label';
    label.textContent = '🐛 Debug';
    bar.appendChild(label);
    items.forEach(item => {
      const a = document.createElement('a');
      a.href = base + item.url;
      a.textContent = item.icon + ' ' + item.label;
      bar.appendChild(a);
    });
    const md = document.createElement('a');
    md.href = base + 'markdown_renderer.html';
    md.textContent = '📝 MD Renderer';
    bar.appendChild(md);
  }

  function buildContentNav(items, base) {
    const nav = document.getElementById('content-nav');
    if (!nav) return;
    items.forEach(item => {
      const a = document.createElement('a');
      a.href = item.url.endsWith('.md')
        ? base + 'markdown_renderer.html?file=' + encodeURIComponent(item.url)
        : base + item.url;
      a.textContent = item.icon + ' ' + item.label;
      nav.appendChild(a);
    });
  }

  function initSearch(base) {
    const input = document.getElementById('search-input');
    const dropdown = document.getElementById('search-dropdown');
    if (!input || !dropdown) return;
    let activeIdx = -1;

    input.addEventListener('input', () => {
      const q = input.value.trim().toLowerCase();
      dropdown.innerHTML = '';
      activeIdx = -1;
      if (!q) { dropdown.classList.remove('open'); return; }
      const matches = ALL_ITEMS.filter(i => i.label.toLowerCase().includes(q)).slice(0, 8);
      if (!matches.length) { dropdown.classList.remove('open'); return; }
      matches.forEach(item => {
        const a = document.createElement('a');
        a.href = item.url.endsWith('.md')
          ? base + 'markdown_renderer.html?file=' + encodeURIComponent(item.url)
          : base + item.url;
        a.innerHTML = `<span>${item.icon || '📄'}</span>${item.label}`;
        dropdown.appendChild(a);
      });
      dropdown.classList.add('open');
    });

    input.addEventListener('keydown', e => {
      const links = dropdown.querySelectorAll('a');
      if (e.key === 'ArrowDown') activeIdx = Math.min(activeIdx + 1, links.length - 1);
      else if (e.key === 'ArrowUp') activeIdx = Math.max(activeIdx - 1, 0);
      else if (e.key === 'Enter' && activeIdx >= 0) { links[activeIdx].click(); return; }
      else if (e.key === 'Escape') { dropdown.classList.remove('open'); return; }
      links.forEach((l, i) => l.classList.toggle('active', i === activeIdx));
    });

    document.addEventListener('click', e => {
      if (!e.target.closest('.search-wrap')) dropdown.classList.remove('open');
    });
  }

  function initDebug() {
    const btn = document.getElementById('debug-toggle');
    const bar = document.getElementById('debug-bar');
    if (!btn || !bar) return;
    const isDebug = document.cookie.split(';').some(c => c.trim() === 'debug=true')
      || new URLSearchParams(location.search).get('debug') === 'true';
    if (isDebug) {
      bar.classList.add('visible');
      document.cookie = 'debug=true; path=/; max-age=86400';
    }
    btn.addEventListener('click', () => {
      const active = bar.classList.toggle('visible');
      document.cookie = `debug=${active}; path=/; max-age=86400`;
    });
  }

  initDebug();
  await loadMenus();
})();
