#!/usr/bin/env python3
"""Build a PDF of the lite Data Model Design Document (no content changes)."""
from __future__ import annotations
import hashlib, re, subprocess, sys
from pathlib import Path
import markdown

SRC: Path = Path('/tmp/claude-0/-home-claude/4770b2d2-f54e-5ec8-aa89-f4fc7cefb22c/scratchpad/mfgwork/cpg-manufacturing-data-design-document-lite.md')
WORK: Path = Path(__file__).parent
OUT: Path = Path('/tmp/claude-0/-home-claude/4770b2d2-f54e-5ec8-aa89-f4fc7cefb22c/scratchpad/pdfmfg/cpg-manufacturing-data-design-document-lite.pdf')
EXPECT: str = '8346c18809d2'

text: str = SRC.read_text(encoding="utf-8")
sha: str = hashlib.sha256(SRC.read_bytes()).hexdigest()

# 1. mermaid -> png
blocks: list[str] = re.findall(r"```mermaid\n(.*?)```", text, re.S)
cfg = WORK / "mm.json"
cfg.write_text('{"args":["--no-sandbox"]}')
pcfg = WORK / "pp.json"
pcfg.write_text('{"args":["--no-sandbox"]}')
for i, b in enumerate(blocks, 1):
    if b.count("-->") > 8 and ("SBJ" in b or "subgraph" in b):
        b = b.replace("flowchart LR", "flowchart TB", 1)  # print layout only: wide rather than tall
    (WORK / f"d{i}.mmd").write_text(b, encoding="utf-8")
    r = subprocess.run(["/home/claude/.npm-global/bin/mmdc", "-i", str(WORK / f"d{i}.mmd"),
        "-o", str(WORK / f"d{i}.png"), "-p", str(pcfg), "-c", str(WORK / ("mmc3.json" if "SBJ" in b and b.count("-->") > 8 else "mmc.json")), "-s", "2", "-w", "1600", "-b", "white"],
        capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"mmdc failed on {i}: {r.stderr[-800:]}")
from PIL import Image
def _img(i: int) -> str:
    w, h = Image.open(WORK / f"d{i}.png").size
    cw: float = w / 2
    return f'\n<div class="diagram"><img src="d{i}.png" style="width:{cw:.0f}px"/></div>\n'
n = iter(range(1, len(blocks) + 1))
text = re.sub(r"```mermaid\n.*?```", lambda m: _img(next(n)), text, flags=re.S)

# 2. markdown -> html, GitHub-style heading ids
def slug(v: str, sep: str) -> str:
    v = re.sub(r"<[^>]+>", "", v).lower()
    v = re.sub(r"[^\w\- ]", "", v)
    return v.replace(" ", "-")
html: str = markdown.markdown(text, extensions=["tables", "fenced_code", "attr_list", "toc", "sane_lists"],
    extension_configs={"toc": {"slugify": slug}})
(WORK / "doc.html").write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>CPG Manufacturing and Supply Chain — Data Model Design Document</title>
<style>
@page {{ size: A4 landscape; margin: 16mm 14mm 18mm 14mm; }}
body {{ font-family: "DejaVu Sans", "Liberation Sans", Arial, sans-serif; font-size: 9pt; line-height: 1.4; color: #1a1a1a; }}
h1 {{ font-size: 22pt; margin: 0 0 8mm; color: #0b2545; }}
h2 {{ font-size: 15pt; color: #0b2545; border-bottom: 1.5px solid #0b2545; padding-bottom: 2px; margin-top: 10mm; break-after: avoid; }}
h3 {{ font-size: 12pt; color: #13315c; margin-top: 7mm; break-after: avoid; }}
h4 {{ font-size: 10pt; color: #13315c; break-after: avoid; }}
table {{ border-collapse: collapse; width: 100%; margin: 3mm 0 5mm; font-size: 7.8pt; table-layout: auto; }}
th, td {{ border: 0.6px solid #9aa5b1; padding: 2px 4px; vertical-align: top; overflow-wrap: break-word; }}
th {{ background: #e6ecf3; text-align: left; }}
thead {{ display: table-header-group; }}
tr {{ break-inside: avoid; }}
code {{ font-family: "DejaVu Sans Mono", monospace; font-size: 7.6pt; background: #f2f4f7; padding: 0 2px; }}
a {{ color: #0b57d0; text-decoration: none; }}
.diagram {{ text-align: center; margin: 4mm 0; break-inside: avoid; }}
.diagram img {{ max-width: 100%; max-height: 135mm; width: auto; object-fit: contain; }}
p:has(+ .diagram), h3 + p, h4 + p {{ break-after: avoid; }}
p:has(+ .diagram) {{ break-inside: avoid; }}
ul {{ padding-left: 5mm; }} li {{ margin: 1px 0; }}
</style></head><body>{html}</body></html>""", encoding="utf-8")

# 3. chrome -> pdf
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    br = p.chromium.launch()
    pg = br.new_page()
    pg.goto((WORK / "doc.html").as_uri())
    pg.wait_for_load_state("networkidle")
    pg.pdf(path=str(OUT), format="A4", landscape=True, print_background=True, display_header_footer=True,
        header_template="<span></span>",
        footer_template='<div style="font-size:7pt;width:100%;padding:0 14mm;display:flex;justify-content:space-between;color:#555;font-family:sans-serif"><span>CPG Manufacturing and Supply Chain — Data Model Design Document · M&amp;A Operating System</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>',
        margin={"top": "16mm", "bottom": "18mm", "left": "14mm", "right": "14mm"})
    br.close()
print("ok", OUT, OUT.stat().st_size)
