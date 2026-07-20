(function () {
  const STORAGE_KEY = 'theme';

  function getPreferredTheme() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === 'dark' || saved === 'light') return saved;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      ? 'dark'
      : 'light';
  }

  function applyTheme(theme) {
    if (theme === 'dark') {
      document.body.classList.add('dark');
    } else {
      document.body.classList.remove('dark');
    }
    updateToggleIcon(theme);
  }

  function updateToggleIcon(theme) {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;
    const icon = btn.querySelector('[data-feather]');
    if (icon) {
      icon.setAttribute('data-feather', theme === 'dark' ? 'sun' : 'moon');
      if (window.feather && typeof window.feather.replace === 'function') {
        window.feather.replace();
      }
    }
    const sr = btn.querySelector('.visually-hidden');
    if (sr) sr.textContent = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
  }

  function toggleTheme() {
    const curr = document.body.classList.contains('dark') ? 'dark' : 'light';
    const next = curr === 'dark' ? 'light' : 'dark';
    localStorage.setItem(STORAGE_KEY, next);
    applyTheme(next);
  }

  // Initialize on DOM ready
  document.addEventListener('DOMContentLoaded', function () {
    applyTheme(getPreferredTheme());
    const btn = document.getElementById('theme-toggle');
    if (btn) btn.addEventListener('click', toggleTheme);
  });

  // React to system theme changes if user hasn't set one explicitly
  try {
    const mq = window.matchMedia('(prefers-color-scheme: dark)');
    mq.addEventListener('change', function (e) {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved !== 'dark' && saved !== 'light') {
        applyTheme(e.matches ? 'dark' : 'light');
      }
    });
  } catch (_) {}
})();
