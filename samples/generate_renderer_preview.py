"""
Renderer preview PNGs — inline chat thread mockups, corporate SaaS styling.
Two panels per image: Raw (left) · Rendered (right).
Run: python3 generate_renderer_preview.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT_DIR   = os.path.join(os.path.dirname(__file__), "renderer-previews")
SANS      = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
MONO      = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
os.makedirs(OUT_DIR, exist_ok=True)

# ── Palette — corporate SaaS ───────────────────────────────────────────────
WHITE         = (255, 255, 255)
THREAD_BG     = (250, 250, 251)       # very light warm gray page bg
CARD_BG       = (255, 255, 255)
CARD_HDR      = (248, 249, 250)       # barely-there header tint
BORDER        = (229, 231, 235)       # E5E7EB
DIVIDER       = (243, 244, 246)       # lighter internal divider
TEXT_PRIMARY  = ( 17,  24,  39)       # near-black
TEXT_SECONDARY= ( 75,  85,  99)       # slate-600
TEXT_TERTIARY = (156, 163, 175)       # slate-400
AVATAR_USER   = (124,  58, 237)       # violet-600
AVATAR_ASST   = ( 16, 185, 129)       # emerald-500
CODE_BG       = ( 22,  27,  34)       # GitHub dark
CODE_TEXT     = (201, 209, 217)
CODE_BLUE     = (121, 192, 255)
CODE_GREEN    = (122, 201, 137)
CODE_ORANGE   = (255, 166,  87)
CODE_PURPLE   = (210, 168, 255)
CODE_YELLOW   = (230, 192, 123)
NODE_FILL     = (239, 246, 255)       # blue-50
NODE_BORDER   = ( 96, 165, 250)       # blue-400
ARROW_COL     = (148, 163, 184)       # slate-400
PILL_REND_BG  = ( 37,  99, 235)       # blue-600 — rendered active
PILL_RAW_BG   = ( 31,  41,  55)       # slate-800 — raw active
PILL_IDLE     = (243, 244, 246)
PILL_BORDER   = (209, 213, 219)
PILL_ON       = (255, 255, 255)
PILL_OFF      = (107, 114, 128)
BADGE_REND_BG = (239, 246, 255)
BADGE_REND_TX = ( 29,  78, 216)
BADGE_RAW_BG  = (243, 244, 246)
BADGE_RAW_TX  = ( 75,  85,  99)

# ── Fonts ──────────────────────────────────────────────────────────────────
def fnt(path, size):
    try:   return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()

UI    = lambda s: fnt(SANS,      s)
BOLD  = lambda s: fnt(SANS_BOLD, s)
MONO_ = lambda s: fnt(MONO,      s)

def twidth(text, font):
    bb = font.getbbox(text)
    return bb[2] - bb[0]

# ── Primitives ─────────────────────────────────────────────────────────────
def rrect(draw, xy, r, fill=None, outline=None, lw=1):
    x0, y0, x1, y1 = xy
    if fill:
        draw.rectangle([x0+r, y0, x1-r, y1], fill=fill)
        draw.rectangle([x0, y0+r, x1, y1-r], fill=fill)
        for ex, ey in [(x0,y0),(x1-2*r,y0),(x0,y1-2*r),(x1-2*r,y1-2*r)]:
            draw.ellipse([ex, ey, ex+2*r, ey+2*r], fill=fill)
    if outline:
        for a0,a1,ex,ey in [(180,270,x0,y0),(270,360,x1-2*r,y0),
                             (90,180,x0,y1-2*r),(0,90,x1-2*r,y1-2*r)]:
            draw.arc([ex, ey, ex+2*r, ey+2*r], a0, a1, fill=outline, width=lw)
        draw.line([x0+r,y0,x1-r,y0], fill=outline, width=lw)
        draw.line([x0+r,y1,x1-r,y1], fill=outline, width=lw)
        draw.line([x0,y0+r,x0,y1-r], fill=outline, width=lw)
        draw.line([x1,y0+r,x1,y1-r], fill=outline, width=lw)

def avatar(draw, cx, cy, r, color, initial):
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=color)
    f = BOLD(r)
    iw = twidth(initial, f)
    draw.text((cx - iw//2, cy - r//2), initial, font=f, fill=WHITE)

def wrapped_lines(text, max_w, font):
    words = text.split()
    lines, line = [], []
    for w in words:
        test = ' '.join(line + [w])
        if twidth(test, font) <= max_w:
            line.append(w)
        else:
            if line: lines.append(' '.join(line))
            line = [w]
    if line: lines.append(' '.join(line))
    return lines

def draw_wrapped(draw, text, x, y, max_w, font, color, lh=20):
    for i, line in enumerate(wrapped_lines(text, max_w, font)):
        draw.text((x, y + i*lh), line, font=font, fill=color)
    return y + len(wrapped_lines(text, max_w, font)) * lh

def arrow_h(draw, x0, y, x1, color=ARROW_COL, head=7):
    if x1 <= x0 + head: return
    draw.line([(x0,y),(x1-head,y)], fill=color, width=2)
    draw.polygon([(x1-head,y-4),(x1,y),(x1-head,y+4)], fill=color)

def node(draw, cx, cy, w, h, label, r=5):
    x0, y0 = cx-w//2, cy-h//2
    rrect(draw, [x0,y0,x0+w,y0+h], r, fill=NODE_FILL, outline=NODE_BORDER, lw=1)
    f = BOLD(12)
    iw = twidth(label, f)
    draw.text((cx - iw//2, cy-7), label, font=f, fill=TEXT_PRIMARY)

# ── Card chrome ────────────────────────────────────────────────────────────
HDR_H  = 44
PILL_W = 120
PILL_H = 26
CARD_R = 6
CARD_INNER_PAD = 20     # padding inside card content area

def render_card(draw, img, x0, y0, card_w, title, active_side, content_fn):
    """
    Draw a renderer card. content_fn(draw, cx0, cy0, cx1, cy1, measure)
    draws content or returns required height when measure=True.
    Returns bottom y.
    """
    content_h = content_fn(None, 0, 0, card_w - CARD_INNER_PAD*2, 0, measure=True)
    total_h = HDR_H + CARD_INNER_PAD + content_h + CARD_INNER_PAD
    x1, y1 = x0 + card_w, y0 + total_h

    # card — no shadow, clean border only
    rrect(draw, [x0, y0, x1, y1], CARD_R, fill=CARD_BG, outline=BORDER, lw=1)

    # header strip
    draw.rectangle([x0+1, y0+1, x1-1, y0+HDR_H], fill=CARD_HDR)
    draw.line([(x0+1, y0+HDR_H), (x1-1, y0+HDR_H)], fill=BORDER, width=1)

    # title
    draw.text((x0+16, y0+14), title, font=BOLD(13), fill=TEXT_PRIMARY)

    # pill toggle
    px = x1 - PILL_W - 12
    py = y0 + (HDR_H - PILL_H) // 2
    hw = PILL_W // 2
    rrect(draw, [px, py, px+PILL_W, py+PILL_H], PILL_H//2,
          fill=PILL_IDLE, outline=PILL_BORDER, lw=1)
    pf = UI(11)
    if active_side == 'rendered':
        rrect(draw, [px, py, px+hw, py+PILL_H], PILL_H//2, fill=PILL_REND_BG)
        draw.text((px+8,  py+7), "Rendered", font=pf, fill=PILL_ON)
        draw.text((px+hw+8, py+7), "Raw",    font=pf, fill=PILL_OFF)
    else:
        rrect(draw, [px+hw, py, px+PILL_W, py+PILL_H], PILL_H//2, fill=PILL_RAW_BG)
        draw.text((px+8,  py+7), "Rendered", font=pf, fill=PILL_OFF)
        draw.text((px+hw+8, py+7), "Raw",    font=pf, fill=PILL_ON)

    # content
    cx0 = x0 + CARD_INNER_PAD
    cy0 = y0 + HDR_H + CARD_INNER_PAD
    cx1 = x1 - CARD_INNER_PAD
    cy1 = y1 - CARD_INNER_PAD
    content_fn(draw, cx0, cy0, cx1, cy1, measure=False)

    return y1

# ── Thread layout ──────────────────────────────────────────────────────────
AV_R       = 15
AV_MARGIN  = 20
MSG_LEFT   = AV_MARGIN + AV_R*2 + 14
MSG_PAD    = 24          # right padding
ROW_GAP    = 28          # gap between user and assistant rows
CARD_MT    = 16          # margin above card

def paint_thread(img, tx, ty, panel_w,
                 user_text, asst_text, card_title, active_side, content_fn):
    draw = ImageDraw.Draw(img)
    y = ty
    msg_w = panel_w - MSG_LEFT - MSG_PAD

    # ── User turn ─────────────────────────────────────────────────────────
    avatar(draw, tx + AV_MARGIN + AV_R, y + AV_R + 2, AV_R, AVATAR_USER, "U")
    draw.text((tx + MSG_LEFT, y), "You", font=BOLD(13), fill=TEXT_PRIMARY)
    y += 20
    y = draw_wrapped(draw, user_text, tx+MSG_LEFT, y, msg_w, UI(13), TEXT_SECONDARY, lh=20)
    y += ROW_GAP

    # separator
    draw.line([(tx, y), (tx+panel_w, y)], fill=DIVIDER, width=1)
    y += ROW_GAP

    # ── Assistant turn ────────────────────────────────────────────────────
    avatar(draw, tx + AV_MARGIN + AV_R, y + AV_R + 2, AV_R, AVATAR_ASST, "A")
    draw.text((tx + MSG_LEFT, y), "Assistant", font=BOLD(13), fill=TEXT_PRIMARY)
    y += 20
    y = draw_wrapped(draw, asst_text, tx+MSG_LEFT, y, msg_w, UI(13), TEXT_SECONDARY, lh=20)
    y += CARD_MT

    # inline card
    card_w = panel_w - MSG_LEFT - MSG_PAD
    y = render_card(draw, img, tx+MSG_LEFT, y, card_w, card_title, active_side, content_fn)

    return y

# ── Content painters ───────────────────────────────────────────────────────
def mermaid_raw(draw, x0, y0, x1, y1, measure=False):
    lines = [
        ("```mermaid",           CODE_TEXT),
        ("flowchart LR",         CODE_BLUE),
        ("",                     CODE_TEXT),
        ("    A[Data Sources]",  CODE_GREEN),
        ("    B[Transform]",     CODE_GREEN),
        ("    C[Output]",        CODE_GREEN),
        ("",                     CODE_TEXT),
        ("    A --> B --> C",    CODE_YELLOW),
        ("```",                  CODE_TEXT),
    ]
    lh, pad = 19, 16
    h = pad*2 + len(lines)*lh
    if measure: return h
    w = x1 - x0
    rrect(draw, [x0, y0, x1, y0+h], 4, fill=CODE_BG)
    mf = MONO_(12)
    for i, (txt, col) in enumerate(lines):
        draw.text((x0+16, y0+pad+i*lh), txt, font=mf, fill=col)

def mermaid_rendered(draw, x0, y0, x1, y1, measure=False):
    h = 140
    if measure: return h
    pcx = (x0+x1)//2
    pcy = y0 + h//2
    nw, nh, gap = 96, 36, 36
    n1x = pcx - nw - gap
    n3x = pcx + nw + gap
    for nx, lbl in [(n1x,"Data Sources"),(pcx,"Transform"),(n3x,"Output")]:
        node(draw, nx, pcy, nw, nh, lbl)
    arrow_h(draw, n1x+nw//2, pcy, pcx-nw//2)
    arrow_h(draw, pcx+nw//2, pcy, n3x-nw//2)

# ═══════════════════════════════════════════════════════════════════════════
#  01 — MERMAID
# ═══════════════════════════════════════════════════════════════════════════
def make_mermaid():
    PANEL_W = 460
    OUTER   = 32          # outer canvas margin
    GAP     = 40          # gap between the two panels
    W = OUTER*2 + PANEL_W*2 + GAP

    user_msg = "Can you show me a simple data pipeline diagram?"
    asst_msg = "Here's a flowchart showing the three stages of the pipeline:"
    title    = "Mermaid Diagram"

    # probe height
    probe = Image.new("RGB", (W, 1000), THREAD_BG)
    y_bot = paint_thread(probe, OUTER, OUTER, PANEL_W,
                         user_msg, asst_msg, title, 'raw', mermaid_raw)
    H = y_bot + OUTER

    img = Image.new("RGB", (W, H), THREAD_BG)

    # left panel — Raw
    paint_thread(img, OUTER, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'raw', mermaid_raw)

    # gap divider
    draw = ImageDraw.Draw(img)
    gx = OUTER + PANEL_W + GAP//2
    draw.line([(gx, OUTER+16),(gx, H-OUTER-16)], fill=BORDER, width=1)

    # right panel — Rendered
    paint_thread(img, OUTER+PANEL_W+GAP, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'rendered', mermaid_rendered)

    return img

# ── Run ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    renders = {"01-mermaid": make_mermaid}
    for name, fn in renders.items():
        path = os.path.join(OUT_DIR, f"{name}.png")
        fn().save(path)
        print(f"  ✓  {path}")
