#!/usr/bin/env python3
"""Add the shared UI components to any site, or list them, show one, or build their gallery

    python3 create.py --dest ../my-site/public/assets/ui     copy ui.css and ui.js there
    python3 create.py --list                                 every component, one line each
    python3 create.py --show compare                         one component: use, avoid, attributes, markup
    python3 create.py --gallery /tmp/ui-gallery              a page showing every component, to check by eye
    python3 create.py --docs                                 docs/COMPONENTS.md, written from components.json

components.json (ui/) is the one source: the docs, the gallery and --show all come from it.
"""
import argparse
import filecmp
import html
import json
import math
import shutil
import struct
import sys
import wave
from pathlib import Path

SHARED = Path(__file__).resolve().parent
UI = SHARED / 'ui'
FILES = ['ui.css', 'ui.js']


def manifest():
    return json.loads((UI / 'components.json').read_text())


def add(dest, update):
    dest.mkdir(parents=True, exist_ok=True)
    clash = [f for f in FILES if (dest / f).exists() and not filecmp.cmp(UI / f, dest / f, shallow=False)]
    if clash and not update:
        sys.exit(f'{dest}: {", ".join(clash)} differ from ui-library; --update replaces them')
    for f in FILES:
        shutil.copy2(UI / f, dest / f)
    m = manifest()
    print(f'Copied {", ".join(FILES)} to {dest}')
    print('In each page\'s <head>, after base.css (paths from the page):')
    for line in m['head'][1:]:
        print('  ' + line)


def show(name):
    m = manifest()
    c = next((c for c in m['components'] if c['name'] == name), None)
    if not c:
        sys.exit(f'no component {name!r}; --list shows them')
    print(f"{c['name']}  {c['selector']}  ({c['from']})\n")
    print('Use: ' + c['use'])
    if c.get('avoid'):
        print('Avoid: ' + c['avoid'])
    for a in c.get('attributes', []):
        print(f"  {a['name']} ({a['type']}{', default ' + repr(a['default']) if 'default' in a else ''}): {a['desc']}")
    for e in c.get('events', []):
        print(f"  event {e['name']} {e['detail']}: {e['desc']}")
    print('\n' + c['example'])


def docs():
    m = manifest()
    out = ['# Components', '',
           '<!-- Written by `python3 create.py --docs > docs/COMPONENTS.md` from ui/components.json. Edit that file, not this one. -->', '',
           m['about'], '', 'In each page\'s `<head>`:', '', '```html', *m['head'], '```', '',
           '`python3 create.py --gallery <dir>` builds a page showing every part. `--show <name>` prints one.', '', '## Rules', '']
    out += ['- ' + r for r in m['rules']]
    out += ['', '## Parts', '', '| Part | Markup | From | Use for |', '| --- | --- | --- | --- |']
    out += [f"| {c['name']} | `{c['selector']}` | {c['from']} | {c['use']} |" for c in m['components']]
    for c in m['components']:
        out += ['', f"### {c['name']}", '', c['use']]
        if c.get('avoid'):
            out += ['', 'Avoid: ' + c['avoid']]
        if c.get('attributes'):
            out += ['', '| Attribute | Value | Default | Does |', '| --- | --- | --- | --- |']
            pipe = '\\|'
            out += [f"| `{a['name']}` | {a['type'].replace('|', pipe)} | {a.get('default', '') or '—'} | {a['desc']} |" for a in c['attributes']]
        for e in c.get('events', []):
            out += ['', f"Fires `{e['name']}` with `{e['detail']}`: {e['desc']}"]
        out += ['', '```html', c['example'], '```']
    return '\n'.join(out) + '\n'


def tone(path, seconds, notes, bpm):
    """A short drum-and-bass loop, so the gallery's audio parts have something to show."""
    rate = 22050
    beat = 60 / bpm
    frames = []
    for i in range(int(seconds * rate)):
        t = i / rate
        b = t % beat
        kick = math.sin(2 * math.pi * (50 + 80 * math.exp(-b * 30)) * b) * math.exp(-b * 9)
        note = notes[int(t / beat) % len(notes)]
        bass = 0.25 * math.sin(2 * math.pi * note * t) * math.exp(-b * 3)
        frames.append(struct.pack('<h', int(max(-1, min(1, 0.6 * kick + bass)) * 30000)))
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(b''.join(frames))


