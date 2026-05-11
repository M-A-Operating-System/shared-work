#!/usr/bin/env python3
"""
Generates a single PDF from the AI Chat Platform design specification.

Usage:
    python generate_pdf.py [output.pdf]

Output defaults to ./docs/product/assistant/assistant_product_design.pdf

Requirements:
    pip install markdown weasyprint
"""

import re
import sys
from pathlib import Path

# ---------- configuration ----------

DOCS_DIR = Path(__file__).parent / "docs" / "product" / "assistant"
DEFAULT_OUTPUT = DOCS_DIR / "assistant_product_design.pdf"

DOC_TITLE = "AI Chat Platform"
DOC_SUBTITLE = "Product Design Specification"
DOC_META = "Draft v1.0 · May 2026"

EXCLUDE = {"README.md"}

# ---------- document ordering ----------

def get_ordered_files(docs_dir: Path) -> list[Path]:
    """Numbered docs in reading order, then ROADMAP."""
    numbered = sorted(
        [f for f in docs_dir.glob("[0-9][0-9]-*.md") if f.name not in EXCLUDE],
        key=lambda f: f.stem[:2],
    )
    roadmap = docs_dir / "ROADMAP.md"
    result = list(numbered)
    if roadmap.exists() and "ROADMAP.md" not in EXCLUDE:
        result.append(roadmap)
    return result

# ---------- markdown processing ----------

def strip_md_links(text: str) -> str:
    """Replace cross-doc .md links with plain text — they don't resolve in PDF."""
    return re.sub(r"\(\./[\w-]+\.md(?:#[\w-]*)?\)", "()", text)


def build_html(files: list[Path]) -> str:
    import markdown

    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "toc", "sane_lists"],
    )

    sections = []
    for i, path in enumerate(files):
        raw = strip_md_links(path.read_text(encoding="utf-8"))
        body = md.convert(raw)
        md.reset()
        extra_class = " first-section" if i == 0 else ""
        sections.append(f'<section class="doc-section{extra_class}">{body}</section>')

    cover = f"""
<div class="cover-page">
  <div class="cover-inner">
    <p class="cover-eyebrow">Confidential · Internal</p>
    <h1 class="cover-title">{DOC_TITLE}</h1>
    <p class="cover-subtitle">{DOC_SUBTITLE}</p>
    <hr class="cover-rule">
    <p class="cover-meta">{DOC_META}</p>
  </div>
</div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>{DOC_TITLE} — {DOC_SUBTITLE}</title></head>
<body>
{cover}
{"".join(sections)}
</body>
</html>"""

# ---------- stylesheet ----------

CSS = """
@page {
    size: A4;
    margin: 22mm 24mm 26mm 24mm;
    @bottom-right {
        content: counter(page);
        font-family: system-ui, sans-serif;
        font-size: 8pt;
        color: #9ca3af;
    }
}

@page cover-page {
    margin: 0;
    @bottom-right { content: none; }
}

/* Cover */
.cover-page {
    page: cover-page;
    page-break-after: always;
    background-color: #1e3a6e;
    min-height: 297mm;
    display: flex;
    align-items: center;
    padding: 0 28mm;
    box-sizing: border-box;
}
.cover-inner  { color: #ffffff; max-width: 130mm; }
.cover-eyebrow {
    font-size: 8pt;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    opacity: 0.55;
    margin: 0 0 14mm;
}
.cover-title {
    font-size: 30pt;
    font-weight: 700;
    line-height: 1.1;
    margin: 0 0 5mm;
}
.cover-subtitle {
    font-size: 13pt;
    opacity: 0.75;
    margin: 0 0 12mm;
    font-weight: 400;
}
.cover-rule {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.25);
    margin: 0 0 8mm;
}
.cover-meta { font-size: 9pt; opacity: 0.5; margin: 0; }

/* Document sections */
.doc-section           { page-break-before: always; }
.doc-section.first-section { page-break-before: avoid; }

/* Base typography */
body {
    font-family: system-ui, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif;
    font-size: 9.5pt;
    line-height: 1.65;
    color: #111827;
}

h1 {
    font-size: 17pt;
    font-weight: 700;
    color: #1e3a6e;
    margin: 0 0 5mm;
    padding-bottom: 3mm;
    border-bottom: 2px solid #dbeafe;
}
h2 {
    font-size: 12pt;
    font-weight: 700;
    color: #1e3a6e;
    margin: 8mm 0 2mm;
}
h3 {
    font-size: 10.5pt;
    font-weight: 600;
    color: #374151;
    margin: 5mm 0 1.5mm;
}
h4 {
    font-size: 9.5pt;
    font-weight: 600;
    color: #374151;
    margin: 3mm 0 1mm;
}
p { margin: 0 0 3mm; }

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 4mm 0;
    font-size: 8.5pt;
}
th {
    background-color: #eff6ff;
    color: #1e3a6e;
    font-weight: 600;
    padding: 4pt 7pt;
    text-align: left;
    border: 1px solid #bfdbfe;
}
td {
    padding: 3.5pt 7pt;
    border: 1px solid #e5e7eb;
    vertical-align: top;
}
tr:nth-child(even) td { background-color: #f9fafb; }

/* Code */
code {
    font-family: 'Courier New', Courier, monospace;
    font-size: 8pt;
    background-color: #f3f4f6;
    color: #1e3a6e;
    padding: 1pt 3pt;
    border-radius: 2pt;
    word-break: break-word;
}
pre {
    background-color: #1e293b;
    color: #cbd5e1;
    font-family: 'Courier New', Courier, monospace;
    font-size: 7.5pt;
    line-height: 1.5;
    padding: 8pt 10pt;
    border-radius: 3pt;
    margin: 3mm 0;
    white-space: pre-wrap;
    word-break: break-all;
    page-break-inside: avoid;
}
pre code {
    background: none;
    color: inherit;
    padding: 0;
    font-size: inherit;
    border-radius: 0;
}

/* Blockquotes */
blockquote {
    border-left: 3pt solid #3b82f6;
    background-color: #eff6ff;
    margin: 3mm 0;
    padding: 4pt 10pt;
    color: #1e3a6e;
    font-size: 9pt;
}

/* Lists */
ul, ol { margin: 1mm 0 3mm; padding-left: 5mm; }
li { margin-bottom: 1.5pt; }

/* Dividers */
hr { border: none; border-top: 1px solid #e5e7eb; margin: 5mm 0; }

/* Links (decorative — PDF doesn't follow them) */
a { color: #1d4ed8; text-decoration: none; }

/* Pagination hints */
h1, h2, h3 { page-break-after: avoid; }
tr          { page-break-inside: avoid; }
"""

# ---------- main ----------

def main():
    try:
        from weasyprint import HTML, CSS as WeasyprintCSS
    except ImportError:
        print("weasyprint not installed. Run: pip install markdown weasyprint")
        sys.exit(1)

    output = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT
    files = get_ordered_files(DOCS_DIR)

    if not files:
        print(f"No markdown files found in {DOCS_DIR}")
        sys.exit(1)

    print(f"Documents ({len(files)}):")
    for f in files:
        print(f"  {f.name}")

    print("\nBuilding HTML…")
    html = build_html(files)

    print("Rendering PDF (this may take a moment)…")
    HTML(string=html, base_url=str(DOCS_DIR)).write_pdf(
        str(output),
        stylesheets=[WeasyprintCSS(string=CSS)],
    )

    size_mb = output.stat().st_size / 1_000_000
    print(f"\nDone → {output}  ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
