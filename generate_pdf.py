#!/usr/bin/env python3
"""
Generates a PDF for each product in docs/product/, placing the output inside
the respective product folder.

Usage:
    python generate_pdf.py [--product <name>] [--nofront]
    python generate_pdf.py --page <path/to/file.md> [--nofront]
    python generate_pdf.py --product <name> --pages <nn> [<nn> ...] [--out <file.pdf>] [--nofront]

    python generate_pdf.py                              → generates all products
    python generate_pdf.py --product analytics          → generates only the analytics product
    python generate_pdf.py --product analytics --nofront
                                                        → without branded cover page
    python generate_pdf.py --product analytics --pages 02 04 08
                                                        → merged PDF of specific chapters
    python generate_pdf.py --product analytics --pages 02 08 --out subset.pdf
                                                        → merged PDF written to subset.pdf

    --product   Select a single product by name.  Omit to generate all products.
    --pages     Space-separated two-digit chapter prefixes to include (requires --product).
                Chapters are included in the order listed on the command line.
    --out       Output filename for --pages mode.  When omitted: a single chapter
                prefix produces a PDF next to the source file with the same name
                and a .pdf extension (identical to --page); multiple prefixes
                produce <product>_pages_<nn…>.pdf in the product directory.
    --nofront   Omit the branded cover page. Useful for distributing content
                outside the M&A Operating System brand context.

Requirements:
    pip install markdown weasyprint
"""

import html as _html
import base64 as _b64
import json
import os
import re
import struct
import subprocess
import sys
import tempfile

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
except (ImportError, AttributeError) as _e:
    import warnings
    warnings.warn(f"fontTools Unicode range patch failed ({_e}); PDF generation may fail on some fonts")
from pathlib import Path

# ---------- product registry ----------

PRODUCTS_DIR = Path(__file__).parent / "docs" / "product"

PRODUCTS = {
    "assistant": {
        "title":  "AI Chat Platform",
        "meta":   "Draft v1.0 · May 2026",
        "author": "Andrew Bush (www.maoperatingsystem.com/bio-andrew-bush)",
        "output": "assistant_product_design.pdf",
    },
    "analytics": {
        "title":  "AI Analytics Platform",
        "meta":   "Draft v1.0 · May 2026",
        "author": "Andrew Bush (www.maoperatingsystem.com/bio-andrew-bush)",
        "output": "analytics_product_design.pdf",
    },
}

EXCLUDE = {"README.md"}

# ---------- document ordering ----------

def get_ordered_files(docs_dir: Path) -> list[Path]:
    """Numbered docs in reading order, then ROADMAP.

    Files whose stem contains '-ignore' are parked and excluded from the build.
    """
    numbered = sorted(
        [f for f in docs_dir.glob("[0-9][0-9]-*.md")
         if f.name not in EXCLUDE and "-ignore" not in f.stem],
        key=lambda f: int(f.stem[:2]),
    )
    roadmap = docs_dir / "ROADMAP.md"
    result = list(numbered)
    if roadmap.exists() and "ROADMAP.md" not in EXCLUDE:
        result.append(roadmap)
    return result

# ---------- markdown processing ----------

def strip_md_links(text: str) -> str:
    """Replace cross-doc .md links with their plain text — they don't resolve in PDF."""
    # [label](./file.md#anchor) → label
    text = re.sub(r"\[([^\]]+)\]\(\./[\w-]+\.md(?:#[\w-]*)?\)", r"\1", text)
    # any remaining bare (./file.md#anchor) with no label → drop it
    text = re.sub(r"\(\./[\w-]+\.md(?:#[\w-]*)?\)", "", text)
    return text


# ---------- mermaid rendering ----------

def _mmdc_available() -> bool:
    try:
        subprocess.run(["mmdc", "--version"], capture_output=True, timeout=10)
        return True
    except (FileNotFoundError, subprocess.SubprocessError):
        return False


_MMDC_PRESENT: bool | None = None  # cached after first check


def _png_size(path: Path) -> tuple[int, int]:
    """Return (width, height) in pixels by reading the PNG IHDR chunk directly."""
    with open(path, "rb") as f:
        f.seek(16)  # 8-byte PNG signature + 4-byte chunk length + 4-byte "IHDR"
        w, h = struct.unpack(">II", f.read(8))
    return w, h


# Content area for US Letter after margins (22mm top, 26mm bottom, 24mm each side):
#   width  = 215.9mm − 48mm  = 167.9mm  → use 160mm to leave breathing room
#   height = 279.4mm − 48mm  = 231.4mm  → cap diagrams at 180mm so they sit with text
_MAX_DIAGRAM_W_MM = 160.0
_MAX_DIAGRAM_H_MM = 180.0


