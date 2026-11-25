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
           '<!-- Written by `python3 create.py --docs > docs/COMPONENTS.md` from ui//components.json. Edit that file, not this one. -->', '',
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
    sections = []
    for c in m['components']:
        extra = '<p class="meta">Avoid: ' + html.escape(c['avoid']) + '</p>' if c.get('avoid') else ''
        sections.append(f'<section class="part" id="{c["name"]}"><h2>{html.escape(c["name"])}</h2>'
                        f'<p class="meta">{html.escape(c["selector"])} · {c["from"]}</p><p>{html.escape(c["use"])}</p>{extra}'
                        f'<div class="part__live">{c["example"]}</div>'
                        f'<ui-copy><pre><code>{html.escape(c["example"])}</code></pre></ui-copy></section>')
    page = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="theme-color" content="#000000"><title>Components</title>' + ''.join(m['head']) +
            '<style>.part{display:flex;flex-direction:column;gap:var(--s2);padding-block:calc(var(--s4) - 1px) var(--s4);border-top:1px solid var(--border)}'
            '.part>p{max-width:var(--measure)}.part pre{margin:0;padding:calc(var(--s2) - 1px);border:1px solid var(--border);overflow-x:auto;font:14px/24px PlexMono,monospace}'
            '.hero{display:flex;flex-direction:column;gap:var(--s2);padding-block:var(--s6)}</style></head><body>'
            '<header class="site-header shell"><span class="brand">Components</span><nav aria-label="Parts">'
            + ''.join(f'<a href="#{c["name"]}">{c["name"]}</a>' for c in m['components']) + '</nav></header>'
            '<main class="shell"><section class="hero"><h1>Components.</h1><p class="lead">' + html.escape(m['about'].split('. ')[0]) + '.</p></section>'
            + ''.join(sections) + '</main><footer class="site-footer shell"><a href="https://github.com/simply-sunny/ui-library">Source on GitHub</a><span>python3 create.py --list</span></footer></body></html>')
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
