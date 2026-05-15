// ── Sidebar toggle (mobile) ──────────────────────────────────────────
function toggleSidebar() {
  const sidebar  = document.getElementById('sidebar');
  const overlay  = document.getElementById('sidebarOverlay');
  const isOpen   = sidebar.classList.toggle('open');
  overlay.style.display = isOpen ? 'block' : 'none';
}

// ── Auto-dismiss flash messages after 4 s ───────────────────────────
document.addEventListener('DOMContentLoaded', function () {

  setTimeout(function () {
    document.querySelectorAll('.auto-dismiss').forEach(function (el) {
      el.style.transition = 'opacity 0.5s ease';
      el.style.opacity    = '0';
      setTimeout(() => el.remove(), 500);
    });
  }, 4000);

  // ── Active nav-link highlight ──────────────────────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (href && href !== '/' && currentPath.startsWith(href)) {
      link.classList.add('active');
    }
  });

  // ── Algorithm hyperparameter toggling ─────────────────────────────
  const algoSelect = document.getElementById('algorithm_type_select');
  if (algoSelect) {
    toggleHyperparams(algoSelect.value);
    algoSelect.addEventListener('change', function () {
      toggleHyperparams(this.value);
    });
  }

  // ── File upload drag-and-drop ──────────────────────────────────────
  const dropZone  = document.querySelector('.upload-zone');
  const fileInput = document.querySelector('input[type="file"]');

  if (dropZone && fileInput) {
    fileInput.style.display = 'none';

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
      dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('drag-over');
      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        updateUploadLabel(e.dataTransfer.files[0].name);
      }
    });

    fileInput.addEventListener('change', function () {
      if (this.files.length) updateUploadLabel(this.files[0].name);
    });
  }

  function updateUploadLabel(filename) {
    const label = document.querySelector('.upload-label');
    if (label) {
      label.innerHTML = `<i class="fas fa-check-circle" style="color:#34d399;margin-right:8px"></i>${filename}`;
    }
    const zone = document.querySelector('.upload-zone');
    if (zone) zone.style.borderColor = '#4f46e5';
  }
});

// ── Hyperparameter panel toggle ──────────────────────────────────────
function toggleHyperparams(algo) {
  const defaultMsg = document.getElementById('defaultMsg');

  document.querySelectorAll('.hyperparam-group').forEach(g => {
    g.style.display = 'none';
  });

  const active = document.querySelector(`.hyperparam-group[data-algo="${algo}"]`);
  if (active) {
    active.style.display = 'block';
    if (defaultMsg) defaultMsg.style.display = 'none';
  } else {
    if (defaultMsg) defaultMsg.style.display = 'block';
  }
}

// ── Toast notification ───────────────────────────────────────────────
function showToast(msg, type = 'success') {
  const colors = {
    success : { bg: '#4f46e5', icon: 'check-circle' },
    error   : { bg: '#ef4444', icon: 'exclamation-circle' },
    warning : { bg: '#f59e0b', icon: 'exclamation-triangle' },
    info    : { bg: '#0891b2', icon: 'info-circle' },
  };
  const c = colors[type] || colors.success;

  const toast = document.createElement('div');
  toast.style.cssText = `
    position:fixed;bottom:24px;right:24px;
    background:${c.bg};color:#fff;
    padding:12px 20px;border-radius:10px;
    z-index:9999;font-size:13px;font-weight:600;
    box-shadow:0 4px 20px rgba(0,0,0,0.3);
    display:flex;align-items:center;gap:10px;
    animation:slideInRight 0.3s ease;
  `;
  toast.innerHTML = `<i class="fas fa-${c.icon}"></i> ${msg}`;
  document.body.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.4s';
    setTimeout(() => toast.remove(), 400);
  }, 3000);
}

// ── Copy to clipboard ────────────────────────────────────────────────
function copyToClipboard(text) {
  navigator.clipboard.writeText(text)
    .then(() => showToast('Copied to clipboard!'))
    .catch(() => showToast('Copy failed', 'error'));
}

// ── Confirm delete helper ────────────────────────────────────────────
function confirmAction(msg, url) {
  if (confirm(msg)) window.location.href = url;
}