const componentLinks = document.querySelectorAll('.index a');

function markCurrentComponent() {
  for (const link of componentLinks) {
    if (link.hash === location.hash) {
      link.setAttribute('aria-current', 'location');
    } else {
      link.removeAttribute('aria-current');
    }
  }
}

window.addEventListener('hashchange', markCurrentComponent);
markCurrentComponent();
