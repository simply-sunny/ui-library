// Shared UI elements: <ui-wave>, <ui-compare>, <ui-plot> and <ui-copy>. Load with
//   <link rel="stylesheet" href="./assets/ui/ui.css"><script type="module" src="./assets/ui/ui.js"></script>
// Each draws in the page's own colours (base.css's --foreground, --muted and --border), so it fits any theme.
// Documented in components.json: python3 create.py --show <name>. Edit here, in ui-library.

const token = (el, name, fallback) => getComputedStyle(el).getPropertyValue(name).trim() || fallback;
const colours = el => ({
  fg: token(el, '--foreground', '#ccc'),
  muted: token(el, '--muted', '#909090'),
  border: token(el, '--border', '#242424'),
  wash: token(el, '--ui-wash', '#161616'),
  wave: token(el, '--ui-wave', '#5a5a5a'),
});
const time = s => (Number.isFinite(s) ? Math.floor(s / 60) + ':' + String(Math.floor(s % 60)).padStart(2, '0') : '0:00');
/** "8,21.1; 40,48" as [[8, 21.1], [40, 48]]. */
const regions = text => (text || '').split(';').map(r => r.split(',').map(Number)).filter(r => r.length === 2 && r.every(Number.isFinite));

/** A canvas sized to its box in device pixels, redrawn on resize. Returns the 2D context and size. */
function surface(canvas) {
  const dpr = devicePixelRatio || 1, w = Math.round(canvas.clientWidth * dpr), h = Math.round(canvas.clientHeight * dpr);
  if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
  return { g: canvas.getContext('2d'), w, h, dpr };
}

const peaksCache = new Map();
/** The loudest sample in each of 1200 slices of a sound file, and its length in seconds. */
function peaks(src) {
  if (!peaksCache.has(src)) {
    peaksCache.set(src, fetch(src).then(r => r.arrayBuffer()).then(b => new (window.AudioContext || window.webkitAudioContext)().decodeAudioData(b)).then(buf => {
      const n = 1200, data = new Float32Array(n), channels = [...Array(buf.numberOfChannels).keys()].map(c => buf.getChannelData(c));
      const step = Math.max(1, Math.floor(buf.length / n));
      for (let i = 0; i < n; i++) {
        let m = 0;
        for (const ch of channels) for (let j = i * step; j < Math.min(buf.length, (i + 1) * step); j++) m = Math.max(m, Math.abs(ch[j]));
        data[i] = m;
      }
      return { data, seconds: buf.duration };
    }));
  }
  return peaksCache.get(src);
}

/** Draws a waveform, its shaded regions and a playhead at `at` seconds. */
function drawWave(canvas, wave, marked, at) {
  const { g, w, h, dpr } = surface(canvas), c = colours(canvas);
  g.clearRect(0, 0, w, h);
  if (!wave) return;
  const x = s => (s / wave.seconds) * w;
  g.fillStyle = c.wash;
  for (const [a, b] of marked) g.fillRect(Math.round(x(a)), 0, Math.round(x(b) - x(a)), h);
  g.fillStyle = c.wave;
  for (let px = 0; px < w; px++) {
    const v = wave.data[Math.floor((px / w) * wave.data.length)] * (h / 2);
    g.fillRect(px, Math.round(h / 2 - v), 1, Math.max(1, Math.round(2 * v)));
  }
  if (at != null) {
    g.fillStyle = c.fg;
    g.fillRect(Math.round(x(at)), 0, Math.max(1, Math.round(dpr)), h);
  }
}

/** Seeks `audio` to where a pointer is over `canvas`, dragging too. */
function seekable(canvas, audio, seconds, after) {
  const seek = e => {
    const r = canvas.getBoundingClientRect(), s = seconds();
    if (!s) return;
    audio().currentTime = Math.max(0, Math.min(1, (e.clientX - r.left) / r.width)) * s;
    after();
  };
  canvas.addEventListener('pointerdown', e => { seek(e); canvas.setPointerCapture(e.pointerId); });
  canvas.addEventListener('pointermove', e => { if (e.buttons) seek(e); });
}