def _diagram_display_size(px_w: int, px_h: int) -> tuple[float, float]:
    """
    Scale px_w × px_h to fit within the page content area, preserving aspect ratio.
    Returns (width_mm, height_mm) as explicit display dimensions for the <img> tag.
    WeasyPrint does not correctly resolve aspect ratio when both max-width and
    max-height are active with height:auto — setting explicit dimensions avoids that.
    """
    aspect = px_w / px_h if px_h else 1.0
    w_mm = _MAX_DIAGRAM_W_MM
    h_mm = w_mm / aspect
    if h_mm > _MAX_DIAGRAM_H_MM:
        h_mm = _MAX_DIAGRAM_H_MM
        w_mm = h_mm * aspect
    return w_mm, h_mm


def _render_mermaid(source: str) -> str | None:
    """
    Render a Mermaid diagram to a PNG via mmdc and return an <img> tag with a
    base64 data URI.  PNG avoids WeasyPrint's inline-SVG font rendering issues
    where <text> elements go missing due to unresolvable font references.
    Returns None on failure (fallback code block used instead).
    """
    global _MMDC_PRESENT
    if _MMDC_PRESENT is None:
        _MMDC_PRESENT = _mmdc_available()
        if not _MMDC_PRESENT:
            print("  [warn] mmdc not found — Mermaid diagrams will render as code blocks")
    if not _MMDC_PRESENT:
        return None

    with tempfile.TemporaryDirectory() as tmpdir:
        in_path  = Path(tmpdir) / "diagram.mmd"
        out_path = Path(tmpdir) / "diagram.png"
        cfg_path = Path(tmpdir) / "puppeteer.json"

        in_path.write_text(source, encoding="utf-8")
        # --no-sandbox and --disable-setuid-sandbox are required in GitHub Actions
        # (and other container environments) where the runner process lacks the
        # Linux user-namespace privileges that Chromium's sandbox depends on.
        # This is safe here because the Mermaid source comes from files inside
        # the repository — it is not arbitrary untrusted web content.
        cfg_path.write_text(json.dumps({"args": ["--no-sandbox", "--disable-setuid-sandbox"]}))

        try:
            result = subprocess.run(
                ["mmdc",
                 "-i", str(in_path),
                 "-o", str(out_path),
                 "--puppeteerConfigFile", str(cfg_path),
                 "-w", "1600",            # high-res render; display size set via inline style
                 "--backgroundColor", "white"],
                capture_output=True,
                timeout=60,
            )
        except subprocess.SubprocessError as e:
            print(f"  [warn] mmdc failed: {e}")
            return None

        # mmdc occasionally adds a -1 suffix (e.g. diagram-1.png)
        if not out_path.exists():
            alt = out_path.parent / f"{out_path.stem}-1{out_path.suffix}"
            if alt.exists():
                out_path = alt

        if result.returncode != 0 or not out_path.exists():
            print(f"  [warn] mmdc error: {result.stderr.decode('utf-8', errors='replace').strip()}")
            return None

        px_w, px_h   = _png_size(out_path)
        w_mm, h_mm   = _diagram_display_size(px_w, px_h)
        data         = _b64.b64encode(out_path.read_bytes()).decode()

    # Inline width/height bypass WeasyPrint's broken max-width+max-height+height:auto
    # aspect-ratio resolution — explicit dimensions are always honoured correctly.
    style = f"width:{w_mm:.1f}mm;height:{h_mm:.1f}mm"
    return f'<img src="data:image/png;base64,{data}" class="mermaid-img" style="{style}" alt="Diagram">'


def extract_mermaid_blocks(text: str) -> tuple[str, dict[str, str]]:
    """
    Replace ```mermaid blocks with unique placeholders before markdown conversion,
    returning the modified text and a map of placeholder → rendered HTML.
    Placeholders survive markdown conversion as bare <p> text nodes.
    """
    placeholders: dict[str, str] = {}
    counter = 0

    def replace(match: re.Match) -> str:
        nonlocal counter
        source = match.group(1).strip()
        key = f"MERMAID_BLOCK_{counter}_END"
        counter += 1
        rendered = _render_mermaid(source)
        if rendered:
            placeholders[key] = f'<div class="mermaid-diagram">{rendered}</div>'
        else:
            escaped = _html.escape(source)
            placeholders[key] = (
                f'<div class="mermaid-fallback">'
                f'<p class="mermaid-fallback-label">Diagram (mmdc unavailable)</p>'
                f'<pre><code>{escaped}</code></pre></div>'
            )
        return f"\n\n{key}\n\n"

    modified = re.sub(r"```mermaid[ \t]*\n(.*?)\n[ \t]*```", replace, text, flags=re.DOTALL)
    return modified, placeholders


