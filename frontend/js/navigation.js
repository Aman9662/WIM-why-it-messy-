/* ================================================
   NAVIGATION.JS — 3-dot menu + routing
   ================================================ */

const NAV_LINKS = [
  { label: 'Platform',  items: [
    { href: '/',          icon: '⌂',  label: 'Home',             desc: 'Overview & features' },
    { href: '/detect',    icon: '⬡',  label: 'Detection Tools',  desc: 'Run a scan now' },
    { href: '/history',   icon: '◷',  label: 'Scan History',     desc: 'View past results' },
  ]},
  { label: 'Resources', items: [
    { href: '/about',     icon: '◉',  label: 'About',            desc: 'Mission & open source' },
    { href: '/api-docs',  icon: '⟨⟩',  label: 'API Docs',        desc: 'Integrate our API' },
  ]},
  { label: 'External', items: [
    { href: 'https://github.com', icon: '⬡', label: 'GitHub', desc: 'View source code', external: true },
  ]}
];

class Navigation {
  constructor() {
    this.isOpen = false;
    this.init();
  }

  init() {
    this.render();
    this.bindEvents();
    this.setActivePage();
    this.handleScroll();
  }

  render() {
    const currentPath = window.location.pathname;

    const navHTML = `
      <nav class="navbar" id="navbar">
        <div class="container">
          <a href="/" class="nav-logo" id="nav-logo">
            <div class="logo-icon">⬡</div>
            <span>Fake<span class="accent">Detector</span></span>
          </a>
          <button class="nav-menu-btn" id="navMenuBtn" aria-label="Toggle navigation" aria-expanded="false">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
          </button>
        </div>
      </nav>

      <div class="nav-overlay" id="navOverlay" role="dialog" aria-modal="true">
        <div class="nav-overlay-backdrop" id="navBackdrop"></div>
        <div class="nav-panel" id="navPanel">
          ${NAV_LINKS.map(group => `
            <div class="nav-panel-label">${group.label}</div>
            ${group.items.map(item => `
              <a href="${item.href}"
                 class="nav-link ${window.location.pathname === item.href ? 'active' : ''}"
                 ${item.external ? 'target="_blank" rel="noopener"' : ''}>
                <div class="nav-icon">${item.icon}</div>
                <div>
                  <div style="font-weight:600;color:var(--text-primary);font-size:var(--text-sm)">${item.label}</div>
                  <div style="font-size:var(--text-xs);color:var(--text-muted);margin-top:2px">${item.desc}</div>
                </div>
              </a>
            `).join('')}
            <div class="nav-divider"></div>
          `).join('')}
        </div>
      </div>

      <div class="toast-container" id="toastContainer"></div>
    `;

    const navContainer = document.getElementById('nav-root');
    if (navContainer) {
      navContainer.innerHTML = navHTML;
    } else {
      // Prepend to body if no root
      const div = document.createElement('div');
      div.innerHTML = navHTML;
      document.body.prepend(div);
    }
  }

  bindEvents() {
    const btn      = document.getElementById('navMenuBtn');
    const overlay  = document.getElementById('navOverlay');
    const backdrop = document.getElementById('navBackdrop');

    if (!btn) return;

    btn.addEventListener('click', () => this.toggle());
    backdrop.addEventListener('click', () => this.close());

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen) this.close();
    });
  }

  toggle() {
    this.isOpen ? this.close() : this.open();
  }

  open() {
    this.isOpen = true;
    document.getElementById('navOverlay').classList.add('open');
    document.getElementById('navMenuBtn').classList.add('active');
    document.getElementById('navMenuBtn').setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  }

  close() {
    this.isOpen = false;
    document.getElementById('navOverlay').classList.remove('open');
    document.getElementById('navMenuBtn').classList.remove('active');
    document.getElementById('navMenuBtn').setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }

  setActivePage() {
    const links = document.querySelectorAll('.nav-link');
    links.forEach(link => {
      if (link.getAttribute('href') === window.location.pathname) {
        link.classList.add('active');
      }
    });
  }

  handleScroll() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;
    window.addEventListener('scroll', () => {
      navbar.classList.toggle('scrolled', window.scrollY > 20);
    }, { passive: true });
  }
}

// ── Toast Notifications ──
function showToast(message, type = 'info', duration = 4000) {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };
  const colors = {
    success: 'var(--success)',
    error:   'var(--danger)',
    warning: 'var(--warning)',
    info:    'var(--info)'
  };

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span style="color:${colors[type]};font-size:1.1rem;flex-shrink:0">${icons[type]}</span>
    <span>${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(8px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ── Reveal on scroll ──
function initReveal() {
  const elements = document.querySelectorAll('.reveal');
  if (!elements.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  elements.forEach(el => observer.observe(el));
}

// ── Initialize on DOM ready ──
document.addEventListener('DOMContentLoaded', () => {
  new Navigation();
  initReveal();
});

window.showToast = showToast;

// ── HTML Escaping (XSS protection) ──
function escapeHtml(str) {
  if (typeof str !== 'string') return str;
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
window.escapeHtml = escapeHtml;