let current = null;
/** The element Space and the number keys go to: the last one used, else the first on the page. */
addEventListener('keydown', e => {
  if (e.target.closest?.('input,textarea,select,[contenteditable]') || e.metaKey || e.ctrlKey || e.altKey) return;
  const el = current?.isConnected ? current : document.querySelector('ui-compare,ui-wave');
  if (!el?.key) return;
  if (el.key(e.key)) e.preventDefault();
});

/**
 * <ui-wave src="clip.wav" regions="8,21.1"></ui-wave>
 * A sound's waveform with a playhead. Click or drag to seek; the Play button and Space play it.
 */
class UiWave extends HTMLElement {
  connectedCallback() {
    if (this.audio) return;
    this.audio = new Audio(this.getAttribute('src'));
    this.audio.preload = 'metadata';
    this.innerHTML = '<canvas class="ui-canvas" aria-label="Waveform; click to seek"></canvas><div class="ui-bar"><button class="ui-button" type="button">Play</button><span class="meta"></span></div>';
    this.canvas = this.querySelector('canvas');
    this.canvas.style.height = (this.getAttribute('height') || 96) + 'px';
    this.play = this.querySelector('button');
    this.meta = this.querySelector('.meta');
    this.play.addEventListener('click', () => { current = this; this.toggle(); });
    this.audio.addEventListener('ended', () => { this.play.textContent = 'Play'; this.draw(); });
    seekable(this.canvas, () => this.audio, () => this.wave?.seconds, () => { current = this; this.draw(); });
    peaks(this.getAttribute('src')).then(w => { this.wave = w; this.draw(); });
    new ResizeObserver(() => this.draw()).observe(this);
  }
  toggle() {
    if (this.audio.paused) {
      for (const el of document.querySelectorAll('ui-wave,ui-compare')) if (el !== this) el.stop?.();
      this.audio.play();
      this.play.textContent = 'Pause';
      const tick = () => { this.draw(); if (!this.audio.paused) requestAnimationFrame(tick); };
      tick();
    } else this.stop();
  }
  stop() { this.audio.pause(); this.play.textContent = 'Play'; }
  key(k) { if (k === ' ') { this.toggle(); return true; } return false; }
  draw() {
    drawWave(this.canvas, this.wave, regions(this.getAttribute('regions')), this.audio.currentTime);
    this.meta.textContent = time(this.audio.currentTime) + ' / ' + time(this.wave?.seconds);
  }
}

/**
 * <ui-compare>
 *   <audio src="old.wav" data-label="Old" data-regions="8,21.1"></audio>
 *   <audio src="new.wav" data-label="New" data-regions="8,34.3"></audio>
 * </ui-compare>
 * Versions of one sound, played from the same moment: switching while it plays keeps the time.
 * Space plays or pauses; 1 to 9 pick a version. The last version is picked first.
 */
