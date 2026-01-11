(function () {
  'use strict';

  function qs(sel, root) { return (root || document).querySelector(sel); }
  function qsa(sel, root) { return Array.from((root || document).querySelectorAll(sel)); }

  const modal = qs('#chartModal');
  if (!modal) return;

  const modalImg = qs('#chartModalImg', modal);
  const closeBtn = qs('#chartModalClose', modal);

  function openModal(imgEl) {
    if (!imgEl || !imgEl.src) return;
    modalImg.src = imgEl.src;
    modalImg.alt = imgEl.alt || 'Wykres';
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
    closeBtn.focus();
  }

  function closeModal() {
    modal.classList.remove('show');
    modalImg.src = '';
    document.body.style.overflow = '';
  }

  // Kliknięcie w obraz wykresu → fullscreen.
  qsa('.chart-frame img').forEach((img) => {
    img.addEventListener('click', () => openModal(img));
    img.setAttribute('tabindex', '0');
    img.setAttribute('role', 'button');
    img.setAttribute('aria-label', 'Powiększ wykres');
    img.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        openModal(img);
      }
    });
  });

  closeBtn.addEventListener('click', closeModal);

  // Kliknięcie w tło modala zamyka.
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  // ESC zamyka.
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('show')) {
      closeModal();
    }
  });
})();
