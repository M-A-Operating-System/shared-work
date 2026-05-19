#!/usr/bin/env python3
"""
Generates a PDF for each product in docs/product/, placing the output inside
the respective product folder.

Usage:
    python generate_pdf.py [product-name]

    python generate_pdf.py          → generates all products
    python generate_pdf.py assistant → generates only the assistant product
    python generate_pdf.py analytics → generates only the analytics product

Requirements:
    pip install markdown weasyprint
"""

import html as _html
import re
import sys

# fontTools raises ValueError when it encounters OS/2 Unicode range bit 123 (out of
# spec, 0–122 valid). Some system fonts on Linux carry this invalid bit. Patch the
# setter to silently discard out-of-range bits so WeasyPrint can continue.
try:
    from fontTools.ttLib.tables import O_S_2f_2 as _os2_mod
    _Table = _os2_mod.table_O_S_2f_2
    _orig = _Table.setUnicodeRanges
    def _safe_setUnicodeRanges(self, value):
        _orig(self, {b for b in value if 0 <= b <= 122})
    _Table.setUnicodeRanges = _safe_setUnicodeRanges
except Exception as _e:
    import warnings
    warnings.warn(f"fontTools Unicode range patch failed ({_e}); PDF generation may fail on some fonts")
from pathlib import Path

# ---------- product registry ----------

PRODUCTS_DIR = Path(__file__).parent / "docs" / "product"

PRODUCTS = {
    "assistant": {
        "title":  "AI Chat Platform",
        "meta":   "Draft v1.0 · May 2026",
        "output": "assistant_product_design.pdf",
    },
    "analytics": {
        "title":  "AI Analytics Platform",
        "meta":   "Draft v1.0 · May 2026",
        "output": "analytics_product_design.pdf",
    },
}

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