class UiCompare extends HTMLElement {
  connectedCallback() {
    if (this.clips) return;
    this.clips = [...this.querySelectorAll(':scope > audio')];
    this.which = this.clips.length - 1;
    for (const a of this.clips) { a.preload = 'auto'; a.hidden = true; }
    const bar = document.createElement('div');
    bar.className = 'ui-bar';
    bar.innerHTML = '<button class="ui-button" type="button">Play</button><div class="ui-toggle" role="group" aria-label="Version">' +
      this.clips.map((a, i) => '<button type="button" aria-pressed="' + (i === this.which) + '">' + (a.dataset.label || 'Version ' + (i + 1)) + '</button>').join('') + '</div><span class="meta"></span>';
    this.canvas = document.createElement('canvas');
    this.canvas.className = 'ui-canvas';
    this.canvas.setAttribute('aria-label', 'Waveform; click to seek');
    this.canvas.style.height = (this.getAttribute('height') || 96) + 'px';
    this.append(this.canvas, bar);
    this.play = bar.querySelector('.ui-button');
    this.meta = bar.querySelector('.meta');
    this.versions = [...bar.querySelectorAll('.ui-toggle button')];
    this.waves = [];
    this.play.addEventListener('click', () => { current = this; this.toggle(); });
    this.versions.forEach((b, i) => b.addEventListener('click', () => { current = this; this.pick(i); }));
    for (const a of this.clips) a.addEventListener('ended', () => { this.play.textContent = 'Play'; this.draw(); });
    seekable(this.canvas, () => this.clips[this.which], () => this.waves[this.which]?.seconds, () => { current = this; this.draw(); });
    this.clips.forEach((a, i) => peaks(a.getAttribute('src')).then(w => { this.waves[i] = w; this.draw(); }));
    new ResizeObserver(() => this.draw()).observe(this);
  }
  get audio() { return this.clips[this.which]; }
  toggle() {
    if (this.audio.paused) {
      for (const el of document.querySelectorAll('ui-wave,ui-compare')) if (el !== this) el.stop?.();
      this.audio.play();
      this.play.textContent = 'Pause';
      const tick = () => { this.draw(); if (!this.audio.paused) requestAnimationFrame(tick); };
      tick();
    } else this.stop();
  }
  stop() { this.audio.pause(); this.play.textContent = 'Play'; }
  /** Switches to version `i` at the same time, still playing if it was. */
  pick(i) {
    if (i === this.which || !this.clips[i]) return;
    const from = this.audio, playing = !from.paused;
    from.pause();
    this.which = i;
    this.audio.currentTime = Math.min(from.currentTime, (this.waves[i]?.seconds ?? Infinity) - 0.05);
    this.versions.forEach((b, k) => b.setAttribute('aria-pressed', String(k === i)));
    this.dispatchEvent(new CustomEvent('ui-pick', { detail: { index: i, label: this.audio.dataset.label } }));
    if (playing) { this.audio.play(); const tick = () => { this.draw(); if (!this.audio.paused) requestAnimationFrame(tick); }; tick(); } else this.draw();
  }
  key(k) {
    if (k === ' ') { this.toggle(); return true; }
    if (/^[1-9]$/.test(k) && this.clips[+k - 1]) { this.pick(+k - 1); return true; }
    return false;
  }
  draw() {
    drawWave(this.canvas, this.waves[this.which], regions(this.audio.dataset.regions), this.audio.currentTime);
    this.meta.textContent = time(this.audio.currentTime) + ' / ' + time(this.waves[this.which]?.seconds);
  }
}

/**
 * <ui-plot values="22,8,-17,-11" labels="1,2,3,4" kind="bars" band="-25,25" unit="ms"></ui-plot>
 * A small chart of numbers: bars (the default) or a line, from zero, with an optional band of values that
 * are fine. Values in the band draw in the text colour, values past it in the muted colour with a mark.
 */
