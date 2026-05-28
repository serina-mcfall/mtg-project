#!/usr/bin/env python3
"""Turn a Scryfall search response into readable JSON, CSV, and HTML."""
import csv
import html
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
# Use the combined "all pages" file if present, otherwise the single-page sample.
SRC = HERE / "commanders-all.raw.json"
if not SRC.exists():
    SRC = HERE / "commanders-page1.raw.json"
SLUG = "commanders-all" if SRC.name.startswith("commanders-all") else "commanders-page1"

with SRC.open() as f:
    payload = json.load(f)

cards = payload["data"]


def clean(card: dict) -> dict:
    img = (card.get("image_uris") or {}).get("normal")
    if not img and card.get("card_faces"):
        img = (card["card_faces"][0].get("image_uris") or {}).get("normal")
    return {
        "name": card.get("name"),
        "mana_cost": card.get("mana_cost") or "",
        "cmc": card.get("cmc"),
        "type_line": card.get("type_line"),
        "oracle_text": card.get("oracle_text") or "",
        "power": card.get("power"),
        "toughness": card.get("toughness"),
        "color_identity": "".join(card.get("color_identity") or []) or "C",
        "set": card.get("set"),
        "set_name": card.get("set_name"),
        "rarity": card.get("rarity"),
        "edhrec_rank": card.get("edhrec_rank"),
        "usd": (card.get("prices") or {}).get("usd"),
        "image": img,
        "scryfall_uri": card.get("scryfall_uri"),
    }


pretty = [clean(c) for c in cards]

# 1. Pretty JSON
out_json = HERE / f"{SLUG}.pretty.json"
with out_json.open("w") as f:
    json.dump(pretty, f, indent=2, ensure_ascii=False)

# 2. CSV
out_csv = HERE / f"{SLUG}.csv"
with out_csv.open("w", newline="") as f:
    w = csv.DictWriter(
        f,
        fieldnames=[
            "name",
            "mana_cost",
            "cmc",
            "color_identity",
            "type_line",
            "power",
            "toughness",
            "rarity",
            "set",
            "edhrec_rank",
            "usd",
            "scryfall_uri",
        ],
    )
    w.writeheader()
    for row in pretty:
        w.writerow({k: row.get(k, "") for k in w.fieldnames})

# 3. HTML — sortable, filterable data table
def num(v):
    if v is None or v == "":
        return ""
    return v

rows = []
for c in pretty:
    pt = f"{c['power']}/{c['toughness']}" if c.get("power") not in (None, "") else ""
    rules = html.escape(c["oracle_text"]).replace("\n", "<br>")
    cmc_val = "" if c.get("cmc") is None else f"{c['cmc']:g}"
    rank = c.get("edhrec_rank")
    rank_disp = "" if rank is None else f"{rank:,}"
    usd = c.get("usd") or ""
    rows.append(
        f"""<tr>
  <td class="name"><a href="{html.escape(c['scryfall_uri'] or '#')}" target="_blank" rel="noopener">{html.escape(c['name'] or '')}</a></td>
  <td class="mono cost">{html.escape(c['mana_cost'])}</td>
  <td class="num" data-sort="{cmc_val}">{cmc_val}</td>
  <td class="mono ci">{html.escape(c['color_identity'])}</td>
  <td>{html.escape(c['type_line'] or '')}</td>
  <td class="mono">{pt}</td>
  <td>{html.escape(c['rarity'] or '')}</td>
  <td class="mono">{html.escape((c['set'] or '').upper())}</td>
  <td class="num" data-sort="{rank if rank is not None else ''}">{rank_disp}</td>
  <td class="num" data-sort="{usd}">{('$' + usd) if usd else ''}</td>
  <td class="rules">{rules}</td>
</tr>"""
    )