def gallery(dest):
    if dest.exists() and any(dest.iterdir()):
        sys.exit(f'destination not empty: {dest}')
    m = manifest()
    assets = dest / 'assets'
    (assets / 'ui').mkdir(parents=True)
    shutil.copy2(SHARED / 'base.css', assets / 'base.css')
    shutil.copytree(SHARED / 'fonts', assets / 'fonts')
    for f in FILES:
        shutil.copy2(UI / f, assets / 'ui' / f)
    tone(assets / 'ui/sample.wav', 3, [55, 55, 65.4, 49], 120)
    tone(assets / 'ui/sample-new.wav', 3, [55, 65.4, 73.4, 82.4], 120)
    shutil.copy2(SHARED / 'gallery.css', assets / 'gallery.css')
    shutil.copy2(SHARED / 'gallery.js', assets / 'gallery.js')
    sections = []
    groups = {'ui.css': ('Interface', []), 'ui.js': ('Interactive', []), 'base.css': ('Wiki', [])}
    wide = {'wave', 'compare', 'plot', 'compare-table'}
    for c in m['components']:
        name = html.escape(c['name'])
        title = html.escape(c['name'].replace('-', ' ').capitalize())
        selector = html.escape(c['selector'])
        stylesheet = html.escape(c['from'])
        example = c['example']
        avoid = f'<p class="part__note"><span>Avoid</span> {html.escape(c["avoid"])}</p>' if c.get('avoid') else ''
        group = groups[c['from']][0]
        size = ' part--wide' if c['name'] in wide else ''
        groups[c['from']][1].append(f'<a href="#{name}">{title}</a>')
        sections.append(f"""
          <section class="part{size}" id="{name}" data-group="{group}" aria-labelledby="{name}-title">
            <header class="part__header">
              <h2 id="{name}-title">{title}</h2>
              <code>{selector}</code>
            </header>
            <div class="part__frame">
              <div class="part__live"><div class="part__example">{example}</div></div>
              <details class="part__source">
                <summary><span>View markup</span><code>{stylesheet}</code></summary>
                <ui-copy><pre><code>{html.escape(example)}</code></pre></ui-copy>
              </details>
            </div>
            <p class="part__description">{html.escape(c["use"])}</p>
            {avoid}
          </section>
        """)
    navigation = ''.join(
        f'<div class="index__group"><p>{label}</p>{"".join(links)}</div>'
        for label, links in groups.values()
    )
    about = html.escape(m['about'].partition('. ')[0])
    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#000000">
  <title>UI Library</title>
  {''.join(m['head'])}
  <link rel="stylesheet" href="./assets/gallery.css">
  <script type="module" src="./assets/gallery.js"></script>
</head>
<body id="top">
  <a class="skip" href="#components">Skip to components</a>
  <header class="gallery-header">
    <div class="gallery-header__inner">
      <a class="gallery-brand" href="#top">UI Library</a>
      <nav aria-label="Library links"><a href="https://github.com/simply-sunny/ui-library/blob/main/docs/COMPONENTS.md">Reference</a><a href="https://github.com/simply-sunny/ui-library">GitHub ↗</a></nav>
    </div>
  </header>
  <div class="gallery">
    <nav class="index" aria-label="Component index">{navigation}</nav>
    <main id="components" tabindex="-1">
      <header class="gallery-intro">
        <h1>Components</h1>
        <p>{about}.</p>
        <nav class="featured" aria-label="Featured components">
          <a href="#tabs"><strong>Loader tabs</strong><span>Switch install instructions</span><span aria-hidden="true">↘</span></a>
          <a href="#compare"><strong>A/B audio</strong><span>Hear versions in sync</span><span aria-hidden="true">↘</span></a>
          <a href="#callout"><strong>Callout</strong><span>Highlight a requirement</span><span aria-hidden="true">↘</span></a>
        </nav>
      </header>
      <div class="catalog-tools" hidden>
        <label for="component-search">Find a component</label>
        <input id="component-search" type="search" placeholder="Search names and descriptions">
        <div class="catalog-filters" role="group" aria-label="Component type">
          <button type="button" aria-pressed="true">All</button>
          <button type="button" aria-pressed="false">Interface</button>
          <button type="button" aria-pressed="false">Interactive</button>
          <button type="button" aria-pressed="false">Wiki</button>
        </div>
        <p class="catalog-status" role="status"></p>
      </div>
      <div class="catalog">{''.join(sections)}</div>
    </main>
  </div>
</body>
</html>
"""
    (dest / 'index.html').write_text(page)
    print(f'Created {dest}/index.html. Serve it (audio needs http): python3 -m http.server -d {dest}')


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], epilog='\n'.join(__doc__.splitlines()[1:]), formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dest', type=Path, help='copy ui.css and ui.js into this folder')
    g.add_argument('--list', action='store_true', help='list every component')
    g.add_argument('--show', metavar='NAME', help='print one component')
    g.add_argument('--gallery', type=Path, metavar='DIR', help='write a page showing every component')
    g.add_argument('--docs', action='store_true', help='print docs/COMPONENTS.md')
    ap.add_argument('--update', action='store_true', help='with --dest: replace ui files that differ')
    a = ap.parse_args()
    if a.dest:
        add(a.dest.resolve(), a.update)
    elif a.list:
        for c in manifest()['components']:
            print(f"{c['name']:<14} {c['selector']:<22} {c['use']}")
    elif a.show:
        show(a.show)
    elif a.gallery:
        gallery(a.gallery.resolve())
    else:
        sys.stdout.write(docs())


if __name__ == '__main__':
    main()