class UiPlot extends HTMLElement {
  static observedAttributes = ['values', 'labels', 'kind', 'band', 'unit', 'height'];
  connectedCallback() {
    if (!this.canvas) {
      this.canvas = document.createElement('canvas');
      this.canvas.className = 'ui-canvas';
      this.canvas.setAttribute('role', 'img');
      this.append(this.canvas);
      new ResizeObserver(() => this.draw()).observe(this);
    }
    this.draw();
  }
  attributeChangedCallback() { if (this.canvas) this.draw(); }
  draw() {
    const values = (this.getAttribute('values') || '').split(',').map(Number).filter(Number.isFinite);
    const labels = (this.getAttribute('labels') || '').split(',').map(s => s.trim()).filter(Boolean);
    const band = (this.getAttribute('band') || '').split(',').map(Number).filter(Number.isFinite);
    const unit = this.getAttribute('unit') || '', kind = this.getAttribute('kind') || 'bars';
    this.canvas.style.height = (this.getAttribute('height') || 120) + 'px';
    this.canvas.setAttribute('aria-label', this.getAttribute('aria-label') || values.map((v, i) => (labels[i] ?? i + 1) + ': ' + v + unit).join(', '));
    const { g, w, h, dpr } = surface(this.canvas), c = colours(this);
    g.clearRect(0, 0, w, h);
    if (!values.length) return;
    const font = 12 * dpr, axis = 16 * dpr, left = 48 * dpr, top = 8 * dpr, bottom = labels.length ? axis + 8 * dpr : 8 * dpr;
    let lo = Math.min(0, ...values, ...(band.length === 2 ? band : [])), hi = Math.max(0, ...values, ...(band.length === 2 ? band : []));
    if (lo === hi) hi = lo + 1;
    const y = v => top + (1 - (v - lo) / (hi - lo)) * (h - top - bottom), plotW = w - left;
    g.font = font + 'px PlexMono, monospace';
    g.textBaseline = 'middle';
    g.textAlign = 'right';
    g.fillStyle = c.muted;
    for (const v of [hi, 0, lo]) g.fillText(Math.round(v) + unit, left - 8 * dpr, Math.min(h - bottom, Math.max(top + font / 2, y(v))));
    if (band.length === 2) { g.fillStyle = c.wash; g.fillRect(left, y(band[1]), plotW, y(band[0]) - y(band[1])); }
    g.fillStyle = c.border;
    g.fillRect(left, Math.round(y(0)), plotW, Math.max(1, Math.round(dpr)));
    const step = plotW / values.length, inBand = v => band.length !== 2 || (v >= band[0] && v <= band[1]);
    if (kind === 'line') {
      g.strokeStyle = c.fg;
      g.lineWidth = Math.max(1, Math.round(dpr));
      g.beginPath();
      values.forEach((v, i) => { const px = left + step * (i + 0.5); i ? g.lineTo(px, y(v)) : g.moveTo(px, y(v)); });
      g.stroke();
      values.forEach((v, i) => { g.fillStyle = inBand(v) ? c.fg : c.muted; g.fillRect(left + step * (i + 0.5) - 2 * dpr, y(v) - 2 * dpr, 4 * dpr, 4 * dpr); });
    } else {
      const bw = Math.max(1, Math.round(step * 0.5));
      values.forEach((v, i) => {
        g.fillStyle = inBand(v) ? c.fg : c.muted;
        const x0 = Math.round(left + step * (i + 0.5) - bw / 2), y0 = Math.round(Math.min(y(v), y(0)));
        g.fillRect(x0, y0, bw, Math.max(Math.round(dpr), Math.round(Math.abs(y(v) - y(0)))));
      });
    }
    if (labels.length) {
      g.textAlign = 'center';
      g.fillStyle = c.muted;
      labels.forEach((l, i) => g.fillText(l, left + step * (i + 0.5), h - axis / 2));
    }
  }
}

/** <ui-copy><pre><code>…</code></pre></ui-copy>: a Copy button on a code block. */
class UiCopy extends HTMLElement {
  connectedCallback() {
    if (this.querySelector(':scope > .ui-button')) return;
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'ui-button';
    b.textContent = 'Copy';
    b.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(this.querySelector('pre')?.innerText ?? '');
        b.textContent = 'Copied';
      } catch {
        b.textContent = 'Select and copy';
      }
      setTimeout(() => (b.textContent = 'Copy'), 1600);
    });
    this.append(b);
  }
}

for (const [name, cls] of [['ui-wave', UiWave], ['ui-compare', UiCompare], ['ui-plot', UiPlot], ['ui-copy', UiCopy]]) {
  if (!customElements.get(name)) customElements.define(name, cls);
}
