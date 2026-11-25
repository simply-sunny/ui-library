# Components

<!-- Written by `python3 create.py --docs > docs/COMPONENTS.md` from ui//components.json. Edit that file, not this one. -->

Shared components for mod wikis and websites. The ui directory holds ui.css and ui.js. The base stylesheet holds the tokens and base components. Add them to a site with `python3 create.py --dest <site>/public/assets/ui`.

In each page's `<head>`:

```html
<link rel="stylesheet" href="./assets/base.css">
<link rel="stylesheet" href="./assets/ui/ui.css">
<script type="module" src="./assets/ui/ui.js"></script>
```

`python3 create.py --gallery <dir>` builds a page showing every part. `--show <name>` prints one.

## Rules

- Use a part from this list before writing new CSS. A new part goes here, in the templates, not in one site.
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
| tabs | `.tabs` | base.css | The same steps for different setups, one shown at a time (Fabric first). Works without JavaScript; up to four tabs. |
| soon | `.soon` | base.css | Something on its way: a store in review. data-tip says since when. |
| actions | `.actions` | base.css | A row of links under a heading or lead: downloads, source. |
| meta | `.meta, .lead` | base.css | .lead for the line under a title; .meta for small mono notes: dates, counts, keys. |

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

The same steps for different setups, one shown at a time (Fabric first). Works without JavaScript; up to four tabs.

Avoid: Content everyone should read.

```html
<div class="tabs"><input type="radio" name="ex-tabs" id="ex-a" checked><label for="ex-a">Fabric</label><input type="radio" name="ex-tabs" id="ex-b"><label for="ex-b">NeoForge</label><div class="tab"><p>Put the jar in mods.</p></div><div class="tab"><p>Not yet.</p></div></div>
```

### soon

Something on its way: a store in review. data-tip says since when.

Avoid: Anything without a date.

```html
<span class="soon" tabindex="0" data-tip="In review since 2026-11-20"><span class="soon__spin"></span>CurseForge</span>
```

### actions

A row of links under a heading or lead: downloads, source.

Avoid: Buttons that act on the page.

```html
<div class="actions"><a href="#">Modrinth ↗</a><a href="#">CurseForge ↗</a><span>1.20.1 to 26.3</span></div>
```

### meta

.lead for the line under a title; .meta for small mono notes: dates, counts, keys.

Avoid: Body text.

```html
<p class="lead">Old and new transitions, side by side.</p><p class="meta">Updated 2026-11-23</p>
```
