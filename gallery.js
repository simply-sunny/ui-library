const tools = document.querySelector('.catalog-tools');
const search = document.querySelector('#component-search');
const filters = [...document.querySelectorAll('.catalog-filters button')];
const status = document.querySelector('.catalog-status');
const entries = [...document.querySelectorAll('.part')].map(card => ({
  card,
  searchText: [...card.querySelectorAll('h2, .part__header code, .part__description')]
    .map(node => node.textContent.toLowerCase()).join(' '),
}));
const links = [...document.querySelectorAll('.index a')];
let active = filters[0];

function updateCatalog() {
  const query = search.value.trim().toLowerCase();
  const group = active.textContent;
  let visible = 0;
  for (const {card, searchText} of entries) {
    card.hidden = !searchText.includes(query) || (group !== 'All' && card.dataset.group !== group);
    if (!card.hidden) visible += 1;
  }
  status.textContent = visible === 0 ? 'No matching components.' : '';
}

function selectFilter(button) {
  active.setAttribute('aria-pressed', 'false');
  active = button;
  active.setAttribute('aria-pressed', 'true');
  updateCatalog();
}

function syncLocation() {
  for (const link of links) {
    if (link.hash === location.hash) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  }
}

document.querySelectorAll('.index a, .featured a').forEach(link => {
  link.addEventListener('click', () => {
    if (!document.getElementById(link.hash.slice(1)).hidden) return;
    search.value = '';
    selectFilter(filters[0]);
  });
});
for (const button of filters) button.addEventListener('click', () => selectFilter(button));
search.addEventListener('input', updateCatalog);
window.addEventListener('hashchange', syncLocation);
syncLocation();
tools.hidden = false;
