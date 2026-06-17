"""
Generates two-card raw vs rendered preview PNGs for each AI Chat Platform
content renderer type. Each PNG shows two separate UI component cards side
by side — the left card in Raw state, the right card in Rendered state.
Run: python3 generate_renderer_preview.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

# ── Paths ──────────────────────────────────────────────────────────────────
OUT_DIR   = os.path.join(os.path.dirname(__file__), "renderer-previews")
SANS      = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
MONO      = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Palette ────────────────────────────────────────────────────────────────
WHITE       = (255, 255, 255)
CANVAS_BG   = (242, 244, 247)
CARD_BG     = (255, 255, 255)
BORDER      = (218, 220, 224)
HEADER_BG   = (250, 251, 252)
TEXT_DARK   = ( 32,  33,  36)
TEXT_MID    = ( 95,  99, 104)
TEXT_LIGHT  = (154, 160, 166)
CODE_BG     = ( 30,  31,  41)
CODE_TEXT   = (248, 248, 242)
CODE_PINK   = (255, 121, 198)
CODE_YELLOW = (241, 250, 140)
CODE_CYAN   = (139, 233, 253)
CODE_GREEN  = ( 80, 250, 123)
CODE_PURPLE = (189, 147, 249)
CODE_ORANGE = (255, 184, 108)
NODE_FILL   = (232, 240, 254)
NODE_BORDER = ( 66, 133, 244)
ARROW_COL   = (100, 116, 139)
# Pill — Raw active state
PILL_RAW_ACTIVE   = ( 32,  33,  36)   # dark chip on right
PILL_REND_ACTIVE  = ( 66, 133, 244)   # blue chip on left
PILL_IDLE         = (241, 243, 244)
PILL_BORDER       = (218, 220, 224)
PILL_ON_TEXT      = (255, 255, 255)
PILL_OFF_TEXT     = ( 95,  99, 104)
LABEL_BG_RAW      = (241, 243, 244)
LABEL_BG_REND     = (232, 240, 254)
LABEL_TEXT_RAW    = ( 95,  99, 104)
LABEL_TEXT_REND   = ( 26,  86, 219)

# ── Fonts ──────────────────────────────────────────────────────────────────
def fnt(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

F_UI      = lambda s: fnt(SANS,      s)
F_BOLD    = lambda s: fnt(SANS_BOLD, s)
F_MONO    = lambda s: fnt(MONO,      s)

# ── Drawing primitives ─────────────────────────────────────────────────────
def rrect(draw, xy, r, fill=None, outline=None, lw=1):
    x0, y0, x1, y1 = xy
    if fill:
        draw.rectangle([x0+r, y0, x1-r, y1], fill=fill)
        draw.rectangle([x0, y0+r, x1, y1-r], fill=fill)
        for ex, ey in [(x0,y0),(x1-2*r,y0),(x0,y1-2*r),(x1-2*r,y1-2*r)]:
            draw.ellipse([ex, ey, ex+2*r, ey+2*r], fill=fill)
    if outline:
        draw.arc([x0,y0,x0+2*r,y0+2*r], 180, 270, fill=outline, width=lw)
        draw.arc([x1-2*r,y0,x1,y0+2*r], 270, 360, fill=outline, width=lw)
        draw.arc([x0,y1-2*r,x0+2*r,y1],  90, 180, fill=outline, width=lw)
        draw.arc([x1-2*r,y1-2*r,x1,y1],   0,  90, fill=outline, width=lw)
        draw.line([x0+r,y0,x1-r,y0], fill=outline, width=lw)
        draw.line([x0+r,y1,x1-r,y1], fill=outline, width=lw)
        draw.line([x0,y0+r,x0,y1-r], fill=outline, width=lw)
        draw.line([x1,y0+r,x1,y1-r], fill=outline, width=lw)

def text_w(draw, text, font):
    bb = font.getbbox(text)
    return bb[2] - bb[0]

def arrow_h(draw, x0, y, x1, color=ARROW_COL, head=8):
    if x1 <= x0: return
    draw.line([(x0, y), (x1-head, y)], fill=color, width=2)
    draw.polygon([(x1-head, y-head//2), (x1, y), (x1-head, y+head//2)], fill=color)

def arrow_v(draw, x, y0, y1, color=ARROW_COL, head=8):
    if y1 <= y0: return
    draw.line([(x, y0), (x, y1-head)], fill=color, width=2)
    draw.polygon([(x-head//2, y1-head), (x, y1), (x+head//2, y1-head)], fill=color)

def node(draw, cx, cy, w, h, label, r=6, fill=NODE_FILL, border=NODE_BORDER):
    x0, y0 = cx-w//2, cy-h//2
    rrect(draw, [x0,y0,x0+w,y0+h], r, fill=fill, outline=border, lw=2)
    f = F_BOLD(12)
    tw = text_w(draw, label, f)
    draw.text((cx-tw//2, cy-8), label, font=f, fill=TEXT_DARK)

def diamond(draw, cx, cy, w, h, label):
    pts = [(cx, cy-h//2), (cx+w//2, cy), (cx, cy+h//2), (cx-w//2, cy)]
    draw.polygon(pts, fill=NODE_FILL, outline=NODE_BORDER)
    f = F_BOLD(11)
    tw = text_w(draw, label, f)
    draw.text((cx-tw//2, cy-7), label, font=f, fill=TEXT_DARK)

# ── Card chrome ─────────────────────────────────────────────────────────────
CARD_R  = 10
HDR_H   = 44
PILL_W  = 116
PILL_H  = 26

def draw_single_card(img, x0, y0, w, h, title, active_side):
    """
    Draw one card at (x0,y0) with size (w,h).
    active_side: 'rendered' | 'raw'
    Returns (draw, content_x0, content_y0, content_x1, content_y1)
    """
    draw = ImageDraw.Draw(img)
    x1, y1 = x0+w, y0+h

    # drop shadow
    for i in range(5, 0, -1):
        rrect(draw, [x0+i, y0+i, x1+i, y1+i], CARD_R, fill=(0,0,0, 8))

    # card body
    rrect(draw, [x0,y0,x1,y1], CARD_R, fill=CARD_BG, outline=BORDER, lw=1)

    # header strip
    draw.rectangle([x0+1, y0+1, x1-1, y0+HDR_H], fill=HEADER_BG)
    draw.line([(x0, y0+HDR_H), (x1, y0+HDR_H)], fill=BORDER, width=1)

    # title
    tf = F_BOLD(13)
    draw.text((x0+16, y0+14), title, font=tf, fill=TEXT_DARK)

    # pill toggle
    px = x1 - PILL_W - 14
    py = y0 + (HDR_H - PILL_H) // 2
    hw = PILL_W // 2

    # pill background
    rrect(draw, [px, py, px+PILL_W, py+PILL_H], PILL_H//2,
          fill=PILL_IDLE, outline=PILL_BORDER, lw=1)

    pf = F_UI(11)
    if active_side == 'rendered':
        # blue left chip active
        rrect(draw, [px, py, px+hw, py+PILL_H], PILL_H//2, fill=PILL_REND_ACTIVE)
        draw.text((px+8,  py+7), "Rendered", font=pf, fill=PILL_ON_TEXT)
        draw.text((px+hw+8, py+7), "Raw",    font=pf, fill=PILL_OFF_TEXT)
    else:
        # dark right chip active
        rrect(draw, [px+hw, py, px+PILL_W, py+PILL_H], PILL_H//2, fill=PILL_RAW_ACTIVE)
        draw.text((px+8,  py+7), "Rendered", font=pf, fill=PILL_OFF_TEXT)
        draw.text((px+hw+8, py+7), "Raw",    font=pf, fill=PILL_ON_TEXT)

    # state label badge below header
    label_text  = "Rendered" if active_side == 'rendered' else "Raw"
    label_fill  = LABEL_BG_REND  if active_side == 'rendered' else LABEL_BG_RAW
    label_color = LABEL_TEXT_REND if active_side == 'rendered' else LABEL_TEXT_RAW
    lf = F_UI(10)
    lw = text_w(draw, label_text, lf) + 16
    lx = x0 + 14
    ly = y0 + HDR_H + 10
    rrect(draw, [lx, ly, lx+lw, ly+18], 4, fill=label_fill)
    draw.text((lx+8, ly+4), label_text, font=lf, fill=label_color)

    cy0 = y0 + HDR_H + 36   # content starts below badge
    return draw, x0, cy0, x1, y1

def make_frame(card_w, card_h, gap=40, margin=32):
    """Canvas holding two cards side by side."""
    W = margin*2 + card_w*2 + gap
    H = margin*2 + card_h
    img = Image.new("RGB", (W, H), CANVAS_BG)
    return img, W, H, margin, margin

def code_panel(draw, x0, y0, x1, y1, lines, corner_r=0):
    """Dark syntax-coloured code area."""
    draw.rectangle([x0, y0, x1, y1], fill=CODE_BG)
    lf = F_MONO(12)
    lh = 19
    px, py = 18, 16
    for i, (txt, col) in enumerate(lines):
        draw.text((x0+px, y0+py+i*lh), txt, font=lf, fill=col)

# ═══════════════════════════════════════════════════════════════════════════
#  01 — MERMAID
# ═══════════════════════════════════════════════════════════════════════════
def make_mermaid():
    CW, CH = 420, 320
    img, W, H, mx, my = make_frame(CW, CH)

    # ── Raw card ──────────────────────────────────────────────────────────
    d, x0, cy0, x1, cy1 = draw_single_card(img, mx, my, CW, CH, "Mermaid Diagram", "raw")
    code_panel(d, x0+1, cy0, x1-1, cy1-1, [
        ("```mermaid",            CODE_TEXT),
        ("flowchart LR",          CODE_PINK),
        ("",                      CODE_TEXT),
        ("    A[Data Sources]",   CODE_CYAN),
        ("    B[Transform]",      CODE_CYAN),
        ("    C[Output]",         CODE_CYAN),
        ("",                      CODE_TEXT),
        ("    A --> B --> C",     CODE_YELLOW),
        ("```",                   CODE_TEXT),
    ])

    # ── Rendered card ─────────────────────────────────────────────────────
    rx = mx + CW + 40
    d2, rx0, rcy0, rx1, rcy1 = draw_single_card(img, rx, my, CW, CH, "Mermaid Diagram", "rendered")
    d2.rectangle([rx0+1, rcy0, rx1-1, rcy1-1], fill=WHITE)

    pcx = (rx0 + rx1) // 2
    pcy = (rcy0 + rcy1) // 2
    nw, nh, gap = 104, 38, 44
    n1x = pcx - nw - gap
    n2x = pcx
    n3x = pcx + nw + gap
    for nx, lbl in [(n1x,"Data Sources"),(n2x,"Transform"),(n3x,"Output")]:
        node(d2, nx, pcy, nw, nh, lbl)
    arrow_h(d2, n1x+nw//2, pcy, n2x-nw//2)
    arrow_h(d2, n2x+nw//2, pcy, n3x-nw//2)

    return img

# ── Run ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    renders = {"01-mermaid": make_mermaid}
    for name, fn in renders.items():
        path = os.path.join(OUT_DIR, f"{name}.png")
        fn().save(path)
        print(f"  ✓  {path}")
