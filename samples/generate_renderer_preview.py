"""
Renderer preview PNGs — inline chat thread mockups.
Left panel: Rendered (sets the frame size).
Right panel: Raw — same frame size as Rendered, scrollbar shown if content overflows.
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
TEXT_PRIMARY   = ( 13,  13,  13)
TEXT_SECONDARY = ( 92,  92,  92)
TEXT_LABEL     = (148, 148, 148)
DIVIDER        = (235, 235, 235)
AVATAR_USER    = (124,  58, 237)
AVATAR_ASST    = ( 16, 185, 129)
EMBED_BG       = (249, 249, 250)
EMBED_BORDER   = (232, 232, 234)
CODE_BG        = ( 22,  27,  34)
CODE_TEXT      = (201, 209, 217)
CODE_BLUE      = (121, 192, 255)
CODE_GREEN     = (122, 201, 137)
CODE_YELLOW    = (230, 192, 123)
NODE_FILL      = (243, 246, 251)
NODE_BORDER    = (180, 198, 228)
NODE_TEXT      = ( 30,  45,  70)
ARROW_COL      = (180, 188, 200)
TOGGLE_ACTIVE  = ( 60,  60,  62)
TOGGLE_MUTED   = (175, 175, 178)
SCROLL_TRACK   = (240, 240, 242)
SCROLL_THUMB   = (196, 196, 200)

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
    r = min(r, (x1-x0)//2, (y1-y0)//2)
    if r < 1:
        if fill:    draw.rectangle([x0,y0,x1,y1], fill=fill)
        if outline: draw.rectangle([x0,y0,x1,y1], outline=outline, width=lw)
        return
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
    if draw:
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

# ── Scrollbar ──────────────────────────────────────────────────────────────
SCROLL_W = 6   # scrollbar track width

def draw_scrollbar(draw, x, y0, y1, full_h, visible_h):
    """Draw a minimal OS-style scrollbar. full_h = total content h, visible_h = viewport h."""
    track_h = y1 - y0
    thumb_h  = max(24, int(track_h * visible_h / full_h))
    thumb_y  = y0   # scrolled to top for preview
    # track (invisible — same as bg)
    draw.rectangle([x, y0, x+SCROLL_W, y1], fill=SCROLL_TRACK)
    # thumb
    rrect(draw, [x+1, thumb_y+2, x+SCROLL_W-1, thumb_y+thumb_h-2], 3, fill=SCROLL_THUMB)

# ── Embed chrome ───────────────────────────────────────────────────────────
EMBED_R       = 5
EMBED_PAD     = 18
TITLE_ROW_H   = 28

def _draw_embed_chrome(draw, x0, y0, x1, y1, title, active_side):
    """Draw the subtle container, title, and toggle. No content."""
    rrect(draw, [x0, y0, x1, y1], EMBED_R, fill=EMBED_BG, outline=EMBED_BORDER, lw=1)
    draw.text((x0 + EMBED_PAD, y0 + 8), title, font=BOLD(13), fill=TEXT_SECONDARY)

    # toggle — plain text, top right
    tog_f   = UI(11)
    tog_b   = BOLD(11)
    sep     = "·"
    raw_lbl = "Raw"
    rnd_lbl = "Rendered"
    rx = x1 - EMBED_PAD
    raw_x = rx - twidth(raw_lbl, tog_b if active_side == 'raw' else tog_f)
    sep_x = raw_x - twidth(sep, tog_f) - 10
    rnd_x = sep_x - twidth(rnd_lbl, tog_b if active_side == 'rendered' else tog_f) - 2

    tog_y = y0 + 10
    if active_side == 'rendered':
        draw.text((rnd_x, tog_y), rnd_lbl, font=tog_b, fill=TOGGLE_ACTIVE)
        draw.text((sep_x + 4, tog_y), sep,  font=tog_f, fill=TEXT_LABEL)
        draw.text((raw_x, tog_y),  raw_lbl, font=tog_f, fill=TOGGLE_MUTED)
    else:
        draw.text((rnd_x, tog_y), rnd_lbl, font=tog_f, fill=TOGGLE_MUTED)
        draw.text((sep_x + 4, tog_y), sep,  font=tog_f, fill=TEXT_LABEL)
        draw.text((raw_x, tog_y),  raw_lbl, font=tog_b, fill=TOGGLE_ACTIVE)

    # rule under title row
    draw.line([(x0+1, y0+TITLE_ROW_H), (x1-1, y0+TITLE_ROW_H)], fill=EMBED_BORDER, width=1)

def render_embed_rendered(draw, img, x0, y0, embed_w, title, content_fn):
    """
    Draw the Rendered embed. Content determines the height.
    Returns (bottom_y, content_h_inside) so Raw can match.
    """
    content_h = content_fn(None, 0, 0, embed_w - EMBED_PAD*2, 0, measure=True)
    total_h   = TITLE_ROW_H + EMBED_PAD + content_h + EMBED_PAD
    x1, y1    = x0 + embed_w, y0 + total_h
    _draw_embed_chrome(draw, x0, y0, x1, y1, title, 'rendered')
    cx0 = x0 + EMBED_PAD
    cy0 = y0 + TITLE_ROW_H + EMBED_PAD
    cx1 = x1 - EMBED_PAD
    cy1 = y1 - EMBED_PAD
    content_fn(draw, cx0, cy0, cx1, cy1, measure=False)
    return y1, total_h

def render_embed_raw(draw, img, x0, y0, embed_w, title, total_h, content_fn):
    """
    Draw the Raw embed at the exact same total_h as the Rendered embed.
    Clips content to the viewport; draws a scrollbar if content is taller.
    """
    x1, y1    = x0 + embed_w, y0 + total_h
    _draw_embed_chrome(draw, x0, y0, x1, y1, title, 'raw')

    viewport_h = total_h - TITLE_ROW_H - EMBED_PAD*2
    content_h  = content_fn(None, 0, 0, embed_w - EMBED_PAD*2 - SCROLL_W - 4, 0, measure=True)
    needs_scroll = content_h > viewport_h

    cx0 = x0 + EMBED_PAD
    cy0 = y0 + TITLE_ROW_H + EMBED_PAD
    cx1 = x1 - EMBED_PAD - (SCROLL_W + 4 if needs_scroll else 0)
    cy1 = y0 + total_h - EMBED_PAD

    # clip region — draw content into a temp image then paste clipped
    cw = cx1 - cx0
    ch = content_h
    tmp = Image.new("RGB", (cw, ch), CODE_BG)
    tmp_draw = ImageDraw.Draw(tmp)
    content_fn(tmp_draw, 0, 0, cw, ch, measure=False)
    # paste only the visible portion
    img.paste(tmp.crop((0, 0, cw, viewport_h)), (cx0, cy0))

    if needs_scroll:
        sx = x1 - EMBED_PAD - SCROLL_W + 2
        draw_scrollbar(draw, sx, cy0, cy0 + viewport_h, content_h, viewport_h)

    return y1

# ── Thread layout ──────────────────────────────────────────────────────────
AV_R      = 14
AV_LEFT   = 20
MSG_LEFT  = AV_LEFT + AV_R*2 + 12
MSG_RIGHT = 24
ROW_GAP   = 26
EMBED_MT  = 14

def paint_thread(img, tx, ty, panel_w, user_text, asst_text,
                 embed_title, active_side, content_fn,
                 fixed_embed_h=None):
    """
    Paint a chat thread. Returns (bottom_y, embed_total_h).
    fixed_embed_h: if set, raw panel uses this height instead of computing it.
    """
    draw  = ImageDraw.Draw(img)
    y     = ty
    msg_w = panel_w - MSG_LEFT - MSG_RIGHT

    # user
    avatar(draw, tx+AV_LEFT+AV_R, y+AV_R+2, AV_R, AVATAR_USER, "U")
    draw.text((tx+MSG_LEFT, y+1), "You", font=BOLD(13), fill=TEXT_PRIMARY)
    y += 20
    y = draw_wrapped(draw, user_text, tx+MSG_LEFT, y, msg_w, UI(13), TEXT_SECONDARY)
    y += ROW_GAP
    draw.line([(tx, y),(tx+panel_w, y)], fill=DIVIDER, width=1)
    y += ROW_GAP

    # assistant
    avatar(draw, tx+AV_LEFT+AV_R, y+AV_R+2, AV_R, AVATAR_ASST, "A")
    draw.text((tx+MSG_LEFT, y+1), "Assistant", font=BOLD(13), fill=TEXT_PRIMARY)
    y += 20
    y = draw_wrapped(draw, asst_text, tx+MSG_LEFT, y, msg_w, UI(13), TEXT_SECONDARY)
    y += EMBED_MT

    embed_w = msg_w
    embed_h = None

    if active_side == 'rendered':
        y, embed_h = render_embed_rendered(draw, img, tx+MSG_LEFT, y, embed_w,
                                           embed_title, content_fn)
    else:
        y = render_embed_raw(draw, img, tx+MSG_LEFT, y, embed_w,
                             embed_title, fixed_embed_h, content_fn)
        embed_h = fixed_embed_h

    return y, embed_h

# ── Content painters ───────────────────────────────────────────────────────
def mermaid_rendered(draw, x0, y0, x1, y1, measure=False):
    h = 140
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
    # fill whole area with code bg, draw lines
    if draw: draw.rectangle([x0, y0, x1, y0+h], fill=CODE_BG)
    mf = MONO_(12)
    for i, (txt, col) in enumerate(lines):
        if draw: draw.text((x0+14, y0+pad+i*lh), txt, font=mf, fill=col)

# ═══════════════════════════════════════════════════════════════════════════
def make_mermaid():
    PANEL_W = 440
    OUTER   = 36
    GAP     = 48
    W       = OUTER*2 + PANEL_W*2 + GAP

    user_msg = "Can you show me a simple data pipeline diagram?"
    asst_msg = "Here's a flowchart showing the three stages of the pipeline:"
    title    = "Mermaid Diagram"

    # ── Probe: measure rendered embed height ───────────────────────────────
    probe = Image.new("RGB", (W, 1000), PAGE_BG)
    y_bot, embed_h = paint_thread(probe, OUTER, OUTER, PANEL_W,
                                  user_msg, asst_msg, title,
                                  'rendered', mermaid_rendered)
    H = y_bot + OUTER

    img = Image.new("RGB", (W, H), PAGE_BG)

    # Left — Rendered (sets size)
    paint_thread(img, OUTER, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'rendered', mermaid_rendered)

    # Gap divider
    draw = ImageDraw.Draw(img)
    gx = OUTER + PANEL_W + GAP//2
    draw.line([(gx, OUTER+10),(gx, H-OUTER-10)], fill=DIVIDER, width=1)

    # Right — Raw (same embed height, scrollbar if needed)
    paint_thread(img, OUTER+PANEL_W+GAP, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'raw', mermaid_raw,
                 fixed_embed_h=embed_h)

    return img

# ── Run ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    renders = {"01-mermaid": make_mermaid}
    for name, fn in renders.items():
        path = os.path.join(OUT_DIR, f"{name}.png")
        fn().save(path)
        print(f"  ✓  {path}")
