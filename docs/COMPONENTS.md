# Components

<!-- Written by `python3 create.py --docs > docs/COMPONENTS.md` from ui/components.json. Edit that file, not this one. -->

Shared components for mod wikis and websites. The ui directory holds ui.css and ui.js. The base stylesheet holds the tokens and base components. Add them to a site with `python3 create.py --dest <site>/public/assets/ui`.

In each page's `<head>`:

```html
<link rel="stylesheet" href="./assets/base.css">
<link rel="stylesheet" href="./assets/ui/ui.css">
<script type="module" src="./assets/ui/ui.js"></script>
```

`python3 create.py --gallery <dir>` builds a page showing every part. `--show <name>` prints one.

## Rules

- Use the shared components before adding page-specific CSS. Add reusable parts to ui-library.
- Spacing uses the tokens --s1 to --s8, or a token less 1px under a border (docs/LAYOUT.md). Line heights are multiples of 8.
- Colours come from base.css: --foreground, --muted, --border, --focus. Elements read them at draw time.
- No rounded corners, shadows, gradients or icons. Pressed or current things are underlined (text) or outlined (buttons).
- Text in parts follows docs/WRITING.md: short, exact, no hype.

## Parts

| Part | Markup | From | Use for |
| --- | --- | --- | --- |
| button | `.ui-button` | ui.css | An action that isn't a link: Play, Copy, Reset. aria-pressed="true" for one that's on. |
| toggle | `.ui-toggle` | ui.css | Picking one of a few views, filters or versions. Set aria-pressed on each button and update it in your script. |
| badge | `.ui-badge` | ui.css | A short value beside a name: a key, a tempo, a version. style="--ui-tone:#hex" colours it. |
| keycap | `.ui-keycap` | ui.css | A key in running text or a Keys table. |
| stats | `.ui-stats` | ui.css | A few numbers that matter, each with a short label: results, sizes, counts. |
| field | `.ui-field` | ui.css | A labelled text box, select or text area. |
| compare-table | `table.ui-compare-table` | ui.css | Two or three versions side by side, row by row. Put it in .table-wrap. |
| details | `details.ui-details` | ui.css | Something most readers skip: a long list, the steps for a rare case. |
| wave | `ui-wave` | ui.js | One sound, with its waveform: click to seek, Play or Space to play. |
| compare | `ui-compare` | ui.js | Versions of one sound, heard from the same moment: before and after a change. Space plays, 1 to 9 pick. |
| plot | `ui-plot` | ui.js | A handful of numbers to compare at a glance: per bar, per run, per version. band marks the range that's fine. |
| copy | `ui-copy` | ui.js | A command or snippet people paste: a Copy button on its code block. |
| tabs | `.tabs` | base.css | Use loader tabs when each download needs its own installation steps. |
| soon | `.soon` | base.css | Show a pending store listing with its review date. |
| actions | `.actions` | base.css | Put downloads and source links together below the lead. |
| meta | `.meta, .lead` | base.css | Show a short lead and supporting metadata such as an update date. |
| callout | `.ui-callout` | ui.css | Highlight a requirement or a brief note alongside the instructions. |
| breadcrumbs | `.ui-breadcrumbs` | ui.css | Show where a page sits in a documentation hierarchy. |
| progress | `.ui-progress` | ui.css | Show a known amount of work completed. |

### button

An action that isn't a link: Play, Copy, Reset. aria-pressed="true" for one that's on.

Avoid: Navigation (use a link) and picking one of a few views (use toggle).

```html
<button class="ui-button" type="button">Play</button> <button class="ui-button" type="button" aria-pressed="true">Loop</button>
```

### toggle

Picking one of a few views, filters or versions. Set aria-pressed on each button and update it in your script.

Avoid: More than about six choices (use a select in a field).

```html
<div class="ui-toggle" role="group" aria-label="Version"><button type="button" aria-pressed="false">Old</button><button type="button" aria-pressed="true">New</button></div>
```

### badge

A short value beside a name: a key, a tempo, a version. style="--ui-tone:#hex" colours it.

Avoid: Sentences, and colour as the only way to tell values apart.

```html
<span class="ui-badge">128 bpm</span> <span class="ui-badge" style="--ui-tone:#e0b070">5A</span>
```

### keycap

A key in running text or a Keys table.

Avoid: Keys the browser keeps, like Ctrl+Tab.

```html
Press <kbd class="ui-keycap">Space</kbd> to play.
```

### stats

A few numbers that matter, each with a short label: results, sizes, counts.

Avoid: More than five, or numbers that need a sentence to make sense.

```html
<dl class="ui-stats"><div><dt>Tempo</dt><dd>128.00</dd></div><div><dt>Beats apart</dt><dd>25 ms</dd></div><div><dt>Bars</dt><dd>8</dd></div></dl>
```

### field

A labelled text box, select or text area.

Avoid: Placeholder text in place of a label.

```html
<div class="ui-field"><label for="ex-name">Name</label><input id="ex-name" value="Cue My Music"></div>
```

### compare-table

Two or three versions side by side, row by row. Put it in .table-wrap.