html_doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Commanders — Scryfall ({len(pretty):,} of {payload['total_cards']:,})</title>
<style>
  :root {{
    color-scheme: dark;
    --bg: #0f1115;
    --panel: #181b22;
    --ink: #e6e8ec;
    --muted: #9aa0aa;
    --accent: #c79b5d;
    --border: #262a33;
    --row-alt: #14171d;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 1.5rem;
    background: var(--bg);
    color: var(--ink);
    font: 14px/1.45 -apple-system, system-ui, "Segoe UI", sans-serif;
  }}
  h1 {{ font-size: 1.4rem; margin: 0 0 0.4rem; }}
  .meta {{ color: var(--muted); margin: 0 0 1rem; font-size: 0.85rem; }}
  .controls {{ display: flex; gap: 0.75rem; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; }}
  .controls label {{ font-size: 0.8rem; color: var(--muted); }}
  .controls input[type=search] {{
    background: var(--panel); color: var(--ink); border: 1px solid var(--border);
    border-radius: 6px; padding: 0.4rem 0.7rem; font: inherit; min-width: 240px;
  }}
  .controls input[type=search]:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 1px; }}
  .count {{ color: var(--muted); font-size: 0.8rem; }}
  .table-wrap {{ overflow: auto; border: 1px solid var(--border); border-radius: 8px; max-height: 80vh; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 0.82rem; }}
  thead th {{
    position: sticky; top: 0; z-index: 1;
    background: #1f232c; text-align: left; padding: 0.55rem 0.7rem;
    border-bottom: 1px solid var(--border); white-space: nowrap;
    font-weight: 600;
  }}
  thead th button {{
    all: unset; cursor: pointer; display: inline-flex; align-items: center; gap: 0.25rem;
    width: 100%;
  }}
  thead th button:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 3px; }}
  thead th[aria-sort=ascending] button::after  {{ content: " ▲"; color: var(--accent); }}
  thead th[aria-sort=descending] button::after {{ content: " ▼"; color: var(--accent); }}
  tbody tr:nth-child(even) {{ background: var(--row-alt); }}
  tbody tr:hover {{ background: #20242d; }}
  td {{ padding: 0.45rem 0.7rem; vertical-align: top; border-bottom: 1px solid var(--border); }}
  td.mono, td.num {{ font-family: ui-monospace, "Cascadia Mono", Menlo, monospace; font-size: 0.78rem; }}
  td.num {{ text-align: right; white-space: nowrap; }}
  td.name a {{ color: var(--ink); text-decoration: none; font-weight: 600; }}
  td.name a:hover {{ color: var(--accent); text-decoration: underline; }}
  td.name a:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 2px; }}
  td.rules {{ max-width: 28rem; font-size: 0.78rem; color: #cdd1d8; }}
  td.ci {{ letter-spacing: 0.15em; }}
  tr.hidden {{ display: none; }}
  @media (prefers-reduced-motion: reduce) {{
    * {{ animation: none !important; transition: none !important; }}
  }}
</style>
</head>
<body>
<h1>Commanders — Scryfall</h1>
<p class="meta">
  Query <code>is:commander</code> · Showing <strong>{len(pretty):,}</strong> of <strong>{payload['total_cards']:,}</strong> ·
  Click a column header to sort. Type in the filter to narrow.
</p>
<div class="controls">
  <label for="filter">Filter (name, type, rules text):</label>
  <input id="filter" type="search" placeholder="e.g. dragon, flying, lifelink…" autocomplete="off">
  <span class="count" id="count" aria-live="polite">{len(pretty)} rows</span>
</div>
<div class="table-wrap">
<table id="cards">
  <thead>
    <tr>
      <th scope="col" aria-sort="none"><button type="button" data-col="0" data-type="text">Name</button></th>
      <th scope="col" aria-sort="none"><button type="button" data-col="1" data-type="text">Cost</button></th>
      <th scope="col" aria-sort="none"><button type="button" data-col="2" data-type="num">CMC</button></th>
      <th scope="col" aria-sort="none"><button type="button" data-col="3" data-type="text">CI</button></th>
      <th scope="col" aria-sort="none"><button type="button" data-col="4" data-type="text">Type</button></th>
      <th scope="col" aria-sort="none"><button type="button" data-col="5" data-type="text">P/T</button></th>
      <th scope="col" aria-sort="none"><button type="button" data-col="6" data-type="text">Rarity</button></th>
      <th scope="col" aria-sort="none"><button type="button" data-col="7" data-type="text">Set</button></th>
      <th scope="col" aria-sort="none"><button type="button" data-col="8" data-type="num">EDHREC</button></th>
      <th scope="col" aria-sort="none"><button type="button" data-col="9" data-type="num">USD</button></th>
      <th scope="col">Rules</th>
    </tr>
  </thead>
  <tbody>
{''.join(rows)}
  </tbody>
</table>
</div>
<script>
(() => {{
  const table = document.getElementById('cards');
  const tbody = table.tBodies[0];
  const filter = document.getElementById('filter');
  const count = document.getElementById('count');

  function applyFilter() {{
    const q = filter.value.trim().toLowerCase();
    let shown = 0;
    for (const tr of tbody.rows) {{
      const hit = !q || tr.textContent.toLowerCase().includes(q);
      tr.classList.toggle('hidden', !hit);
      if (hit) shown++;
    }}
    count.textContent = shown + ' rows';
  }}
  filter.addEventListener('input', applyFilter);

  table.querySelectorAll('thead button').forEach(btn => {{
    btn.addEventListener('click', () => {{
      const col = +btn.dataset.col;
      const type = btn.dataset.type;
      const th = btn.parentElement;
      const current = th.getAttribute('aria-sort');
      const dir = current === 'ascending' ? 'descending' : 'ascending';

      table.querySelectorAll('thead th').forEach(h => h.setAttribute('aria-sort', 'none'));
      th.setAttribute('aria-sort', dir);

      const rows = Array.from(tbody.rows);
      rows.sort((a, b) => {{
        const ca = a.cells[col];
        const cb = b.cells[col];
        let va = ca.dataset.sort ?? ca.textContent.trim();
        let vb = cb.dataset.sort ?? cb.textContent.trim();
        if (type === 'num') {{
          const na = va === '' ? Infinity : parseFloat(va);
          const nb = vb === '' ? Infinity : parseFloat(vb);
          return dir === 'ascending' ? na - nb : nb - na;
        }}
        va = va.toLowerCase(); vb = vb.toLowerCase();
        if (va < vb) return dir === 'ascending' ? -1 : 1;
        if (va > vb) return dir === 'ascending' ?  1 : -1;
        return 0;
      }});
      for (const r of rows) tbody.appendChild(r);
    }});
  }});
}})();
</script>
</body>
</html>
"""

out_html = HERE / f"{SLUG}.html"
out_html.write_text(html_doc)

print(f"Wrote {len(pretty)} cards across 3 files:")
for p in (out_json, out_csv, out_html):
    print(f"  {p}  ({p.stat().st_size:,} bytes)")