def inject_mermaid(html: str, placeholders: dict[str, str]) -> str:
    """Substitute mermaid placeholders back into converted HTML."""
    for key, rendered in placeholders.items():
        html = html.replace(f"<p>{key}</p>", rendered)
        html = html.replace(key, rendered)  # fallback if not wrapped in <p>
    return html


def build_html(files: list[Path], title: str, meta: str,
               author: str = "", nofront: bool = False,
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
        raw, mermaid_map = extract_mermaid_blocks(raw)
        body = md.convert(raw)
        body = inject_mermaid(body, mermaid_map)
        md.reset()

        # Fail fast if any mermaid block slipped through unextracted.
        # fenced_code marks un-extracted blocks with class="language-mermaid".
        leaked = body.count('language-mermaid')
        if leaked:
            raise RuntimeError(
                f"{leaked} mermaid block(s) in {path.name} were not extracted "
                f"before markdown conversion — they will render as raw text. "
                f"Check extract_mermaid_blocks() regex."
            )

        extra_class = " first-section" if i == 0 else ""
        sections.append(f'<section class="doc-section{extra_class}">{body}</section>')

    safe_title  = _html.escape(title)
    safe_meta   = _html.escape(meta)
    safe_author = _html.escape(author)

    if nofront:
        cover = ""
    else:
        author_line = f'\n    <p class="cover-author">{safe_author}</p>' if safe_author else ""
        cover = f"""
<div class="cover-page">
  <div class="cover-inner">
    <p class="cover-eyebrow">M&amp;A Operating System</p>
    <p class="cover-category">Product Design</p>
    <h1 class="cover-title">{safe_title}</h1>
    <hr class="cover-rule">
    <p class="cover-meta">{safe_meta}</p>{author_line}
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
    size: letter;
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
    min-height: 279.4mm;
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
.cover-author { font-size: 9pt; color: #9ca3af; margin: 4pt 0 0 0; }

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

/* Mermaid diagrams */
.mermaid-diagram {
    margin: 4mm 0;
    page-break-inside: avoid;
    text-align: center;
}
.mermaid-img {
    /* width and height are set inline by generate_pdf.py from PNG intrinsic
       dimensions — WeasyPrint does not correctly resolve aspect ratio when
       max-width, max-height, and height:auto are all active simultaneously. */
    display: block;
    margin: 0 auto;
}
.mermaid-fallback {
    background-color: #f9fafb;
    border: 1px dashed #d1d5db;
    border-radius: 3pt;
    padding: 6pt 10pt;
    margin: 4mm 0;
}
.mermaid-fallback-label {
    font-size: 7.5pt;
    color: #9ca3af;
    margin: 0 0 2mm;
    font-style: italic;
}
"""

# ---------- per-product generation ----------

def generate_product(name: str, config: dict, nofront: bool = False) -> None:
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
                      author=config.get("author", ""),
                      nofront=nofront,
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


def generate_page(file_path: Path, nofront: bool = False) -> None:
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
    html = build_html([file_path], page_title, config["meta"],
                      author=config.get("author", ""),
                      nofront=nofront)

    print("Rendering PDF…")
    from weasyprint import HTML, CSS as WeasyprintCSS
    HTML(string=html, base_url=str(file_path.parent)).write_pdf(
        str(output),
        stylesheets=[WeasyprintCSS(string=CSS)],
    )

    size_mb = output.stat().st_size / 1_000_000
    print(f"Done → {output}  ({size_mb:.1f} MB)")

    # Publish the output path for GitHub Actions step chaining
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        gop = Path(github_output)
        if not gop.is_absolute() or ".." in gop.parts:
            print(f"  [warn] GITHUB_OUTPUT path looks unsafe, skipping: {github_output}")
        else:
            repo_root = Path(__file__).parent
            with open(gop, "a") as f:
                f.write(f"pdf_path={output.relative_to(repo_root)}\n")

# ---------- pages-subset generation ----------

def generate_pages(product_name: str, page_prefixes: list[str],
                   out_name: str | None, nofront: bool = False) -> None:
    """Generate a merged PDF from a subset of chapters, in the order given."""
    config = PRODUCTS[product_name]
    docs_dir = PRODUCTS_DIR / product_name

    files: list[Path] = []
    missing: list[str] = []
    for prefix in page_prefixes:
        matches = sorted(docs_dir.glob(f"{prefix}-*.md"))
        matches = [m for m in matches if "-ignore" not in m.stem and m.name not in EXCLUDE]
        if not matches:
            missing.append(prefix)
        else:
            if matches[0].is_symlink():
                print(f"  [error] symlinks are not supported: {matches[0].name}")
                sys.exit(1)
            if len(matches) > 1:
                print(f"  [warn] prefix '{prefix}' matched {len(matches)} files — using {matches[0].name}")
            files.append(matches[0])

    if missing:
        print(f"  [error] no chapter file found for prefix(es): {', '.join(missing)}")
        print(f"          Available chapters in '{product_name}':")
        for f in sorted(docs_dir.glob("[0-9][0-9]-*.md")):
            if "-ignore" not in f.stem:
                print(f"    {f.stem[:2]}  ({f.name})")
        sys.exit(1)

    if out_name:
        output = docs_dir / out_name
    elif len(page_prefixes) == 1:
        output = files[0].with_suffix('.pdf')
    else:
        label = "_".join(page_prefixes)
        output = docs_dir / f"{product_name}_pages_{label}.pdf"

    print(f"\n── {product_name} pages: {', '.join(page_prefixes)} ──────────────────────────────")
    print(f"Documents ({len(files)}):")
    for f in files:
        print(f"  {f.name}")

    print("Building HTML…")
    html = build_html(files, config["title"], config["meta"],
                      author=config.get("author", ""),
                      nofront=nofront,
                      subs={"{{PRODUCT_NAME}}": product_name})

    print("Rendering PDF…")
    from weasyprint import HTML as WeasyprintHTML, CSS as WeasyprintCSS
    WeasyprintHTML(string=html, base_url=str(docs_dir)).write_pdf(
        str(output),
        stylesheets=[WeasyprintCSS(string=CSS)],
    )

    size_mb = output.stat().st_size / 1_000_000
    print(f"Done → {output}  ({size_mb:.1f} MB)")

    # Publish the output path for GitHub Actions step chaining (single-chapter only,
    # matching the behaviour of generate_page() for the --page flag).
    if len(page_prefixes) == 1 and out_name is None:
        github_output = os.environ.get("GITHUB_OUTPUT")
        if github_output:
            gop = Path(github_output)
            if not gop.is_absolute() or ".." in gop.parts:
                print(f"  [warn] GITHUB_OUTPUT path looks unsafe, skipping: {github_output}")
            else:
                repo_root = Path(__file__).parent
                with open(gop, "a") as f:
                    f.write(f"pdf_path={output.relative_to(repo_root)}\n")


# ---------- main ----------

def main():
    try:
        from weasyprint import HTML  # noqa: F401
    except ImportError:
        print("weasyprint not installed. Run: pip install markdown weasyprint")
        sys.exit(1)

    args = sys.argv[1:]
    nofront = "--nofront" in args
    args = [a for a in args if a != "--nofront"]

    # --page <file>
    if args and args[0] == '--page':
        if len(args) < 2:
            print("Usage: python generate_pdf.py --page <path/to/file.md> [--nofront]")
            sys.exit(1)
        generate_page(Path(args[1]), nofront=nofront)
        print("\nAll done.")
        return

    # Extract --product, --pages, --out from args
    product_flag: str | None = None
    pages_flag: list[str] = []
    out_flag: str | None = None

    i = 0
    positional: list[str] = []
    while i < len(args):
        if args[i] == "--product":
            if i + 1 >= len(args):
                print("  [error] --product requires a value")
                sys.exit(1)
            product_flag = args[i + 1]
            i += 2
        elif args[i] == "--pages":
            i += 1
            while i < len(args) and not args[i].startswith("--"):
                pages_flag.append(args[i])
                i += 1
        elif args[i] == "--out":
            if i + 1 >= len(args):
                print("  [error] --out requires a filename")
                sys.exit(1)
            out_flag = args[i + 1]
            i += 2
        else:
            positional.append(args[i])
            i += 1

    if positional:
        print(f"  [error] unexpected positional argument(s): {' '.join(positional)}")
        print(f"          Use --product <name> to select a product.")
        sys.exit(1)

    # --pages mode: needs --product
    if pages_flag:
        if not product_flag:
            print("  [error] --pages requires --product <name>")
            sys.exit(1)
        if product_flag not in PRODUCTS:
            print(f"  [error] unknown product '{product_flag}'. Available: {', '.join(PRODUCTS)}")
            sys.exit(1)
        # validate prefix format (exactly two digits)
        bad = [p for p in pages_flag if not re.fullmatch(r"\d{2}", p)]
        if bad:
            print(f"  [error] page prefixes must be two digits (e.g. 02 04 08), got: {', '.join(bad)}")
            sys.exit(1)
        generate_pages(product_flag, pages_flag, out_flag, nofront=nofront)
        print("\nAll done.")
        return

    # Normal product generation
    if product_flag:
        if product_flag not in PRODUCTS:
            print(f"Unknown product '{product_flag}'. Available: {', '.join(PRODUCTS)}")
            sys.exit(1)
        targets = {product_flag: PRODUCTS[product_flag]}
    else:
        targets = PRODUCTS

    for name, config in targets.items():
        generate_product(name, config, nofront=nofront)

    print("\nAll done.")


if __name__ == "__main__":
    main()
