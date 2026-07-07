# ETF Rotation Research Lab

Public-safe interactive portfolio dashboard for an ETF rotation research system.

## Scope

- Static resume / GitHub Pages-ready web page.
- Reads only public-safe JSON generated from local research artifacts.
- Does not include account data, tokens, broker state, or live order capability.
- Does not change underlying strategy logic.

## Build Data

```bash
python3 scripts/build_public_data.py
```

## Preview

```bash
python3 -m http.server 8090
```

Open:

```text
http://localhost:8090/
```

## Files

- `index.html` - page structure
- `styles.css` - visual system
- `app.js` - language toggle, filters, and SVG charts
- `data/strategy_dashboard_data.json` - generated public-safe data snapshot
