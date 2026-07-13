/**
 * FitVerse AI — Main JavaScript
 * Shared utilities, IntersectionObserver animations
 */

document.addEventListener('DOMContentLoaded', () => {

  // ── Animate cards on scroll ──────────────────────────────────
  const slideEls = document.querySelectorAll('.animate-slide-up');
  if (slideEls.length) {
    const obs = new IntersectionObserver((entries) => {
      entries.forEach((e, i) => {
        if (e.isIntersecting) {
          e.target.style.animationDelay = `${i * 0.08}s`;
          e.target.style.animationPlayState = 'running';
          obs.unobserve(e.target);
        }
      });
    }, { threshold: 0.1 });
    slideEls.forEach(el => {
      el.style.animationPlayState = 'paused';
      obs.observe(el);
    });
  }

  // ── Active nav link ──────────────────────────────────────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-pill').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPath || (currentPath === '/' && href === '/')) {
      link.classList.add('active');
    } else if (href !== '/' && currentPath.startsWith(href)) {
      link.classList.add('active');
    }
  });

  // ── Smooth back-to-top on logo click ────────────────────────
  document.querySelectorAll('.brand-logo').forEach(el => {
    if (el.tagName === 'A' && el.href.endsWith('/')) {
      el.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
    }
  });

});