Avoid: One column of data (use a plain table).

```html
<div class="table-wrap"><table class="ui-compare-table"><thead><tr><th></th><th>Old</th><th>New</th></tr></thead><tbody><tr><td>Tempo</td><td>125.03</td><td>128.00</td></tr><tr><td>Length</td><td>4 bars</td><td>8 bars</td></tr></tbody></table></div>
```

### details

Something most readers skip: a long list, the steps for a rare case.

Avoid: Hiding what everyone needs.

```html
<details class="ui-details"><summary>Build from source</summary><p>Run <code>./gradlew build</code>.</p></details>
```

### wave

One sound, with its waveform: click to seek, Play or Space to play.

Avoid: Several versions of one sound (use compare).

| Attribute | Value | Default | Does |
| --- | --- | --- | --- |
| `src` | url | — | The sound file, same origin. |
| `regions` | start,end[;start,end] | — | Seconds to shade. |
| `height` | px | 96 | Waveform height, a multiple of 8. |

```html
<ui-wave src="./assets/ui/sample.wav" regions="1,2.5"></ui-wave>
```

### compare

Versions of one sound, heard from the same moment: before and after a change. Space plays, 1 to 9 pick.

Avoid: Unrelated sounds (use a wave each).

| Attribute | Value | Default | Does |
| --- | --- | --- | --- |
| `height` | px | 96 | Waveform height. |
| `audio[data-label]` | text | — | Each version's name, in a child audio element. |
| `audio[data-regions]` | start,end[;start,end] | — | Seconds to shade in that version. |

Fires `ui-pick` with `{index, label}`: A version was picked.

```html
<ui-compare><audio src="./assets/ui/sample.wav" data-label="Old" data-regions="0.5,1.5"></audio><audio src="./assets/ui/sample-new.wav" data-label="New" data-regions="1,2.5"></audio></ui-compare>
```

### plot

A handful of numbers to compare at a glance: per bar, per run, per version. band marks the range that's fine.

Avoid: Exact values someone will read off (use a table), and more than about 60 points.

| Attribute | Value | Default | Does |
| --- | --- | --- | --- |
| `values` | number,number,… | — | The values, in order. |
| `labels` | text,text,… | — | A label under each value. |
| `kind` | bars\|line | bars | How to draw them. |
| `band` | low,high | — | The range that's fine; values past it draw muted. |
| `unit` | text | — | After each axis number, like ms. |
| `height` | px | 120 | Chart height, a multiple of 8. |

```html
<ui-plot values="22,8,-17,-11,4,0,-25,20" labels="1,2,3,4,5,6,7,8" band="-30,30" unit=" ms"></ui-plot>
```

### copy

A command or snippet people paste: a Copy button on its code block.

Avoid: Code people read rather than run.

```html
<ui-copy><pre><code>python3 create.py --dest public/assets/ui</code></pre></ui-copy>
```

### tabs

Use loader tabs when each download needs its own installation steps.

```html
<div class="tabs" role="group" aria-label="Mod loader">
  <input type="radio" name="ex-tabs" id="ex-a" checked><label for="ex-a">Fabric</label>
  <input type="radio" name="ex-tabs" id="ex-b"><label for="ex-b">NeoForge</label>
  <div class="tab">
    <h3>Install on Fabric</h3>
    <ul><li>Install Fabric Loader and Fabric API.</li><li>Put the Fabric build in <code>mods</code>.</li></ul>
  </div>
  <div class="tab">
    <h3>Install on NeoForge</h3>
    <ul><li>Install NeoForge for your game version.</li><li>Put the NeoForge build in <code>mods</code>.</li></ul>
  </div>
</div>
```

### soon

Show a pending store listing with its review date.

```html
<span class="soon" tabindex="0" data-tip="In review since 2026-11-20"><span class="soon__spin" aria-hidden="true"></span>CurseForge in review</span>
```

### actions

Put downloads and source links together below the lead.

```html
<div class="actions"><a href="https://modrinth.com/">Modrinth ↗</a><a href="https://www.curseforge.com/">CurseForge ↗</a><span>1.20.1 to 26.3</span></div>
```

### meta

Show a short lead and supporting metadata such as an update date.

```html
<p class="lead">Old and new transitions, side by side.</p><p class="meta">Updated 2026-11-23</p>
```

### callout

Highlight a requirement or a brief note alongside the instructions.

```html
<aside class="ui-callout" aria-labelledby="example-note"><h3 id="example-note">Client only</h3><p>Install the mod on your client. Servers can run without it.</p></aside>
```

### breadcrumbs

Show where a page sits in a documentation hierarchy.

```html
<nav class="ui-breadcrumbs" aria-label="Breadcrumb"><ol><li><a href="#components">Docs</a></li><li><a href="#tabs">Install</a></li><li aria-current="page">Fabric</li></ol></nav>
```

### progress

Show a known amount of work completed.

```html
<div class="ui-progress"><label for="example-progress">Indexing files</label><span aria-hidden="true">7 / 12</span><progress id="example-progress" value="7" max="12">7 of 12</progress></div>
```
