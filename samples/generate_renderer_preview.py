"""
Generates side-by-side raw vs rendered preview PNGs for each AI Chat Platform
content renderer type. Run: python3 generate_renderer_preview.py
"""

from PIL import Image, ImageDraw, ImageFont
import os, math

# ── Paths ──────────────────────────────────────────────────────────────────
OUT_DIR   = os.path.join(os.path.dirname(__file__), "renderer-previews")
SANS      = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
MONO      = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Palette ────────────────────────────────────────────────────────────────
WHITE        = (255, 255, 255)
CANVAS_BG    = (248, 249, 250)
CARD_BG      = (255, 255, 255)
BORDER       = (218, 220, 224)
DIVIDER      = (218, 220, 224)
HEADER_BG    = (250, 251, 252)
TEXT_DARK    = ( 32,  33,  36)
TEXT_MID     = ( 95,  99, 104)
TEXT_LIGHT   = (154, 160, 166)
CODE_BG      = ( 30,  31,  41)
CODE_TEXT    = (248, 248, 242)
CODE_PINK    = (255, 121, 198)
CODE_YELLOW  = (241, 250, 140)
CODE_GREEN   = ( 80, 250, 123)
CODE_PURPLE  = (189, 147, 249)
CODE_CYAN    = (139, 233, 253)
CODE_ORANGE  = (255, 184, 108)
NODE_FILL    = (232, 240, 254)
NODE_BORDER  = ( 66, 133, 244)
NODE_TEXT    = ( 32,  33,  36)
ARROW        = (100, 116, 139)
PILL_ACTIVE  = ( 32,  33,  36)
PILL_IDLE    = (241, 243, 244)
PILL_AT      = (255, 255, 255)
PILL_IT      = ( 95,  99, 104)
LABEL_RENDERED = ( 66, 133, 244)