def build_html(files: list[Path], title: str, meta: str,
               subs: dict[str, str] | None = None) -> str:
    import markdown

    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "toc", "sane_lists"],
    )

    sections = []
    for i, path in enumerate(files):
        raw = strip_md_links(path.read_text(encoding="utf-8"))
        if subs:
            for key, val in subs.items():
                raw = raw.replace(key, val)
        body = md.convert(raw)
        md.reset()
        extra_class = " first-section" if i == 0 else ""
        sections.append(f'<section class="doc-section{extra_class}">{body}</section>')

    safe_title = _html.escape(title)
    safe_meta  = _html.escape(meta)

    cover = f"""
<div class="cover-page">
  <div class="cover-inner">
    <p class="cover-eyebrow">M&amp;A Operating System</p>
    <p class="cover-category">Product Design</p>
    <h1 class="cover-title">{safe_title}</h1>
    <hr class="cover-rule">
    <p class="cover-meta">{safe_meta}</p>
  </div>
</div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>{safe_title}</title></head>
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
    background-color: #ffffff;
    min-height: 297mm;
    display: flex;
    align-items: center;
    padding: 0 28mm;
    box-sizing: border-box;
}
.cover-inner { max-width: 130mm; }
.cover-eyebrow {
    font-size: 8pt;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6b7280;
    margin: 0 0 4mm;
}
.cover-category {
    font-size: 11pt;
    color: #374151;
    font-weight: 400;
    margin: 0 0 5mm;
}
.cover-title {
    font-size: 30pt;
    font-weight: 700;
    line-height: 1.1;
    color: #1e3a6e;
    margin: 0 0 12mm;
}
.cover-rule {
    border: none;
    border-top: 2px solid #1e3a6e;
    margin: 0 0 8mm;
}
.cover-meta { font-size: 9pt; color: #9ca3af; margin: 0; }

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

# ---------- per-product generation ----------

def generate_product(name: str, config: dict) -> None:
    docs_dir = PRODUCTS_DIR / name
    if not docs_dir.is_dir():
        print(f"  [skip] {name}: directory not found at {docs_dir}")
        return

    output = docs_dir / config["output"]
    about = PRODUCTS_DIR / "about.md"
    files = ([about] if about.exists() else []) + get_ordered_files(docs_dir)

    if not files:
        print(f"  [skip] {name}: no markdown files found in {docs_dir}")
        return

    print(f"\n── {name} ──────────────────────────────────────────")
    print(f"Documents ({len(files)}):")
    for f in files:
        print(f"  {f.name}")

    print("Building HTML…")
    html = build_html(files, config["title"], config["meta"],
                      subs={"{{PRODUCT_NAME}}": name})

    print("Rendering PDF (this may take a moment)…")
    from weasyprint import HTML, CSS as WeasyprintCSS
    HTML(string=html, base_url=str(docs_dir)).write_pdf(
        str(output),
        stylesheets=[WeasyprintCSS(string=CSS)],
    )

    size_mb = output.stat().st_size / 1_000_000
    print(f"Done → {output}  ({size_mb:.1f} MB)")

# ---------- single-page generation ----------

def _resolve_page_path(file_path: Path) -> Path:
    """Resolve a page path, searching product directories if only a filename was given."""
    if file_path.is_file() and not file_path.is_symlink():
        return file_path.resolve()

    # Search all product directories for a file with this name
    candidates = sorted(
        f for f in PRODUCTS_DIR.rglob(file_path.name)
        if f.is_file() and not f.is_symlink()
    )
    repo_root = Path(__file__).parent
    if len(candidates) == 1:
        resolved = candidates[0].relative_to(repo_root)
        print(f"  [info] resolved '{file_path.name}' → {resolved}")
        return candidates[0].resolve()
    if len(candidates) > 1:
        print(f"  [error] '{file_path.name}' matches multiple files — use the full path:")
        for c in candidates:
            print(f"    {c.relative_to(repo_root)}")
        sys.exit(1)
    print(f"  [error] '{file_path.name}' not found in any product directory.")
    print(f"          Provide the path relative to the repo root,")
    print(f"          e.g.: docs/product/analytics/07-text-to-sql-antipattern.md")
    sys.exit(1)


def generate_page(file_path: Path) -> None:
    """Generate a PDF for a single .md file, placed next to it."""
    if file_path.is_symlink():
        print(f"  [error] symlinks are not supported: {file_path}")
        sys.exit(1)

    file_path = _resolve_page_path(file_path)

    if file_path.suffix != '.md':
        print(f"  [error] only .md files are supported, got: {file_path.name}")
        sys.exit(1)

    if not file_path.is_file():
        print(f"  [error] file not found: {file_path}")
        sys.exit(1)

    config = None
    for name, cfg in PRODUCTS.items():
        if file_path.parent == (PRODUCTS_DIR / name).resolve():
            config = cfg
            break

    if config is None:
        print(f"  [error] {file_path}: not inside a known product directory")
        sys.exit(1)

    raw = file_path.read_text(encoding="utf-8")
    h1 = re.search(r'^#\s+(.+)$', raw, re.MULTILINE)
    page_title = h1.group(1).strip() if h1 else file_path.stem

    output = file_path.with_suffix('.pdf')

    print(f"\n── page: {file_path.name} ──────────────────────────────────────────")
    print("Building HTML…")
    html = build_html([file_path], page_title, config["meta"])

    print("Rendering PDF…")
    from weasyprint import HTML, CSS as WeasyprintCSS
    HTML(string=html, base_url=str(file_path.parent)).write_pdf(
        str(output),
        stylesheets=[WeasyprintCSS(string=CSS)],
    )

    size_mb = output.stat().st_size / 1_000_000
    print(f"Done → {output}  ({size_mb:.1f} MB)")

# ---------- main ----------

def main():
    try:
        from weasyprint import HTML  # noqa: F401
    except ImportError:
        print("weasyprint not installed. Run: pip install markdown weasyprint")
        sys.exit(1)

    if len(sys.argv) > 1 and sys.argv[1] == '--page':
        if len(sys.argv) < 3:
            print("Usage: python generate_pdf.py --page <path/to/file.md>")
            sys.exit(1)
        generate_page(Path(sys.argv[2]))
        print("\nAll done.")
        return

    requested = sys.argv[1] if len(sys.argv) > 1 else None

    if requested:
        if requested not in PRODUCTS:
            print(f"Unknown product '{requested}'. Available: {', '.join(PRODUCTS)}")
            sys.exit(1)
        targets = {requested: PRODUCTS[requested]}
    else:
        targets = PRODUCTS

    for name, config in targets.items():
        generate_product(name, config)

    print("\nAll done.")


if __name__ == "__main__":
    main()
