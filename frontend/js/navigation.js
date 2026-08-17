/* ================================================
   NAVIGATION.JS — Simple 4-Tool Menu
   ================================================ */

class Navigation {
  constructor() {
    this.isOpen = false;
    this.init();
  }

  init() {
    const el = document.getElementById('nav-container');
    if (!el) return;

    el.innerHTML = `
      <nav class="navbar" id="main-navbar">
        <a href="/" class="nav-logo">
          <span class="logo-dot"></span>
          Why It's Messy
        </a>
        <div class="nav-links">
          <a href="/detect" class="nav-link">Detection</a>
          <a href="/pdf-tools" class="nav-link">PDF Tools</a>
          <a href="/size-tools" class="nav-link">Size Fixer</a>
          <a href="/transfer" class="nav-link">Transfer</a>
        </div>
        <button class="nav-menu-btn" onclick="window._nav.toggle()">⋮</button>
      </nav>

      <div class="drawer-overlay" id="dOverlay" onclick="window._nav.close()"></div>
      <div class="drawer" id="dPanel">
        <div class="drawer-header">
          <span style="font-family:var(--font-display);font-size:var(--text-xl);">All Tools</span>
          <button class="drawer-close" onclick="window._nav.close()">✕</button>
        </div>

        <a href="/detect" class="drawer-item" onclick="window._nav.close()">
          <div class="drawer-item-icon detect">🛡️</div>
          <div class="drawer-item-info">
            <div class="drawer-item-label">Fake Detection</div>
            <div class="drawer-item-desc">AI content, plagiarism, fake news & more</div>
          </div>
        </a>

        <a href="/pdf-tools" class="drawer-item" onclick="window._nav.close()">
          <div class="drawer-item-icon pdf">📄</div>
          <div class="drawer-item-info">
            <div class="drawer-item-label">PDF Tools</div>
            <div class="drawer-item-desc">Merge, split, convert, protect & more</div>
          </div>
        </a>

        <a href="/size-tools" class="drawer-item" onclick="window._nav.close()">
          <div class="drawer-item-icon size">📐</div>
          <div class="drawer-item-info">
            <div class="drawer-item-label">Size & Format Fixer</div>
            <div class="drawer-item-desc">Compress, resize, preset templates</div>
          </div>
        </a>

        <a href="/transfer" class="drawer-item" onclick="window._nav.close()">
          <div class="drawer-item-icon transfer">📤</div>
          <div class="drawer-item-info">
            <div class="drawer-item-label">Send Anywhere</div>
            <div class="drawer-item-desc">Share files with a 6-digit code</div>
          </div>
        </a>

        <div style="margin-top:var(--space-xl);padding-top:var(--space-md);border-top:1px solid var(--border);">
          <div class="drawer-section-title">More</div>
          <a href="/history" class="drawer-item" onclick="window._nav.close()">
            <div class="drawer-item-icon" style="background:var(--canvas-alt);">◷</div>
            <div class="drawer-item-info">
              <div class="drawer-item-label">Scan History</div>
              <div class="drawer-item-desc">View past results</div>
            </div>
          </a>
          <a href="/about" class="drawer-item" onclick="window._nav.close()">
            <div class="drawer-item-icon" style="background:var(--canvas-alt);">◉</div>
            <div class="drawer-item-info">
              <div class="drawer-item-label">About</div>
              <div class="drawer-item-desc">Our mission</div>
            </div>
          </a>
          <a href="/api-docs" class="drawer-item" onclick="window._nav.close()">
            <div class="drawer-item-icon" style="background:var(--canvas-alt);">{ }</div>
            <div class="drawer-item-info">
              <div class="drawer-item-label">API Docs</div>
              <div class="drawer-item-desc">Developer API</div>
            </div>
          </a>
        </div>
      </div>
    `;

    this.highlight();
    this.scrollEffect();
    document.addEventListener('keydown', e => { if (e.key === 'Escape') this.close(); });
    document.body.style.paddingTop = '80px';
  }

  toggle() { this.isOpen ? this.close() : this.open(); }

  open() {
    this.isOpen = true;
    document.getElementById('dOverlay').classList.add('open');
    document.getElementById('dPanel').classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  close() {
    this.isOpen = false;
    document.getElementById('dOverlay').classList.remove('open');
    document.getElementById('dPanel').classList.remove('open');
    document.body.style.overflow = '';
  }

  highlight() {
    const p = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(a => {
      if (a.getAttribute('href') === p) a.classList.add('active');
    });
  }

  scrollEffect() {
    const nav = document.getElementById('main-navbar');
    if (nav) window.addEventListener('scroll', () => nav.classList.toggle('scrolled', window.scrollY > 20));
  }
}

document.addEventListener('DOMContentLoaded', () => { window._nav = new Navigation(); });

// ================================================
// GLOBAL TOAST
// ================================================
function showToast(message, type = 'info', duration = 4000) {
  const t = document.getElementById('toast');
  if (!t) return;
  t.textContent = message;
  t.className = 'toast ' + type + ' visible';
  clearTimeout(t._tid);
  t._tid = setTimeout(() => t.classList.remove('visible'), duration);
}

function escapeHtml(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}
