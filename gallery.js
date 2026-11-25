const main = document.querySelector('#components');
const parts = new Map([...main.querySelectorAll('.part')].map(part => [part.id, part]));
const links = [...document.querySelectorAll('.index a')];
const search = document.querySelector('#component-search');
const status = document.querySelector('.index-status');
let selected;

function selectPart(id, scroll = false) {
  const next = parts.get(id);
  if (!next) return;
  if (selected && selected !== next) {
    selected.querySelectorAll('audio').forEach(audio => audio.pause());
  }
  selected = next;
  for (const part of parts.values()) part.hidden = part !== selected;
  for (const link of links) {
    if (link.hash === '#' + id) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  }
  if (scroll) {
    if (matchMedia('(max-width: 680px)').matches) main.scrollIntoView();
    else window.scrollTo(0, 0);
  }
}

function followHash() {
  const id = location.hash.slice(1);
  if (!id || parts.has(id)) selectPart(id || 'tabs', Boolean(id));
}

main.closest('.gallery').addEventListener('click', event => {
  const link = event.target.closest('a[href^="#"]');
  const id = link?.hash.slice(1);
  if (!parts.has(id) || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  event.preventDefault();
  if (location.hash !== link.hash) history.pushState(null, '', link.hash);
  selectPart(id, true);
});
search.addEventListener('input', () => {
  const query = search.value.toLowerCase().trim();
  for (const link of links) link.hidden = !link.dataset.search.toLowerCase().includes(query);
  for (const group of document.querySelectorAll('.index__group')) {
    group.hidden = !group.querySelector('a:not([hidden])');
  }
  status.textContent = links.every(link => link.hidden) ? 'No matching components.' : '';
});
search.addEventListener('keydown', event => {
  if (event.key === 'Enter') links.find(link => !link.hidden)?.click();
});
window.addEventListener('popstate', followHash);
window.addEventListener('hashchange', followHash);
document.documentElement.dataset.enhanced = '';
document.querySelector('.index-search').hidden = false;
selectPart('tabs');
followHash();
