"""
Renderer preview PNGs — inline chat thread mockups, subtle content-embed styling.
The rendered object is part of the conversation, not a separate component.
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

# ── Palette ────────────────────────────────────────────────────────────────
WHITE          = (255, 255, 255)
PAGE_BG        = (255, 255, 255)
TEXT_PRIMARY   = ( 13,  13,  13)      # near-black — matches chat prose
TEXT_SECONDARY = ( 92,  92,  92)      # muted — matches chat secondary text
TEXT_LABEL     = (148, 148, 148)      # very muted label / meta text
DIVIDER        = (235, 235, 235)
AVATAR_USER    = (124,  58, 237)
AVATAR_ASST    = ( 16, 185, 129)
EMBED_BG       = (249, 249, 250)      # barely-there tint for content block
EMBED_BORDER   = (232, 232, 234)      # very subtle 1px border
CODE_BG        = ( 22,  27,  34)
CODE_TEXT      = (201, 209, 217)
CODE_BLUE      = (121, 192, 255)
CODE_GREEN     = (122, 201, 137)
CODE_YELLOW    = (230, 192, 123)
NODE_FILL      = (243, 246, 251)
NODE_BORDER    = (180, 198, 228)
NODE_TEXT      = ( 30,  45,  70)
ARROW_COL      = (180, 188, 200)
TOGGLE_TEXT    = (160, 160, 162)      # very muted toggle labels
TOGGLE_ACTIVE  = ( 80,  80,  82)      # slightly darker when active

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

def draw_wrapped(draw, text, x, y, max_w, font, color, lh=21):
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
    for i, l in enumerate(lines):
        draw.text((x, y + i*lh), l, font=font, fill=color)
    return y + len(lines) * lh

def arrow_h(draw, x0, y, x1, color=ARROW_COL, head=6):
    if x1 <= x0 + head: return
    draw.line([(x0,y),(x1-head,y)], fill=color, width=1)
    draw.polygon([(x1-head,y-3),(x1,y),(x1-head,y+3)], fill=color)

def node(draw, cx, cy, w, h, label, r=4):
    x0, y0 = cx-w//2, cy-h//2
    rrect(draw, [x0,y0,x0+w,y0+h], r, fill=NODE_FILL, outline=NODE_BORDER, lw=1)
    f = UI(12)
    iw = twidth(label, f)
    draw.text((cx - iw//2, cy-7), label, font=f, fill=NODE_TEXT)

# ── Content embed ──────────────────────────────────────────────────────────
# No header bar. Title is inline with toggle, same weight as chat body.
# Container is barely-there: light bg tint + 1px subtle border.

EMBED_R    = 5
EMBED_PAD  = 18       # internal padding

def render_embed(draw, img, x0, y0, embed_w, title, active_side, content_fn):
    """
    Draw a minimal content embed — title + toggle on one line, then content.
    No header bar, no component chrome. Flows as part of the message.
    Returns bottom y.
    """
    content_h = content_fn(None, 0, 0, embed_w - EMBED_PAD*2, 0, measure=True)
    title_row_h = 28
    total_h = title_row_h + content_h + EMBED_PAD
    x1, y1 = x0 + embed_w, y0 + total_h

    # subtle container
    rrect(draw, [x0, y0, x1, y1], EMBED_R, fill=EMBED_BG, outline=EMBED_BORDER, lw=1)

    # title — same font weight as bold chat text (BOLD 13), muted color
    tf = BOLD(13)
    draw.text((x0 + EMBED_PAD, y0 + 8), title, font=tf, fill=TEXT_SECONDARY)

    # toggle — very subtle, top right, plain text links
    tog_f = UI(11)
    rend_lbl = "Rendered"
    raw_lbl  = "Raw"
    sep      = "·"
    # positions from right
    rx = x1 - EMBED_PAD
    rend_w = twidth(rend_lbl, tog_f)
    raw_w  = twidth(raw_lbl,  tog_f)
    sep_w  = twidth(sep,      tog_f) + 8

    raw_x  = rx - raw_w
    sep_x  = raw_x - sep_w
    rend_x = sep_x - rend_w

    tog_y = y0 + 10

    if active_side == 'rendered':
        draw.text((rend_x, tog_y), rend_lbl, font=BOLD(11), fill=TOGGLE_ACTIVE)
        draw.text((sep_x + 4, tog_y), sep, font=tog_f, fill=TEXT_LABEL)
        draw.text((raw_x,  tog_y), raw_lbl,  font=tog_f, fill=TOGGLE_TEXT)
    else:
        draw.text((rend_x, tog_y), rend_lbl, font=tog_f, fill=TOGGLE_TEXT)
        draw.text((sep_x + 4, tog_y), sep, font=tog_f, fill=TEXT_LABEL)
        draw.text((raw_x,  tog_y), raw_lbl,  font=BOLD(11), fill=TOGGLE_ACTIVE)

    # thin rule below title row
    draw.line([(x0+1, y0+title_row_h), (x1-1, y0+title_row_h)], fill=EMBED_BORDER, width=1)

    # content
    cx0 = x0 + EMBED_PAD
    cy0 = y0 + title_row_h + EMBED_PAD
    cx1 = x1 - EMBED_PAD
    cy1 = y1 - EMBED_PAD
    content_fn(draw, cx0, cy0, cx1, cy1, measure=False)

    return y1

# ── Thread layout ──────────────────────────────────────────────────────────
AV_R      = 14
AV_LEFT   = 20
MSG_LEFT  = AV_LEFT + AV_R*2 + 12
MSG_RIGHT = 24
ROW_GAP   = 26
EMBED_MT  = 14     # margin above embed

def paint_thread(img, tx, ty, panel_w,
                 user_text, asst_text, embed_title, active_side, content_fn):
    draw = ImageDraw.Draw(img)
    y    = ty
    msg_w = panel_w - MSG_LEFT - MSG_RIGHT

    # ── User turn ─────────────────────────────────────────────────────────
    avatar(draw, tx + AV_LEFT + AV_R, y + AV_R + 2, AV_R, AVATAR_USER, "U")
    draw.text((tx + MSG_LEFT, y + 1), "You", font=BOLD(13), fill=TEXT_PRIMARY)
    y += 20
    y = draw_wrapped(draw, user_text, tx+MSG_LEFT, y, msg_w, UI(13), TEXT_SECONDARY)
    y += ROW_GAP

    # row divider
    draw.line([(tx, y),(tx+panel_w, y)], fill=DIVIDER, width=1)
    y += ROW_GAP

    # ── Assistant turn ────────────────────────────────────────────────────
    avatar(draw, tx + AV_LEFT + AV_R, y + AV_R + 2, AV_R, AVATAR_ASST, "A")
    draw.text((tx + MSG_LEFT, y + 1), "Assistant", font=BOLD(13), fill=TEXT_PRIMARY)
    y += 20
    y = draw_wrapped(draw, asst_text, tx+MSG_LEFT, y, msg_w, UI(13), TEXT_SECONDARY)
    y += EMBED_MT

    # inline embed
    embed_w = msg_w
    y = render_embed(draw, img, tx+MSG_LEFT, y, embed_w, embed_title, active_side, content_fn)

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
    lh, pad = 18, 14
    h = pad*2 + len(lines)*lh
    if measure: return h
    w = x1 - x0
    rrect(draw, [x0, y0, x1, y0+h], 3, fill=CODE_BG)
    mf = MONO_(12)
    for i, (txt, col) in enumerate(lines):
        draw.text((x0+14, y0+pad+i*lh), txt, font=mf, fill=col)

def mermaid_rendered(draw, x0, y0, x1, y1, measure=False):
    h = 130
    if measure: return h
    pcx = (x0+x1)//2
    pcy = y0 + h//2
    nw, nh, gap = 90, 34, 34
    n1x = pcx - nw - gap
    n3x = pcx + nw + gap
    for nx, lbl in [(n1x,"Data Sources"),(pcx,"Transform"),(n3x,"Output")]:
        node(draw, nx, pcy, nw, nh, lbl)
    arrow_h(draw, n1x+nw//2, pcy, pcx-nw//2)
    arrow_h(draw, pcx+nw//2, pcy, n3x-nw//2)

# ═══════════════════════════════════════════════════════════════════════════
def make_mermaid():
    PANEL_W = 440
    OUTER   = 36
    GAP     = 48
    W = OUTER*2 + PANEL_W*2 + GAP

    user_msg = "Can you show me a simple data pipeline diagram?"
    asst_msg = "Here's a flowchart showing the three stages of the pipeline:"
    title    = "Mermaid Diagram"

    probe = Image.new("RGB", (W, 900), PAGE_BG)
    y_bot = paint_thread(probe, OUTER, OUTER, PANEL_W,
                         user_msg, asst_msg, title, 'raw', mermaid_raw)
    H = y_bot + OUTER

    img = Image.new("RGB", (W, H), PAGE_BG)

    paint_thread(img, OUTER, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'raw', mermaid_raw)

    draw = ImageDraw.Draw(img)
    gx = OUTER + PANEL_W + GAP//2
    draw.line([(gx, OUTER+10),(gx, H-OUTER-10)], fill=DIVIDER, width=1)

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
