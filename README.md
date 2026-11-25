# ui-library

Shared components for mod wikis and websites. The gallery shows the buttons, fields, toggles, plots and audio players in the black wiki theme.

[Live gallery](https://simply-sunny.github.io/ui-library/) · [Component reference](docs/COMPONENTS.md)

## Use

Copy `base.css` and `fonts/` into your site's assets directory. Keep the fonts next to the stylesheet. Copy the component styles and script into the same site's `assets/ui` directory.

```sh
python3 create.py --dest path/to/site/assets/ui
python3 create.py --list
python3 create.py --show compare
```

The component reference lists the stylesheets and script to add to each page. The installer asks for `--update` when a destination file differs.

## Develop

```sh
python3 -m unittest discover -s tests
python3 create.py --docs > docs/COMPONENTS.md
python3 create.py --gallery /tmp/ui-gallery
python3 -m http.server -d /tmp/ui-gallery
```

The gallery uses the examples in `ui/components.json`. Update the manifest when a component changes, then regenerate the reference.

## License

MIT. The IBM Plex font licenses are in `fonts/`.