# ── Font loader ─────────────────────────────────────────────────────────────
def fnt(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

# ── Drawing helpers ─────────────────────────────────────────────────────────
def rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
    x0, y0, x1, y1 = xy
    r = radius
    if fill:
        draw.rectangle([x0+r, y0, x1-r, y1], fill=fill)
        draw.rectangle([x0, y0+r, x1, y1-r], fill=fill)
        draw.ellipse([x0, y0, x0+2*r, y0+2*r], fill=fill)
        draw.ellipse([x1-2*r, y0, x1, y0+2*r], fill=fill)
        draw.ellipse([x0, y1-2*r, x0+2*r, y1], fill=fill)
        draw.ellipse([x1-2*r, y1-2*r, x1, y1], fill=fill)
    if outline:
        draw.arc([x0, y0, x0+2*r, y0+2*r], 180, 270, fill=outline, width=width)
        draw.arc([x1-2*r, y0, x1, y0+2*r], 270, 360, fill=outline, width=width)
        draw.arc([x0, y1-2*r, x0+2*r, y1], 90, 180, fill=outline, width=width)
        draw.arc([x1-2*r, y1-2*r, x1, y1], 0, 90, fill=outline, width=width)
        draw.line([x0+r, y0, x1-r, y0], fill=outline, width=width)
        draw.line([x0+r, y1, x1-r, y1], fill=outline, width=width)
        draw.line([x0, y0+r, x0, y1-r], fill=outline, width=width)
        draw.line([x1, y0+r, x1, y1-r], fill=outline, width=width)

def draw_card(draw, img_w, img_h, title, label_rendered="Rendered", label_raw="Raw"):
    """Draw the outer card chrome — header, divider, pill toggle. Returns content area."""
    M = 24           # outer margin
    CARD_R = 10
    HDR_H = 44
    # shadow
    shadow = Image.new("RGBA", (img_w, img_h), (0,0,0,0))
    sd = ImageDraw.Draw(shadow)
    for i in range(6, 0, -1):
        sd.rounded_rectangle([M+i, M+i, img_w-M+i, img_h-M+i],
                              radius=CARD_R, fill=(0,0,0, 6))
    img_base = Image.new("RGB", (img_w, img_h), CANVAS_BG)
    img_base.paste(Image.alpha_composite(img_base.convert("RGBA"), shadow).convert("RGB"))
    draw2 = ImageDraw.Draw(img_base)

    # card body
    rounded_rect(draw2, [M, M, img_w-M, img_h-M], CARD_R, fill=CARD_BG, outline=BORDER, width=1)
    # header strip
    draw2.rectangle([M+1, M+1, img_w-M-1, M+HDR_H], fill=HEADER_BG)
    draw2.line([(M, M+HDR_H), (img_w-M, M+HDR_H)], fill=BORDER, width=1)

    # title
    tf = fnt(SANS_BOLD, 13)
    draw2.text((M+16, M+14), title, font=tf, fill=TEXT_DARK)

    # pill toggle — top right of header
    pill_x = img_w - M - 120
    pill_y = M + 10
    pill_w = 110
    pill_h = 24
    pill_r = 12
    # pill background
    rounded_rect(draw2, [pill_x, pill_y, pill_x+pill_w, pill_y+pill_h], pill_r,
                 fill=PILL_IDLE, outline=BORDER, width=1)
    # active half (Rendered)
    half_w = pill_w // 2
    rounded_rect(draw2, [pill_x, pill_y, pill_x+half_w, pill_y+pill_h], pill_r,
                 fill=PILL_ACTIVE)
    # pill labels
    pf = fnt(SANS, 11)
    draw2.text((pill_x + 10, pill_y + 6), label_rendered, font=pf, fill=PILL_AT)
    draw2.text((pill_x + half_w + 8, pill_y + 6), label_raw, font=pf, fill=PILL_IT)

    # content area
    content_y = M + HDR_H + 1
    return img_base, draw2, M, content_y, img_w - M, img_h - M

def draw_vertical_divider(draw, x, y0, y1):
    draw.line([(x, y0), (x, y1)], fill=DIVIDER, width=1)

def draw_section_label(draw, x, y, text, color=TEXT_LIGHT):
    f = fnt(SANS, 10)
    draw.text((x, y), text, font=f, fill=color)

def draw_code_panel(draw, x0, y0, x1, y1, lines):
    """Dark code panel with coloured token lines."""
    draw.rectangle([x0, y0, x1, y1], fill=CODE_BG)
    lf = fnt(MONO, 12)
    lh = 18
    pad_x, pad_y = 16, 14
    for i, (text, color) in enumerate(lines):
        draw.text((x0 + pad_x, y0 + pad_y + i * lh), text, font=lf, fill=color)

def arrow_right(draw, x0, y, x1, color=ARROW, head=7):
    draw.line([(x0, y), (x1 - head, y)], fill=color, width=2)
    draw.polygon([(x1-head, y-head//2), (x1, y), (x1-head, y+head//2)], fill=color)

def draw_node(draw, cx, cy, w, h, label, r=6):
    x0, y0 = cx - w//2, cy - h//2
    rounded_rect(draw, [x0, y0, x0+w, y0+h], r, fill=NODE_FILL, outline=NODE_BORDER, width=2)
    nf = fnt(SANS_BOLD, 13)
    bbox = nf.getbbox(label)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw//2, cy - 8), label, font=nf, fill=NODE_TEXT)

# ═══════════════════════════════════════════════════════════════════════════
#  MERMAID
# ═══════════════════════════════════════════════════════════════════════════
def make_mermaid():
    W, H = 860, 340
    img = Image.new("RGB", (W, H), CANVAS_BG)
    draw = ImageDraw.Draw(img)

    img, draw, cx0, cy0, cx1, cy1 = draw_card(draw, W, H, "Mermaid Diagram")

    mid_x = (cx0 + cx1) // 2

    # ── Left: raw code panel ──────────────────────────────────────────────
    draw_code_panel(draw, cx0, cy0, mid_x, cy1, [
        ("```mermaid",                      CODE_TEXT),
        ("flowchart LR",                    CODE_PINK),
        ("",                                CODE_TEXT),
        ("    A[Data Sources]",             CODE_CYAN),
        ("    B[Transform]",                CODE_CYAN),
        ("    C[Output]",                   CODE_CYAN),
        ("",                                CODE_TEXT),
        ("    A --> B --> C",               CODE_YELLOW),
        ("```",                             CODE_TEXT),
    ])
    draw_section_label(draw, cx0 + 16, cy1 - 22, "RAW SOURCE", TEXT_LIGHT)

    # ── Divider ───────────────────────────────────────────────────────────
    draw_vertical_divider(draw, mid_x, cy0, cy1)

    # ── Right: rendered flowchart ─────────────────────────────────────────
    rx0, ry0, rx1, ry1 = mid_x + 1, cy0, cx1, cy1
    draw.rectangle([rx0, ry0, rx1, ry1], fill=WHITE)

    panel_cx = (rx0 + rx1) // 2
    panel_cy = (ry0 + ry1) // 2
    node_w, node_h = 110, 42
    gap = 52

    n1x = panel_cx - node_w - gap
    n2x = panel_cx
    n3x = panel_cx + node_w + gap

    draw_node(draw, n1x, panel_cy, node_w, node_h, "Data Sources")
    draw_node(draw, n2x, panel_cy, node_w, node_h, "Transform")
    draw_node(draw, n3x, panel_cy, node_w, node_h, "Output")

    arrow_right(draw, n1x + node_w//2, panel_cy, n2x - node_w//2)
    arrow_right(draw, n2x + node_w//2, panel_cy, n3x - node_w//2)

    draw_section_label(draw, rx0 + 16, cy1 - 22, "RENDERED — SVG via Mermaid.js", TEXT_LIGHT)

    return img

# ── Run ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    renders = {
        "01-mermaid": make_mermaid,
    }
    for name, fn in renders.items():
        path = os.path.join(OUT_DIR, f"{name}.png")
        fn().save(path)
        print(f"  ✓  {path}")
