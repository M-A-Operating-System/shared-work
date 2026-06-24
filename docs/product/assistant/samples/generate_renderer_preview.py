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
    PANEL_W = 580
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

# ═══════════════════════════════════════════════════════════════════════════
#  02 — VEGA-LITE CHART
# ═══════════════════════════════════════════════════════════════════════════
BAR_FILL   = ( 99, 132, 255)
BAR_FILL_2 = ( 54, 162, 235)
AXIS_COL   = (200, 204, 210)
TICK_COL   = (160, 165, 172)
GRID_COL   = (238, 240, 243)

def vegalite_rendered(draw, x0, y0, x1, y1, measure=False):
    h = 180
    if measure: return h
    data = [("Q1", 42), ("Q2", 67), ("Q3", 55), ("Q4", 81)]
    pad_l, pad_r, pad_t, pad_b = 36, 16, 16, 28
    chart_x0 = x0 + pad_l
    chart_x1 = x1 - pad_r
    chart_y0 = y0 + pad_t
    chart_y1 = y0 + h - pad_b
    chart_w  = chart_x1 - chart_x0
    chart_h  = chart_y1 - chart_y0
    max_val  = 100
    n = len(data)
    bar_gap  = 14
    bar_w    = (chart_w - bar_gap * (n + 1)) // n

    # grid lines
    for pct in [0, 25, 50, 75, 100]:
        gy = chart_y1 - int(chart_h * pct / max_val)
        draw.line([(chart_x0, gy), (chart_x1, gy)], fill=GRID_COL, width=1)
        lbl = str(pct)
        lf = UI(10)
        lw = twidth(lbl, lf)
        draw.text((chart_x0 - lw - 4, gy - 6), lbl, font=lf, fill=TICK_COL)

    # axes
    draw.line([(chart_x0, chart_y0), (chart_x0, chart_y1)], fill=AXIS_COL, width=1)
    draw.line([(chart_x0, chart_y1), (chart_x1, chart_y1)], fill=AXIS_COL, width=1)

    # bars + labels
    for i, (label, val) in enumerate(data):
        bx = chart_x0 + bar_gap * (i + 1) + bar_w * i
        bar_h_px = int(chart_h * val / max_val)
        by0 = chart_y1 - bar_h_px
        rrect(draw, [bx, by0, bx+bar_w, chart_y1], 3, fill=BAR_FILL)
        lf = UI(10)
        lw = twidth(label, lf)
        draw.text((bx + bar_w//2 - lw//2, chart_y1 + 4), label, font=lf, fill=TICK_COL)

def vegalite_raw(draw, x0, y0, x1, y1, measure=False):
    lines = [
        ('```vega-lite',                            CODE_TEXT),
        ('{',                                       CODE_TEXT),
        ('  "$schema": "https://vega.github.io/",', CODE_BLUE),
        ('  "mark": "bar",',                        CODE_GREEN),
        ('  "data": { "values": [',                 CODE_TEXT),
        ('    {"quarter":"Q1","value":42},',         CODE_YELLOW),
        ('    {"quarter":"Q2","value":67},',         CODE_YELLOW),
        ('    {"quarter":"Q3","value":55},',         CODE_YELLOW),
        ('    {"quarter":"Q4","value":81}',          CODE_YELLOW),
        ('  ] },',                                  CODE_TEXT),
        ('  "encoding": {',                         CODE_TEXT),
        ('    "x": {"field":"quarter"},',            CODE_BLUE),
        ('    "y": {"field":"value"}',               CODE_BLUE),
        ('  }',                                     CODE_TEXT),
        ('}',                                       CODE_TEXT),
        ('```',                                     CODE_TEXT),
    ]
    lh, pad = 17, 12
    h = pad*2 + len(lines)*lh
    if measure: return h
    if draw: draw.rectangle([x0, y0, x1, y0+h], fill=CODE_BG)
    mf = MONO_(11)
    for i, (txt, col) in enumerate(lines):
        if draw: draw.text((x0+14, y0+pad+i*lh), txt, font=mf, fill=col)

def make_vegalite():
    PANEL_W = 580
    OUTER   = 36
    GAP     = 48
    W       = OUTER*2 + PANEL_W*2 + GAP

    user_msg = "Can you show me our quarterly revenue as a chart?"
    asst_msg = "Here's a bar chart of revenue across the four quarters:"
    title    = "Vega-Lite Chart"

    probe = Image.new("RGB", (W, 1000), PAGE_BG)
    y_bot, embed_h = paint_thread(probe, OUTER, OUTER, PANEL_W,
                                  user_msg, asst_msg, title,
                                  'rendered', vegalite_rendered)
    H = y_bot + OUTER

    img = Image.new("RGB", (W, H), PAGE_BG)
    paint_thread(img, OUTER, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'rendered', vegalite_rendered)

    draw = ImageDraw.Draw(img)
    gx = OUTER + PANEL_W + GAP//2
    draw.line([(gx, OUTER+10),(gx, H-OUTER-10)], fill=DIVIDER, width=1)

    paint_thread(img, OUTER+PANEL_W+GAP, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'raw', vegalite_raw,
                 fixed_embed_h=embed_h)
    return img

# ═══════════════════════════════════════════════════════════════════════════
#  03 — DATA TABLE
# ═══════════════════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════════
#  03 — DATA TABLE
# ═══════════════════════════════════════════════════════════════════════════
TBL_HDR_BG   = (247, 248, 250)
TBL_HDR_TX   = ( 55,  65,  81)
TBL_ROW_ALT  = (252, 252, 253)
TBL_BORDER   = (229, 231, 235)
TBL_TX       = ( 31,  41,  55)
TBL_MUTED    = (130, 138, 150)
SORT_ACTIVE  = ( 99, 102, 241)
FILTER_BG    = (255, 255, 255)
FILTER_BDR   = (209, 213, 219)
ROW_NUM_COL  = (185, 190, 200)
STATUS_GREEN = (220, 252, 231)
STATUS_GTXT  = ( 22, 101,  52)
STATUS_RED   = (254, 226, 226)
STATUS_RTXT  = (153,  27,  27)
STATUS_GRAY  = (243, 244, 246)
STATUS_GTXT2 = ( 75,  85,  99)
STATUS_AMB   = (254, 243, 199)
STATUS_ATXT  = (146,  64,  14)

ROW_NUM_W = 26
COLS_DEF  = [                         # (label, pixel-width in full table)
    ("Name",        92),
    ("Department",  88),
    ("Role",        90),
    ("Score",       52),
    ("Region",      66),
    ("Status",      66),
]
ALL_ROWS = [
    ("Alice Chen",  "Engineering", "Senior Developer",  "94", "EMEA",  "Active"),
    ("Bob Martin",  "Marketing",   "Campaign Manager",  "78", "AMER",  "Active"),
    ("Carol White", "Finance",     "Analyst",           "85", "APAC",  "On Leave"),
    ("David Kim",   "Engineering", "Tech Lead",         "91", "AMER",  "Active"),
    ("Emma Davis",  "Marketing",   "Brand Manager",     "72", "EMEA",  "Inactive"),
    ("Frank Lee",   "Engineering", "Developer",         "88", "APAC",  "Active"),
    ("Grace Hall",  "Finance",     "Controller",        "95", "AMER",  "Active"),
    ("Henry Park",  "Sales",       "Account Executive", "69", "EMEA",  "Active"),
]
VISIBLE_ROWS = 5
TBL_ROW_H  = 21
TBL_HDR_H  = 25
TBL_FILT_H = 21
TBL_FOOT_H = 20
V_SCROLL_W = 7
H_SCROLL_H = 7

def _status_badge(draw, cx, cy, text):
    if   text == "Active":   bg, tx = STATUS_GREEN, STATUS_GTXT
    elif text == "Inactive": bg, tx = STATUS_RED,   STATUS_RTXT
    elif text == "On Leave": bg, tx = STATUS_AMB,   STATUS_ATXT
    else:                    bg, tx = STATUS_GRAY,  STATUS_GTXT2
    f  = UI(9)
    tw = twidth(text, f)
    bw, bh = tw+10, 14
    bx, by = cx-bw//2, cy-bh//2
    rrect(draw, [bx, by, bx+bw, by+bh], 7, fill=bg)
    draw.text((bx+5, by+3), text, font=f, fill=tx)

def _draw_full_table(td, col_widths, col_names, total_w):
    """Draw the complete table (all rows, all cols) into ImageDraw td at (0,0)."""
    hf  = BOLD(10)
    rf  = UI(10)
    ff  = UI(9)

    def cx(i):
        return ROW_NUM_W + sum(col_widths[:i])

    # ── Header ───────────────────────────────────────────────────────────
    td.rectangle([0, 0, total_w, TBL_HDR_H], fill=TBL_HDR_BG)
    td.line([(0, TBL_HDR_H), (total_w, TBL_HDR_H)], fill=TBL_BORDER, width=1)
    td.line([(ROW_NUM_W, 0), (ROW_NUM_W, TBL_HDR_H)], fill=TBL_BORDER, width=1)
    for i, (name, cw) in enumerate(zip(col_names, col_widths)):
        td.text((cx(i)+6, TBL_HDR_H//2-6), name, font=hf, fill=TBL_HDR_TX)
        sx = cx(i)+cw-12
        sy = TBL_HDR_H//2
        if i == 3:   # score — active sort
            td.polygon([(sx,sy+3),(sx+5,sy-3),(sx+10,sy+3)], fill=SORT_ACTIVE)
        else:
            td.polygon([(sx,sy+2),(sx+5,sy-2),(sx+10,sy+2)], fill=(205,207,213))
        if i < len(col_names)-1:
            td.line([(cx(i+1), 0),(cx(i+1), TBL_HDR_H)], fill=TBL_BORDER, width=1)

    # ── Filter row ────────────────────────────────────────────────────────
    fy = TBL_HDR_H
    td.rectangle([0, fy, total_w, fy+TBL_FILT_H], fill=WHITE)
    td.line([(0, fy+TBL_FILT_H),(total_w, fy+TBL_FILT_H)], fill=TBL_BORDER, width=1)
    for i, cw in enumerate(col_widths):
        fx0 = cx(i)+5;  fx1 = cx(i)+cw-6
        rrect(td, [fx0, fy+3, fx1, fy+TBL_FILT_H-3], 3,
              fill=FILTER_BG, outline=FILTER_BDR, lw=1)
        td.text((fx0+4, fy+5), "Filter…", font=ff, fill=(200,202,208))
        if i < len(col_names)-1:
            td.line([(cx(i+1), fy),(cx(i+1), fy+TBL_FILT_H)], fill=TBL_BORDER, width=1)
    td.line([(ROW_NUM_W, fy),(ROW_NUM_W, fy+TBL_FILT_H)], fill=TBL_BORDER, width=1)

    # ── Data rows ─────────────────────────────────────────────────────────
    ry_base = TBL_HDR_H + TBL_FILT_H
    for r, row in enumerate(ALL_ROWS):
        ry0 = ry_base + r*TBL_ROW_H
        ry1 = ry0 + TBL_ROW_H
        bg  = WHITE if r % 2 == 0 else TBL_ROW_ALT
        td.rectangle([0, ry0, total_w, ry1], fill=bg)
        td.line([(0, ry1),(total_w, ry1)], fill=TBL_BORDER, width=1)
        # row number
        rn = str(r+1)
        rnw = twidth(rn, rf)
        td.text((ROW_NUM_W//2-rnw//2, ry0+TBL_ROW_H//2-6), rn, font=rf, fill=ROW_NUM_COL)
        td.line([(ROW_NUM_W, ry0),(ROW_NUM_W, ry1)], fill=TBL_BORDER, width=1)
        for i, (val, cw) in enumerate(zip(row, col_widths)):
            if i == 5:
                _status_badge(td, cx(i)+cw//2, ry0+TBL_ROW_H//2, val)
            else:
                td.text((cx(i)+6, ry0+TBL_ROW_H//2-6), val, font=rf, fill=TBL_TX)
            if i < len(col_widths)-1:
                td.line([(cx(i+1),ry0),(cx(i+1),ry1)], fill=TBL_BORDER, width=1)

def table_rendered(draw, x0, y0, x1, y1, measure=False):
    h = TBL_HDR_H + TBL_FILT_H + TBL_ROW_H*VISIBLE_ROWS + H_SCROLL_H + TBL_FOOT_H
    if measure: return h

    viewport_w  = x1 - x0
    col_vp_w    = viewport_w - V_SCROLL_W    # column area leaves room for v-scrollbar
    row_vp_h    = TBL_HDR_H + TBL_FILT_H + TBL_ROW_H * VISIBLE_ROWS

    col_names   = [c[0] for c in COLS_DEF]
    col_widths  = [c[1] for c in COLS_DEF]
    full_w      = ROW_NUM_W + sum(col_widths)
    full_h      = TBL_HDR_H + TBL_FILT_H + TBL_ROW_H * len(ALL_ROWS)

    # Draw full table into temp image, paste clipped region
    tmp    = Image.new("RGB", (full_w, full_h), WHITE)
    td     = ImageDraw.Draw(tmp)
    _draw_full_table(td, col_widths, col_names, full_w)
    img_ref = draw._image
    img_ref.paste(tmp.crop((0, 0, col_vp_w, row_vp_h)), (x0, y0))

    # Outer border around the column+row viewport
    draw.rectangle([x0, y0, x0+col_vp_w, y0+row_vp_h], outline=TBL_BORDER, width=1)

    # ── Vertical scrollbar ────────────────────────────────────────────────
    vsx  = x0 + col_vp_w
    vsy0 = y0 + TBL_HDR_H + TBL_FILT_H
    vsy1 = y0 + row_vp_h
    draw.rectangle([vsx, y0, vsx+V_SCROLL_W, y0+row_vp_h], fill=SCROLL_TRACK)
    v_thumb_h = max(16, int((vsy1-vsy0) * VISIBLE_ROWS / len(ALL_ROWS)))
    rrect(draw, [vsx+1, vsy0+2, vsx+V_SCROLL_W-1, vsy0+v_thumb_h-2], 3, fill=SCROLL_THUMB)

    # ── Horizontal scrollbar ──────────────────────────────────────────────
    hsy  = y0 + row_vp_h
    draw.rectangle([x0, hsy, x0+col_vp_w, hsy+H_SCROLL_H], fill=SCROLL_TRACK)
    h_thumb_w = max(24, int(col_vp_w * col_vp_w / full_w))
    rrect(draw, [x0+2, hsy+1, x0+h_thumb_w-2, hsy+H_SCROLL_H-1], 3, fill=SCROLL_THUMB)

    # ── Footer ────────────────────────────────────────────────────────────
    foot_y = hsy + H_SCROLL_H
    draw.rectangle([x0, foot_y, x1, foot_y+TBL_FOOT_H], fill=TBL_HDR_BG)
    draw.line([(x0, foot_y),(x1, foot_y)], fill=TBL_BORDER, width=1)
    draw.text((x0+8, foot_y+5),
              f"Showing 1–{VISIBLE_ROWS} of {len(ALL_ROWS)} rows · {len(COLS_DEF)} columns",
              font=UI(9), fill=TBL_MUTED)

def table_raw(draw, x0, y0, x1, y1, measure=False):
    lines = [
        ("```csv",                                             CODE_TEXT),
        ("Name,Department,Role,Score,Region,Status",          CODE_BLUE),
        ("Alice Chen,Engineering,Senior Developer,94,EMEA,Active",   CODE_GREEN),
        ("Bob Martin,Marketing,Campaign Manager,78,AMER,Active",     CODE_GREEN),
        ("Carol White,Finance,Analyst,85,APAC,On Leave",             CODE_YELLOW),
        ("David Kim,Engineering,Tech Lead,91,AMER,Active",           CODE_GREEN),
        ("Emma Davis,Marketing,Brand Manager,72,EMEA,Inactive",      CODE_TEXT),
        ("Frank Lee,Engineering,Developer,88,APAC,Active",           CODE_GREEN),
        ("Grace Hall,Finance,Controller,95,AMER,Active",             CODE_GREEN),
        ("Henry Park,Sales,Account Executive,69,EMEA,Active",        CODE_GREEN),
        ("```",                                                CODE_TEXT),
    ]
    lh, pad = 17, 12
    h = pad*2 + len(lines)*lh
    if measure: return h
    if draw: draw.rectangle([x0, y0, x1, y0+h], fill=CODE_BG)
    mf = MONO_(10)
    for i, (txt, col) in enumerate(lines):
        if draw: draw.text((x0+12, y0+pad+i*lh), txt, font=mf, fill=col)

def make_table():
    PANEL_W = 580
    OUTER   = 36
    GAP     = 48
    W       = OUTER*2 + PANEL_W*2 + GAP

    user_msg = "Can you show me the full team breakdown in a table?"
    asst_msg = "Here's the team data with scores, roles, and status:"
    title    = "Data Table"

    probe = Image.new("RGB", (W, 1000), PAGE_BG)
    y_bot, embed_h = paint_thread(probe, OUTER, OUTER, PANEL_W,
                                  user_msg, asst_msg, title,
                                  'rendered', table_rendered)
    H = y_bot + OUTER

    img = Image.new("RGB", (W, H), PAGE_BG)
    paint_thread(img, OUTER, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'rendered', table_rendered)

    draw = ImageDraw.Draw(img)
    gx = OUTER + PANEL_W + GAP//2
    draw.line([(gx, OUTER+10),(gx, H-OUTER-10)], fill=DIVIDER, width=1)

    paint_thread(img, OUTER+PANEL_W+GAP, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'raw', table_raw,
                 fixed_embed_h=embed_h)
    return img

# ═══════════════════════════════════════════════════════════════════════════
#  04 — JSON INSPECTOR
# ═══════════════════════════════════════════════════════════════════════════
JSON_BG       = (255, 255, 255)
JSON_KEY      = ( 14,  99, 156)    # blue key
JSON_STR      = (198,  93,  93)    # red/salmon string
JSON_NUM      = (100, 155,  80)    # green number
JSON_BOOL     = (157,  99, 215)    # purple boolean
JSON_NULL     = (157,  99, 215)
JSON_PUNCT    = ( 80,  80,  80)    # brackets / braces
JSON_EXPAND   = (180, 185, 195)    # triangle expand icon
JSON_LINE     = (240, 241, 243)    # tree guide lines
JSON_ROOT_BG  = (247, 248, 250)    # root header band
JSON_BADGE_BG = (232, 237, 255)
JSON_BADGE_TX = ( 60,  80, 180)
JSON_HOVER    = (238, 242, 255)    # hover highlight (shown on first key)

# Tree definition: (indent_level, key, value_text, value_color, expanded, children_count)
# value_color=None means no inline value (object/array node)
_JSON_NODES = [
    # lvl  key                 value              color        badge
    (0,    None,               None,              None,        "{}"),       # root object
    (1,    "name",             '"Atlas"',         JSON_STR,    None),
    (1,    "version",          '"2.3.1"',         JSON_STR,    None),
    (1,    "active",           "true",            JSON_BOOL,   None),
    (1,    "config",           None,              None,        "{}"),       # collapsed object
    (2,    "provider",         '"anthropic"',     JSON_STR,    None),
    (2,    "model",            '"powerful"',      JSON_STR,    None),
    (2,    "maxTokens",        "4096",            JSON_NUM,    None),
    (1,    "tools",            None,              None,        "[3]"),      # collapsed array
    (2,    "0",                '"search"',        JSON_STR,    None),
    (2,    "1",                '"calculator"',    JSON_STR,    None),
    (2,    "2",                '"data-lookup"',   JSON_STR,    None),
    (1,    "sessionId",        '"sess_9f2c"',     JSON_STR,    None),
    (1,    "createdAt",        '"2026-06-17"',    JSON_STR,    None),
]

# Which nodes are visible in the rendered viewport
# Root + name/version/active (expanded) + config (collapsed, no children shown)
# + tools (collapsed, no children shown) + sessionId + createdAt
_VISIBLE_NODES = [0, 1, 2, 3, 4, 8, 12, 13]   # indices into _JSON_NODES

def _draw_triangle(draw, cx, cy, expanded, color):
    """Draw a small disclosure triangle."""
    if expanded:
        draw.polygon([(cx-4,cy-2),(cx+4,cy-2),(cx,cy+3)], fill=color)
    else:
        draw.polygon([(cx-2,cy-4),(cx+3,cy),(cx-2,cy+4)], fill=color)

def json_rendered(draw, x0, y0, x1, y1, measure=False):
    ROW_H  = 22
    PAD    = 10
    INDENT = 16
    total_rows = len(_VISIBLE_NODES)
    h = PAD + ROW_H * total_rows + PAD
    if measure: return h
    if draw is None: return

    f_key  = BOLD(11)
    f_val  = UI(11)
    f_bge  = UI(9)

    for row_idx, node_idx in enumerate(_VISIBLE_NODES):
        lvl, key, val, col, badge = _JSON_NODES[node_idx]
        ry = y0 + PAD + row_idx * ROW_H

        # hover highlight on first data row
        if row_idx == 1:
            draw.rectangle([x0-4, ry-1, x1+4, ry+ROW_H-3], fill=JSON_HOVER)

        # indent guides
        for d in range(1, lvl+1):
            gx = x0 + PAD + (d-1)*INDENT + INDENT//2
            draw.line([(gx, ry),(gx, ry+ROW_H)], fill=JSON_LINE, width=1)

        tx = x0 + PAD + lvl * INDENT

        # triangle for expandable nodes
        is_obj_or_arr = (val is None)
        if is_obj_or_arr:
            expanded = (node_idx in [0, 4]) if row_idx > 0 else True
            # root is always expanded in this view; config at idx 4 is also shown expanded
            expanded = node_idx in [0]   # only root expanded; config+tools collapsed
            _draw_triangle(draw, tx+5, ry+ROW_H//2, expanded, JSON_EXPAND)
            tx += 14

        # key
        if key is not None:
            draw.text((tx, ry+4), f'"{key}"', font=f_key, fill=JSON_KEY)
            kw = twidth(f'"{key}"', f_key)
            draw.text((tx+kw, ry+4), ": ", font=f_val, fill=JSON_PUNCT)
            tx += kw + twidth(": ", f_val)

        # value or badge
        if val is not None:
            draw.text((tx, ry+4), val, font=f_val, fill=col)
        elif badge is not None:
            # badge pill
            bw = twidth(badge, f_bge) + 10
            bh = 14
            by = ry + ROW_H//2 - bh//2
            rrect(draw, [tx, by, tx+bw, by+bh], 4, fill=JSON_BADGE_BG)
            draw.text((tx+5, by+3), badge, font=f_bge, fill=JSON_BADGE_TX)

def json_raw(draw, x0, y0, x1, y1, measure=False):
    lines = [
        ('```json',                             CODE_TEXT),
        ('{',                                   CODE_TEXT),
        ('  "name": "Atlas",',                  CODE_TEXT),
        ('  "version": "2.3.1",',               CODE_TEXT),
        ('  "active": true,',                   CODE_TEXT),
        ('  "config": {',                       CODE_TEXT),
        ('    "provider": "anthropic",',         CODE_TEXT),
        ('    "model": "powerful",',             CODE_TEXT),
        ('    "maxTokens": 4096',               CODE_TEXT),
        ('  },',                                CODE_TEXT),
        ('  "tools": [',                        CODE_TEXT),
        ('    "search",',                       CODE_TEXT),
        ('    "calculator",',                   CODE_TEXT),
        ('    "data-lookup"',                   CODE_TEXT),
        ('  ],',                                CODE_TEXT),
        ('  "sessionId": "sess_9f2c",',         CODE_TEXT),
        ('  "createdAt": "2026-06-17"',         CODE_TEXT),
        ('}',                                   CODE_TEXT),
        ('```',                                 CODE_TEXT),
    ]
    # syntax-color the lines
    def color(txt):
        t = txt.strip()
        if t.startswith('"') and '":' in t:
            k, rest = t.split(':', 1)
            return [(CODE_BLUE, txt[:len(txt)-len(t)]+k+':'),
                    (CODE_TEXT, ' '),
                    (CODE_GREEN if '"' in rest else
                     CODE_YELLOW if any(c.isdigit() for c in rest) else
                     JSON_BOOL, rest.strip().rstrip(','))]
        return [(CODE_TEXT, txt)]

    lh, pad = 16, 12
    h = pad*2 + len(lines)*lh
    if measure: return h
    if draw:
        draw.rectangle([x0, y0, x1, y0+h], fill=CODE_BG)
        mf = MONO_(10)
        for i, (txt, _) in enumerate(lines):
            draw.text((x0+12, y0+pad+i*lh), txt, font=mf, fill=CODE_TEXT)

def make_json():
    PANEL_W = 580
    OUTER   = 36
    GAP     = 48
    W       = OUTER*2 + PANEL_W*2 + GAP

    user_msg = "What does the current assistant config look like?"
    asst_msg = "Here's the active configuration object for this session:"
    title    = "JSON Inspector"

    probe = Image.new("RGB", (W, 1000), PAGE_BG)
    y_bot, embed_h = paint_thread(probe, OUTER, OUTER, PANEL_W,
                                  user_msg, asst_msg, title,
                                  'rendered', json_rendered)
    H = y_bot + OUTER

    img = Image.new("RGB", (W, H), PAGE_BG)
    paint_thread(img, OUTER, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'rendered', json_rendered)

    draw = ImageDraw.Draw(img)
    gx = OUTER + PANEL_W + GAP//2
    draw.line([(gx, OUTER+10),(gx, H-OUTER-10)], fill=DIVIDER, width=1)

    paint_thread(img, OUTER+PANEL_W+GAP, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'raw', json_raw,
                 fixed_embed_h=embed_h)
    return img

# ═══════════════════════════════════════════════════════════════════════════
#  05 — MATH (KaTeX)
# ═══════════════════════════════════════════════════════════════════════════
MATH_BG      = (255, 255, 255)
MATH_INK     = ( 22,  22,  22)
MATH_ACCENT  = ( 30,  80, 180)   # blue for key symbols
MATH_GRAY    = (120, 125, 135)   # dim parts
MATH_DIVIDER = (225, 227, 232)

def _draw_fraction(draw, cx, cy, num_txt, den_txt, fnt_main, fnt_small, ink):
    """Draw a vertical fraction centered at cx, cy. Returns half-height used."""
    nw = twidth(num_txt, fnt_small)
    dw = twidth(den_txt, fnt_small)
    bar_w = max(nw, dw) + 8
    bar_h = 1
    # numerator
    draw.text((cx - nw//2, cy - 18), num_txt, font=fnt_small, fill=ink)
    # bar
    draw.line([(cx - bar_w//2, cy - 4), (cx + bar_w//2, cy - 4)], fill=ink, width=bar_h)
    # denominator
    draw.text((cx - dw//2, cy + 2), den_txt, font=fnt_small, fill=ink)
    return 20   # half-height

def _draw_sigma(draw, cx, cy, size, ink):
    """Draw a simple Σ-like sum symbol."""
    f = fnt(SANS, size)
    sym = "Σ"
    sw = twidth(sym, f)
    draw.text((cx - sw//2, cy - size//2), sym, font=f, fill=ink)

def math_rendered(draw, x0, y0, x1, y1, measure=False):
    """
    Render three display-math expressions in a KaTeX-style layout:
      1. Bayes' theorem
      2. Normal distribution PDF
      3. Euler's identity
    """
    BLOCK_H  = 72   # height per expression block
    PAD_V    = 16
    h = PAD_V + BLOCK_H * 3 + PAD_V
    if measure: return h
    if draw is None: return

    f_main  = fnt(SANS,      18)
    f_small = fnt(SANS,      13)
    f_tiny  = fnt(SANS,      11)
    f_label = fnt(SANS_BOLD, 10)
    f_bold  = fnt(SANS_BOLD, 18)
    f_sym   = fnt(SANS,      22)
    f_sub   = fnt(SANS,      10)

    cx = (x0 + x1) // 2

    # ── Block 1: Bayes' Theorem  P(A|B) = P(B|A)·P(A) / P(B) ──────────────
    by = y0 + PAD_V + BLOCK_H // 2
    label = "Bayes' Theorem"
    lw = twidth(label, f_label)
    draw.text((x0, y0 + PAD_V - 2), label, font=f_label, fill=MATH_GRAY)

    # render as inline pieces around a fraction
    # Left: "P(A|B) ="
    lhs = "P(A|B) ="
    lhs_w = twidth(lhs, f_main)
    frac_cx = cx + lhs_w // 2 - 10
    draw.text((cx - lhs_w//2 - 10, by - 10), lhs, font=f_main, fill=MATH_INK)

    # Fraction: P(B|A)·P(A) over P(B)
    fc = frac_cx + lhs_w // 2 + 32
    _draw_fraction(draw, fc, by - 4, "P(B|A) · P(A)", "P(B)", f_small, f_small, MATH_INK)

    # divider
    div_y = y0 + PAD_V + BLOCK_H
    draw.line([(x0, div_y), (x1, div_y)], fill=MATH_DIVIDER, width=1)

    # ── Block 2: Normal Distribution PDF ─────────────────────────────────
    by2 = div_y + BLOCK_H // 2
    label2 = "Normal Distribution — Probability Density"
    draw.text((x0, div_y + 6), label2, font=f_label, fill=MATH_GRAY)

    # f(x) =
    piece = "f(x) ="
    pw = twidth(piece, f_main)
    draw.text((cx - 110, by2 - 9), piece, font=f_main, fill=MATH_INK)

    # fraction: 1 / (σ√2π)
    fc2 = cx - 110 + pw + 28
    _draw_fraction(draw, fc2, by2 - 4, "1", "σ√2π", f_small, f_small, MATH_INK)

    # exp(...)
    exp_x = fc2 + 40
    draw.text((exp_x, by2 - 10), "exp", font=f_main, fill=MATH_INK)
    ew = twidth("exp", f_main)

    # superscript fraction: −(x−μ)² / 2σ²
    sx = exp_x + ew + 2
    sy = by2 - 20
    draw.text((sx, sy), "−(x−μ)²", font=f_tiny, fill=MATH_ACCENT)
    bar2_w = twidth("−(x−μ)²", f_tiny) + 4
    draw.line([(sx - 2, sy + 13), (sx + bar2_w, sy + 13)], fill=MATH_ACCENT, width=1)
    dw2 = twidth("2σ²", f_tiny)
    draw.text((sx + bar2_w//2 - dw2//2, sy + 15), "2σ²", font=f_tiny, fill=MATH_ACCENT)

    # divider
    div_y2 = div_y + BLOCK_H
    draw.line([(x0, div_y2), (x1, div_y2)], fill=MATH_DIVIDER, width=1)

    # ── Block 3: Euler's Identity ─────────────────────────────────────────
    by3 = div_y2 + BLOCK_H // 2
    label3 = "Euler's Identity"
    draw.text((x0, div_y2 + 6), label3, font=f_label, fill=MATH_GRAY)

    # e^(iπ) + 1 = 0   — draw each glyph
    parts = [
        ("e", f_bold, MATH_ACCENT),
        ("iπ", f_sub, MATH_ACCENT),   # superscript
        ("  + 1 = 0", f_main, MATH_INK),
    ]
    total_w = (twidth("e", f_bold) + twidth("iπ", f_sub) +
               twidth("  + 1 = 0", f_main))
    tx = cx - total_w // 2

    draw.text((tx, by3 - 10), "e", font=f_bold, fill=MATH_ACCENT)
    ex = tx + twidth("e", f_bold)
    draw.text((ex, by3 - 20), "iπ", font=f_sub, fill=MATH_ACCENT)
    ex2 = ex + twidth("iπ", f_sub)
    draw.text((ex2, by3 - 10), "  + 1 = 0", font=f_main, fill=MATH_INK)

def math_raw(draw, x0, y0, x1, y1, measure=False):
    lines = [
        ("$$",                                          CODE_TEXT),
        ("P(A|B) = \\frac{P(B|A) \\cdot P(A)}{P(B)}",  CODE_GREEN),
        ("$$",                                          CODE_TEXT),
        ("",                                            CODE_TEXT),
        ("$$",                                          CODE_TEXT),
        ("f(x) = \\frac{1}{\\sigma\\sqrt{2\\pi}}",      CODE_GREEN),
        ("  \\exp\\!\\left(",                            CODE_GREEN),
        ("    -\\frac{(x-\\mu)^2}{2\\sigma^2}",         CODE_BLUE),
        ("  \\right)",                                  CODE_GREEN),
        ("$$",                                          CODE_TEXT),
        ("",                                            CODE_TEXT),
        ("$$",                                          CODE_TEXT),
        ("e^{i\\pi} + 1 = 0",                           CODE_YELLOW),
        ("$$",                                          CODE_TEXT),
    ]
    lh, pad = 17, 12
    h = pad*2 + len(lines)*lh
    if measure: return h
    if draw:
        draw.rectangle([x0, y0, x1, y0+h], fill=CODE_BG)
        mf = MONO_(10)
        for i, (txt, col) in enumerate(lines):
            draw.text((x0+12, y0+pad+i*lh), txt, font=mf, fill=col)

def make_math():
    PANEL_W = 580
    OUTER   = 36
    GAP     = 48
    W       = OUTER*2 + PANEL_W*2 + GAP

    user_msg = "Can you show me Bayes' theorem, the normal distribution PDF, and Euler's identity?"
    asst_msg = "Here are the three expressions rendered in display math:"
    title    = "Math — KaTeX"

    probe = Image.new("RGB", (W, 1200), PAGE_BG)
    y_bot, embed_h = paint_thread(probe, OUTER, OUTER, PANEL_W,
                                  user_msg, asst_msg, title,
                                  'rendered', math_rendered)
    H = y_bot + OUTER

    img = Image.new("RGB", (W, H), PAGE_BG)
    paint_thread(img, OUTER, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'rendered', math_rendered)

    draw = ImageDraw.Draw(img)
    gx = OUTER + PANEL_W + GAP//2
    draw.line([(gx, OUTER+10),(gx, H-OUTER-10)], fill=DIVIDER, width=1)

    paint_thread(img, OUTER+PANEL_W+GAP, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'raw', math_raw,
                 fixed_embed_h=embed_h)
    return img

# ═══════════════════════════════════════════════════════════════════════════
#  06 — MARKDOWN DOCUMENT
# ═══════════════════════════════════════════════════════════════════════════
MD_H1        = ( 13,  13,  13)
MD_H2        = ( 30,  30,  30)
MD_H3        = ( 50,  50,  50)
MD_BODY      = ( 50,  55,  62)
MD_MUTED     = (120, 126, 136)
MD_CODE_BG   = (240, 242, 245)
MD_CODE_TX   = (180,  50,  90)
MD_BULLET    = ( 99, 102, 115)
MD_RULE      = (220, 222, 226)
MD_BOLD      = ( 13,  13,  13)
MD_LINK      = ( 37, 99, 235)
MD_DOC_BG    = (255, 255, 255)
MD_DOC_FRAME = (232, 234, 237)

def _md_inline_code(draw, x, y, text, base_size=13):
    """Draw an inline code span. Returns x after the span."""
    f = MONO_(base_size - 2)
    tw = twidth(text, f)
    pad = 4
    draw.rectangle([x - pad, y - 1, x + tw + pad, y + 14], fill=MD_CODE_BG)
    draw.text((x, y + 1), text, font=f, fill=MD_CODE_TX)
    return x + tw + pad * 2

def markdown_rendered(draw, x0, y0, x1, y1, measure=False):
    """Render a styled markdown document excerpt."""
    W   = x1 - x0
    PAD = 12
    lh_body = 20
    lh_h2   = 26

    # content blocks:
    # H1 title, rule, H2 + body x2, bullet list x4, H2 + body with inline code + bold
    h = (
        PAD +        # top
        34 +         # H1
        6  +         # gap after H1
        1  +         # rule
        16 +         # gap
        22 +         # H2 "Executive Summary"
        8  +         # gap
        lh_body*3 +  # body paragraph (3 lines)
        14 +         # gap
        22 +         # H2 "Key Metrics"
        8  +         # gap
        lh_body*4 +  # 4 bullet items
        14 +         # gap
        22 +         # H2 "Technical Notes"
        8  +         # gap
        lh_body*2 +  # body with inline code/bold
        PAD          # bottom
    )
    if measure: return h
    if draw is None: return

    y = y0 + PAD

    f_h1   = fnt(SANS_BOLD, 20)
    f_h2   = fnt(SANS_BOLD, 14)
    f_body = fnt(SANS,      13)
    f_bold = fnt(SANS_BOLD, 13)
    f_mute = fnt(SANS,      11)

    # H1
    draw.text((x0, y), "Q2 Performance Review", font=f_h1, fill=MD_H1)
    y += 34
    # rule under H1
    draw.line([(x0, y), (x1, y)], fill=MD_RULE, width=1)
    y += 10

    # meta line
    draw.text((x0, y), "Andrew Bush  ·  June 2026  ·  v1.2", font=f_mute, fill=MD_MUTED)
    y += 20

    # H2 — Executive Summary
    draw.text((x0, y), "Executive Summary", font=f_h2, fill=MD_H2)
    y += lh_h2
    body1 = ("Revenue grew 18 % quarter-on-quarter, driven by the EMEA region "
             "expansion and the launch of the Atlas assistant tier. Operating "
             "costs held flat at 34 % of revenue.")
    y = draw_wrapped(draw, body1, x0, y, W, f_body, MD_BODY, lh=lh_body)
    y += 14

    # H2 — Key Metrics
    draw.text((x0, y), "Key Metrics", font=f_h2, fill=MD_H2)
    y += lh_h2
    bullets = [
        ("Revenue",  "£4.2 M  (+18 % QoQ)"),
        ("MAU",      "12,400  (+31 % QoQ)"),
        ("NPS",      "67  (up from 58 in Q1)"),
        ("Uptime",   "99.96 %  (SLA: 99.9 %)"),
    ]
    for key, val in bullets:
        # bullet dot
        draw.ellipse([x0+2, y+7, x0+6, y+11], fill=MD_BULLET)
        draw.text((x0 + 14, y), key + ": ", font=f_bold, fill=MD_BOLD)
        kw = twidth(key + ": ", f_bold)
        draw.text((x0 + 14 + kw, y), val, font=f_body, fill=MD_BODY)
        y += lh_body
    y += 14

    # H2 — Technical Notes
    draw.text((x0, y), "Technical Notes", font=f_h2, fill=MD_H2)
    y += lh_h2
    # line with inline code
    draw.text((x0, y), "Cache hit rate reached ", font=f_body, fill=MD_BODY)
    x_after = twidth("Cache hit rate reached ", f_body)
    draw.text((x0 + x_after, y), "48 %", font=f_bold, fill=MD_BOLD)
    x_after += twidth("48 %", f_bold)
    draw.text((x0 + x_after, y), " against the ", font=f_body, fill=MD_BODY)
    x_after += twidth(" against the ", f_body)
    _md_inline_code(draw, x0 + x_after, y, "≥ 40 %", 13)
    y += lh_body
    # link line
    draw.text((x0, y), "Full data: ", font=f_body, fill=MD_BODY)
    lx = twidth("Full data: ", f_body)
    draw.text((x0 + lx, y), "analytics-dashboard → Q2 Report", font=f_body, fill=MD_LINK)
    ly = y + 14
    draw.line([(x0 + lx, ly), (x0 + lx + twidth("analytics-dashboard → Q2 Report", f_body), ly)],
              fill=MD_LINK, width=1)

def markdown_raw(draw, x0, y0, x1, y1, measure=False):
    lines = [
        ("# Q2 Performance Review",                          CODE_BLUE),
        ("*Andrew Bush · June 2026 · v1.2*",                CODE_TEXT),
        ("---",                                              CODE_TEXT),
        ("",                                                 CODE_TEXT),
        ("## Executive Summary",                             CODE_BLUE),
        ("",                                                 CODE_TEXT),
        ("Revenue grew 18 % quarter-on-quarter, driven by", CODE_TEXT),
        ("the EMEA region expansion and the launch of the",  CODE_TEXT),
        ("Atlas assistant tier. Operating costs held flat.",  CODE_TEXT),
        ("",                                                 CODE_TEXT),
        ("## Key Metrics",                                   CODE_BLUE),
        ("",                                                 CODE_TEXT),
        ("- **Revenue**: £4.2 M  (+18 % QoQ)",              CODE_GREEN),
        ("- **MAU**: 12,400  (+31 % QoQ)",                   CODE_GREEN),
        ("- **NPS**: 67  (up from 58 in Q1)",                CODE_GREEN),
        ("- **Uptime**: 99.96 %  (SLA: 99.9 %)",            CODE_GREEN),
        ("",                                                 CODE_TEXT),
        ("## Technical Notes",                               CODE_BLUE),
        ("",                                                 CODE_TEXT),
        ("Cache hit rate reached **48 %** against the",      CODE_TEXT),
        ("`≥ 40 %` target. Full data:",                      CODE_TEXT),
        ("[analytics-dashboard → Q2 Report](https://...)",   CODE_YELLOW),
    ]
    lh, pad = 16, 12
    h = pad*2 + len(lines)*lh
    if measure: return h
    if draw:
        draw.rectangle([x0, y0, x1, y0+h], fill=CODE_BG)
        mf = MONO_(10)
        for i, (txt, col) in enumerate(lines):
            draw.text((x0+12, y0+pad+i*lh), txt, font=mf, fill=col)

def make_markdown():
    PANEL_W = 580
    OUTER   = 36
    GAP     = 48
    W       = OUTER*2 + PANEL_W*2 + GAP

    user_msg = "Can you put together the Q2 performance summary as a document?"
    asst_msg = "Here's the Q2 Performance Review document:"
    title    = "Document"

    probe = Image.new("RGB", (W, 1400), PAGE_BG)
    y_bot, embed_h = paint_thread(probe, OUTER, OUTER, PANEL_W,
                                  user_msg, asst_msg, title,
                                  'rendered', markdown_rendered)
    H = y_bot + OUTER

    img = Image.new("RGB", (W, H), PAGE_BG)
    paint_thread(img, OUTER, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'rendered', markdown_rendered)

    draw = ImageDraw.Draw(img)
    gx = OUTER + PANEL_W + GAP//2
    draw.line([(gx, OUTER+10),(gx, H-OUTER-10)], fill=DIVIDER, width=1)

    paint_thread(img, OUTER+PANEL_W+GAP, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'raw', markdown_raw,
                 fixed_embed_h=embed_h)
    return img


# ═══════════════════════════════════════════════════════════════════════════
#  07 — PDF DOCUMENT ATTACHMENT
# ═══════════════════════════════════════════════════════════════════════════
PDF_PAGE_BG   = (255, 255, 255)
PDF_PAGE_SHD  = (210, 212, 218)
PDF_TOOLBAR   = (245, 246, 248)
PDF_TOOL_BDR  = (224, 226, 230)
PDF_BADGE_BG  = (220,  38,  38)   # red PDF badge
PDF_BADGE_TX  = (255, 255, 255)
PDF_ICON_BG   = (254, 226, 226)   # light red for file icon
PDF_ICON_TX   = (220,  38,  38)
PDF_ATTACH_BG = (249, 250, 251)
PDF_ATTACH_BD = (229, 231, 235)
PDF_BODY_TX   = ( 40,  40,  40)
PDF_BODY_MUT  = (100, 105, 115)
PDF_CTRL      = (120, 125, 135)
PDF_CTRL_HOV  = ( 60,  65,  80)

def _pdf_toolbar(draw, x0, y0, x1, toolbar_h, page, total_pages):
    """Draw a minimal PDF viewer toolbar."""
    draw.rectangle([x0, y0, x1, y0+toolbar_h], fill=PDF_TOOLBAR)
    draw.line([(x0, y0+toolbar_h), (x1, y0+toolbar_h)], fill=PDF_TOOL_BDR, width=1)

    f = fnt(SANS, 11)
    fb = fnt(SANS_BOLD, 11)

    # Left: page indicator
    pg_txt = f"Page {page} of {total_pages}"
    draw.text((x0+10, y0+toolbar_h//2-7), pg_txt, font=f, fill=PDF_CTRL)

    # Center: ‹ › nav arrows
    cx = (x0 + x1) // 2
    draw.text((cx - 28, y0+toolbar_h//2-8), "‹", font=fnt(SANS, 16), fill=PDF_CTRL_HOV)
    draw.text((cx + 16, y0+toolbar_h//2-8), "›", font=fnt(SANS, 16), fill=PDF_CTRL_HOV)

    # Right: zoom label
    draw.text((x1 - 60, y0+toolbar_h//2-7), "100 %  ⊕  ⊖", font=f, fill=PDF_CTRL)

def _pdf_page(draw, img, x0, y0, page_w, page_h):
    """Draw a white page with shadow and realistic document content."""
    # shadow
    draw.rectangle([x0+3, y0+3, x0+page_w+3, y0+page_h+3], fill=PDF_PAGE_SHD)
    # page
    draw.rectangle([x0, y0, x0+page_w, y0+page_h], fill=PDF_PAGE_BG, outline=PDF_TOOL_BDR, width=1)

    # Document content inside page
    px, py = x0 + 18, y0 + 18
    pw = page_w - 36

    f_title = fnt(SANS_BOLD, 11)
    f_h     = fnt(SANS_BOLD, 9)
    f_body  = fnt(SANS,      8)
    f_mute  = fnt(SANS,      7)

    # logo placeholder + title block
    draw.rectangle([px, py, px+28, py+12], fill=(220, 225, 240))
    draw.text((px+32, py+1), "Acme Corporation", font=f_title, fill=PDF_BODY_TX)
    draw.text((px+32, py+13), "Confidential — Internal Use Only", font=f_mute, fill=PDF_BODY_MUT)
    draw.line([(px, py+26), (px+pw, py+26)], fill=PDF_TOOL_BDR, width=1)
    py += 34

    # H1 equivalent
    draw.text((px, py), "Master Services Agreement", font=fnt(SANS_BOLD, 12), fill=PDF_BODY_TX)
    py += 17
    draw.text((px, py), "Effective Date: 1 July 2026  ·  Reference: MSA-2026-0042", font=f_mute, fill=PDF_BODY_MUT)
    py += 16

    # Section heading
    draw.text((px, py), "1.  Definitions", font=f_h, fill=PDF_BODY_TX)
    py += 13

    # Body paragraph (narrow lines for realism)
    para = ("In this Agreement, unless the context otherwise requires, the following terms shall "
            "have the meanings set out below. \"Services\" means the software-as-a-service platform "
            "and any professional services delivered by the Provider under each Order Form.")
    words = para.split()
    line, lines = [], []
    for w in words:
        test = ' '.join(line + [w])
        if twidth(test, f_body) <= pw:
            line.append(w)
        else:
            lines.append(' '.join(line))
            line = [w]
    if line: lines.append(' '.join(line))
    for l in lines[:6]:
        draw.text((px, py), l, font=f_body, fill=PDF_BODY_TX)
        py += 11

    py += 6
    draw.text((px, py), "2.  License Grant", font=f_h, fill=PDF_BODY_TX)
    py += 13
    para2 = ("Subject to the terms of this Agreement and timely payment of all Fees, Provider "
             "grants Customer a non-exclusive, non-transferable, worldwide license to access "
             "and use the Services during the Subscription Term.")
    words2 = para2.split()
    line2, lines2 = [], []
    for w in words2:
        test = ' '.join(line2 + [w])
        if twidth(test, f_body) <= pw:
            line2.append(w)
        else:
            lines2.append(' '.join(line2))
            line2 = [w]
    if line2: lines2.append(' '.join(line2))
    for l in lines2[:4]:
        draw.text((px, py), l, font=f_body, fill=PDF_BODY_TX)
        py += 11

def pdf_rendered(draw, x0, y0, x1, y1, measure=False):
    TOOLBAR_H = 28
    PAGE_W    = x1 - x0 - 20   # centered page with margin
    PAGE_H    = int(PAGE_W * 1.3)
    h = TOOLBAR_H + 12 + PAGE_H + 12
    if measure: return h
    if draw is None: return

    # toolbar
    _pdf_toolbar(draw, x0, y0, x1, TOOLBAR_H, 1, 8)

    # page
    px = x0 + 10
    py = y0 + TOOLBAR_H + 12
    _pdf_page(draw, draw._image if hasattr(draw, '_image') else None,
              px, py, PAGE_W, PAGE_H)

def pdf_raw(draw, x0, y0, x1, y1, measure=False):
    """Raw view — attachment metadata card (no binary content)."""
    CARD_H    = 64
    INFO_H    = 80
    PAD       = 12
    h = PAD + CARD_H + PAD + INFO_H + PAD
    if measure: return h
    if draw is None: return

    # Attachment card
    cy0 = y0 + PAD
    cy1 = cy0 + CARD_H
    rrect(draw, [x0, cy0, x1, cy1], 6, fill=PDF_ATTACH_BG, outline=PDF_ATTACH_BD, lw=1)

    # PDF file icon
    ix0, iy0 = x0+12, cy0+10
    ix1, iy1 = ix0+28, iy0+36
    rrect(draw, [ix0, iy0, ix1, iy1], 3, fill=PDF_ICON_BG)
    # dog-ear
    draw.polygon([(ix1-8,iy0),(ix1,iy0+8),(ix1-8,iy0+8)], fill=(250,200,200))
    draw.line([(ix1-8,iy0),(ix1-8,iy0+8),(ix1,iy0+8)], fill=PDF_ICON_TX, width=1)
    # PDF label
    f_badge = fnt(SANS_BOLD, 8)
    draw.text((ix0+4, iy0+16), "PDF", font=f_badge, fill=PDF_ICON_TX)

    # filename + meta
    fx = ix1 + 12
    draw.text((fx, cy0+10), "MSA-2026-0042.pdf", font=fnt(SANS_BOLD, 12), fill=PDF_BODY_TX)
    draw.text((fx, cy0+27), "8 pages  ·  142 KB  ·  Uploaded 17 Jun 2026",
              font=fnt(SANS, 10), fill=PDF_BODY_MUT)

    # Open / Download buttons
    btn_y = cy0 + 43
    for label, bx in [("Open", fx), ("Download", fx+60)]:
        bw = twidth(label, fnt(SANS, 10)) + 16
        rrect(draw, [bx, btn_y, bx+bw, btn_y+18], 4,
              fill=(255,255,255), outline=PDF_ATTACH_BD, lw=1)
        draw.text((bx+8, btn_y+3), label, font=fnt(SANS, 10), fill=PDF_BODY_TX)

    # Info block
    iy0b = cy1 + PAD
    draw.rectangle([x0, iy0b, x1, iy0b+INFO_H], fill=CODE_BG)
    mf = MONO_(10)
    meta_lines = [
        ("# Attachment metadata",          CODE_TEXT),
        ("filename:  MSA-2026-0042.pdf",   CODE_BLUE),
        ("mime:      application/pdf",     CODE_GREEN),
        ("pages:     8",                   CODE_YELLOW),
        ("size:      142 KB",              CODE_YELLOW),
        ("sha256:    3f9a…c14e",           CODE_TEXT),
    ]
    for i, (txt, col) in enumerate(meta_lines):
        draw.text((x0+12, iy0b+8+i*12), txt, font=mf, fill=col)

def make_pdf():
    PANEL_W = 580
    OUTER   = 36
    GAP     = 48
    W       = OUTER*2 + PANEL_W*2 + GAP

    user_msg = "Here's the master services agreement — can you pull out the key obligations?"
    asst_msg = "I can see the MSA you've attached. Here's the document preview:"
    title    = "PDF Document"

    probe = Image.new("RGB", (W, 1400), PAGE_BG)
    y_bot, embed_h = paint_thread(probe, OUTER, OUTER, PANEL_W,
                                  user_msg, asst_msg, title,
                                  'rendered', pdf_rendered)
    H = y_bot + OUTER

    img = Image.new("RGB", (W, H), PAGE_BG)
    paint_thread(img, OUTER, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'rendered', pdf_rendered)

    draw = ImageDraw.Draw(img)
    gx = OUTER + PANEL_W + GAP//2
    draw.line([(gx, OUTER+10),(gx, H-OUTER-10)], fill=DIVIDER, width=1)

    paint_thread(img, OUTER+PANEL_W+GAP, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'raw', pdf_raw,
                 fixed_embed_h=embed_h)
    return img


# ═══════════════════════════════════════════════════════════════════════════
#  08 — FEEDBACK / DECISION CARD
# ═══════════════════════════════════════════════════════════════════════════
FB_QUESTION  = ( 17,  24,  39)
FB_OPT_BG    = (255, 255, 255)
FB_OPT_BDR   = (209, 213, 219)
FB_OPT_TX    = ( 55,  65,  81)
FB_HOV_BG    = (239, 246, 255)
FB_HOV_BDR   = ( 96, 165, 250)
FB_HOV_TX    = ( 37,  99, 235)
FB_BTN_BG    = ( 37,  99, 235)
FB_BTN_TX    = (255, 255, 255)
FB_SKIP_TX   = (107, 114, 128)

_FB_OPTIONS  = ["PDF Document", "Markdown", "Word Document", "CSV (data only)"]

def feedback_rendered(draw, x0, y0, x1, y1, measure=False):
    W       = x1 - x0
    PAD     = 14
    Q_H     = 22
    GAP     = 12
    OPT_H   = 32
    OPT_GAP = 8
    BTN_H   = 32
    opts_h  = OPT_H * 2 + OPT_GAP
    h = PAD + Q_H + GAP + opts_h + GAP + BTN_H + PAD
    if measure: return h
    if draw is None: return

    y = y0 + PAD
    draw.text((x0, y), "Which export format would you like?",
              font=BOLD(13), fill=FB_QUESTION)
    y += Q_H + GAP

    col_w = (W - OPT_GAP) // 2
    for i, opt in enumerate(_FB_OPTIONS):
        col = i % 2
        row = i // 2
        ox  = x0 + col * (col_w + OPT_GAP)
        oy  = y  + row * (OPT_H  + OPT_GAP)
        hover = (i == 0)
        bg  = FB_HOV_BG  if hover else FB_OPT_BG
        bdr = FB_HOV_BDR if hover else FB_OPT_BDR
        tx  = FB_HOV_TX  if hover else FB_OPT_TX
        fw  = BOLD(12)   if hover else UI(12)
        rrect(draw, [ox, oy, ox+col_w, oy+OPT_H], 5, fill=bg, outline=bdr, lw=1)
        # radio circle
        rc_x, rc_y = ox+13, oy+OPT_H//2
        draw.ellipse([rc_x-6, rc_y-6, rc_x+6, rc_y+6], outline=bdr, width=1, fill=bg)
        if hover:
            draw.ellipse([rc_x-3, rc_y-3, rc_x+3, rc_y+3], fill=FB_HOV_TX)
        draw.text((ox+27, oy+OPT_H//2-7), opt, font=fw, fill=tx)

    y += opts_h + GAP
    btn_w = 120
    rrect(draw, [x0, y, x0+btn_w, y+BTN_H], 5, fill=FB_BTN_BG)
    lbl = "Submit"
    lw = twidth(lbl, BOLD(12))
    draw.text((x0+btn_w//2-lw//2, y+BTN_H//2-8), lbl, font=BOLD(12), fill=FB_BTN_TX)
    draw.text((x0+btn_w+14, y+BTN_H//2-7), "Skip", font=UI(12), fill=FB_SKIP_TX)

def feedback_raw(draw, x0, y0, x1, y1, measure=False):
    lines = [
        ('```feedback-request',                              CODE_TEXT),
        ('{',                                                CODE_TEXT),
        ('  "question": "Which export format',               CODE_BLUE),
        ('             would you like?",',                   CODE_BLUE),
        ('  "options": [',                                   CODE_TEXT),
        ('    { "id": "pdf",  "label": "PDF Document" },',   CODE_GREEN),
        ('    { "id": "md",   "label": "Markdown" },',       CODE_GREEN),
        ('    { "id": "docx", "label": "Word Document" },',  CODE_GREEN),
        ('    { "id": "csv",  "label": "CSV (data only)" }', CODE_GREEN),
        ('  ],',                                             CODE_TEXT),
        ('  "multi":    false,',                             CODE_YELLOW),
        ('  "required": true',                               CODE_YELLOW),
        ('}',                                                CODE_TEXT),
        ('```',                                              CODE_TEXT),
    ]
    lh, pad = 17, 12
    h = pad*2 + len(lines)*lh
    if measure: return h
    if draw:
        draw.rectangle([x0, y0, x1, y0+h], fill=CODE_BG)
        mf = MONO_(10)
        for i, (txt, col) in enumerate(lines):
            draw.text((x0+12, y0+pad+i*lh), txt, font=mf, fill=col)

def make_feedback():
    PANEL_W = 580
    OUTER   = 36
    GAP     = 48
    W       = OUTER*2 + PANEL_W*2 + GAP

    user_msg = "I need to share the Q2 report with the board — what format options are there?"
    asst_msg = "I can export the report in several formats. Which would you prefer?"
    title    = "Decision Card"

    probe = Image.new("RGB", (W, 1000), PAGE_BG)
    y_bot, embed_h = paint_thread(probe, OUTER, OUTER, PANEL_W,
                                  user_msg, asst_msg, title,
                                  'rendered', feedback_rendered)
    H = y_bot + OUTER
    img = Image.new("RGB", (W, H), PAGE_BG)
    paint_thread(img, OUTER, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'rendered', feedback_rendered)
    draw = ImageDraw.Draw(img)
    gx = OUTER + PANEL_W + GAP//2
    draw.line([(gx, OUTER+10),(gx, H-OUTER-10)], fill=DIVIDER, width=1)
    paint_thread(img, OUTER+PANEL_W+GAP, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'raw', feedback_raw,
                 fixed_embed_h=embed_h)
    return img


# ═══════════════════════════════════════════════════════════════════════════
#  09 — WRITE-PROPOSAL CARD
# ═══════════════════════════════════════════════════════════════════════════
WP_BADGE_BG  = (252, 211,  77)
WP_BADGE_TX  = ( 92,  61,   0)
WP_DIFF_HDR  = (243, 244, 246)
WP_DIFF_BDR  = (229, 231, 235)
WP_DIFF_HTXT = ( 75,  85,  99)
WP_KEY_TX    = (107, 114, 128)
WP_VAL_TX    = ( 30,  41,  55)
WP_CHG_BF    = (254, 226, 226)
WP_CHG_AF    = (220, 252, 231)
WP_CHG_TX    = ( 17,  24,  39)
WP_IMPACT    = (107, 114, 128)
WP_TOOL_TX   = ( 37,  99, 235)
WP_BTN_PRI   = ( 37,  99, 235)
WP_BTN_TX    = (255, 255, 255)
WP_BTN_SBDR  = (209, 213, 219)

def write_proposal_rendered(draw, x0, y0, x1, y1, measure=False):
    W          = x1 - x0
    PAD        = 14
    BADGE_H    = 26
    ACT_H      = 22
    TOOL_H     = 20
    GAP        = 10
    DHDR_H     = 22
    DROW_H     = 21
    N_ROWS     = 3
    IMPACT_H   = 20
    BTN_H      = 32
    h = (PAD + BADGE_H + GAP + ACT_H + GAP + TOOL_H + GAP +
         DHDR_H + DROW_H*N_ROWS + GAP + IMPACT_H + GAP + BTN_H + PAD)
    if measure: return h
    if draw is None: return

    y = y0 + PAD

    # Badge + action heading
    badge = "UPDATE"
    bf    = BOLD(9)
    bw    = twidth(badge, bf) + 12
    rrect(draw, [x0, y, x0+bw, y+BADGE_H], 4, fill=WP_BADGE_BG)
    draw.text((x0+6, y+BADGE_H//2-6), badge, font=bf, fill=WP_BADGE_TX)
    y += BADGE_H + GAP

    draw.text((x0, y), "Update target region for campaign CA-2041",
              font=BOLD(13), fill=WP_CHG_TX)
    y += ACT_H + GAP

    draw.text((x0, y), "Tool: ", font=UI(11), fill=WP_KEY_TX)
    tw = twidth("Tool: ", UI(11))
    draw.text((x0+tw, y), "crm.updateCampaign", font=MONO_(11), fill=WP_TOOL_TX)
    y += TOOL_H + GAP

    # Before / after diff table
    col_w = (W - 1) // 2
    # header
    draw.rectangle([x0, y, x1, y+DHDR_H], fill=WP_DIFF_HDR)
    draw.line([(x0+col_w, y),(x0+col_w, y+DHDR_H+DROW_H*N_ROWS)], fill=WP_DIFF_BDR, width=1)
    draw.rectangle([x0, y, x1, y+DHDR_H+DROW_H*N_ROWS], outline=WP_DIFF_BDR, width=1)
    draw.text((x0+8, y+5), "Before", font=BOLD(10), fill=WP_DIFF_HTXT)
    draw.text((x0+col_w+8, y+5), "After", font=BOLD(10), fill=WP_DIFF_HTXT)
    y += DHDR_H

    for key, bval, aval, changed in [
        ("id",     "CA-2041", "CA-2041", False),
        ("region", "AMER",    "EMEA",    True),
        ("status", "draft",   "draft",   False),
    ]:
        bg_b = WP_CHG_BF if changed else (255,255,255)
        bg_a = WP_CHG_AF if changed else (255,255,255)
        draw.rectangle([x0,       y, x0+col_w, y+DROW_H], fill=bg_b)
        draw.rectangle([x0+col_w+1, y, x1,     y+DROW_H], fill=bg_a)
        draw.line([(x0, y+DROW_H),(x1, y+DROW_H)], fill=WP_DIFF_BDR, width=1)
        kf  = UI(10)
        vf  = BOLD(10) if changed else UI(10)
        vtx = WP_CHG_TX if changed else WP_VAL_TX
        kw  = twidth(key+":", kf) + 4
        draw.text((x0+6,        y+5), key+":", font=kf, fill=WP_KEY_TX)
        draw.text((x0+6+kw,     y+5), bval,   font=vf, fill=vtx)
        draw.text((x0+col_w+6,  y+5), key+":", font=kf, fill=WP_KEY_TX)
        draw.text((x0+col_w+6+kw, y+5), aval, font=vf, fill=vtx)
        y += DROW_H

    y += GAP
    draw.text((x0, y), "⚠  1 campaign record will be modified. This action cannot be undone.",
              font=UI(11), fill=WP_IMPACT)
    y += IMPACT_H + GAP

    # Buttons
    pri_w = 140
    rrect(draw, [x0, y, x0+pri_w, y+BTN_H], 5, fill=WP_BTN_PRI)
    lbl  = "Apply changes"
    lw   = twidth(lbl, BOLD(12))
    draw.text((x0+pri_w//2-lw//2, y+BTN_H//2-8), lbl, font=BOLD(12), fill=WP_BTN_TX)
    sx  = x0 + pri_w + 10
    sw  = 76
    rrect(draw, [sx, y, sx+sw, y+BTN_H], 5, fill=WHITE, outline=WP_BTN_SBDR, lw=1)
    lbl2 = "Cancel"
    lw2  = twidth(lbl2, UI(12))
    draw.text((sx+sw//2-lw2//2, y+BTN_H//2-7), lbl2, font=UI(12), fill=WP_VAL_TX)

def write_proposal_raw(draw, x0, y0, x1, y1, measure=False):
    lines = [
        ('```write-proposal',                              CODE_TEXT),
        ('{',                                              CODE_TEXT),
        ('  "operation": "update",',                       CODE_BLUE),
        ('  "action": "Update target region',              CODE_BLUE),
        ('            for campaign CA-2041",',             CODE_BLUE),
        ('  "tool":   "crm.updateCampaign",',              CODE_GREEN),
        ('  "before": {',                                  CODE_TEXT),
        ('    "id":     "CA-2041",',                       CODE_YELLOW),
        ('    "region": "AMER",',                          CODE_YELLOW),
        ('    "status": "draft"',                          CODE_YELLOW),
        ('  },',                                           CODE_TEXT),
        ('  "after": {',                                   CODE_TEXT),
        ('    "id":     "CA-2041",',                       CODE_GREEN),
        ('    "region": "EMEA",',                          CODE_GREEN),
        ('    "status": "draft"',                          CODE_GREEN),
        ('  },',                                           CODE_TEXT),
        ('  "impact": "1 campaign record',                 CODE_TEXT),
        ('            will be modified."',                 CODE_TEXT),
        ('}',                                              CODE_TEXT),
        ('```',                                            CODE_TEXT),
    ]
    lh, pad = 16, 12
    h = pad*2 + len(lines)*lh
    if measure: return h
    if draw:
        draw.rectangle([x0, y0, x1, y0+h], fill=CODE_BG)
        mf = MONO_(10)
        for i, (txt, col) in enumerate(lines):
            draw.text((x0+12, y0+pad+i*lh), txt, font=mf, fill=col)

def make_write_proposal():
    PANEL_W = 580
    OUTER   = 36
    GAP     = 48
    W       = OUTER*2 + PANEL_W*2 + GAP

    user_msg = "Move campaign CA-2041 from AMER to EMEA."
    asst_msg = "I'll update the campaign region. Please review the change before I apply it:"
    title    = "Write Proposal"

    probe = Image.new("RGB", (W, 1200), PAGE_BG)
    y_bot, embed_h = paint_thread(probe, OUTER, OUTER, PANEL_W,
                                  user_msg, asst_msg, title,
                                  'rendered', write_proposal_rendered)
    H = y_bot + OUTER
    img = Image.new("RGB", (W, H), PAGE_BG)
    paint_thread(img, OUTER, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'rendered', write_proposal_rendered)
    draw = ImageDraw.Draw(img)
    gx = OUTER + PANEL_W + GAP//2
    draw.line([(gx, OUTER+10),(gx, H-OUTER-10)], fill=DIVIDER, width=1)
    paint_thread(img, OUTER+PANEL_W+GAP, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'raw', write_proposal_raw,
                 fixed_embed_h=embed_h)
    return img


# ═══════════════════════════════════════════════════════════════════════════
#  10 — TOOL CALL DISCLOSURE
# ═══════════════════════════════════════════════════════════════════════════
DISC_HDR_BG  = (249, 250, 251)
DISC_BDR     = (229, 231, 235)
DISC_OK_BG   = (220, 252, 231)
DISC_OK_TX   = ( 22, 101,  52)
DISC_TOOL    = ( 37,  99, 235)
DISC_KEY     = (107, 114, 128)
DISC_VAL     = ( 30,  41,  55)
DISC_TIME    = (156, 163, 175)
DISC_SECT    = ( 75,  85,  99)

def tool_disclosure_rendered(draw, x0, y0, x1, y1, measure=False):
    HDR_H  = 34
    PAD    = 10
    ROW_H  = 18
    SECT_H = 18
    h = HDR_H + PAD + SECT_H + ROW_H*2 + PAD + 1 + PAD + SECT_H + ROW_H*2 + PAD
    if measure: return h
    if draw is None: return

    y = y0

    # Header
    rrect(draw, [x0, y, x1, y+HDR_H], 5, fill=DISC_HDR_BG, outline=DISC_BDR, lw=1)
    # chevron ▾
    cx_, cy_ = x0+12, y+HDR_H//2
    draw.polygon([(cx_-4,cy_-2),(cx_+4,cy_-2),(cx_,cy_+3)], fill=DISC_KEY)
    # tool name
    tx = x0 + 24
    draw.text((tx, y+HDR_H//2-7), "crm.searchCampaigns", font=MONO_(11), fill=DISC_TOOL)
    tw = twidth("crm.searchCampaigns", MONO_(11))
    # status badge
    bx  = tx + tw + 10
    bgl = "✓  Completed"
    bw  = twidth(bgl, UI(10)) + 14
    bh  = 18
    by_ = y + HDR_H//2 - bh//2
    rrect(draw, [bx, by_, bx+bw, by_+bh], 9, fill=DISC_OK_BG)
    draw.text((bx+7, by_+4), bgl, font=UI(10), fill=DISC_OK_TX)
    # duration
    draw.text((x1-50, y+HDR_H//2-7), "312 ms", font=UI(10), fill=DISC_TIME)

    # Body (white rectangle covering border seam)
    draw.rectangle([x0+1, y+HDR_H-1, x1-1, y+h-1], fill=WHITE)
    draw.rectangle([x0, y+HDR_H, x1, y+h], outline=DISC_BDR, width=1)
    draw.rectangle([x0+1, y+HDR_H, x1-1, y+h-1], fill=WHITE)

    y += HDR_H + PAD

    # Input section
    draw.text((x0+PAD, y), "INPUT", font=BOLD(9), fill=DISC_SECT)
    y += SECT_H
    for key, val in [("status", '"active"'), ("region", '"EMEA"')]:
        draw.text((x0+PAD, y), key+":", font=UI(10), fill=DISC_KEY)
        kw = twidth(key+":", UI(10))
        draw.text((x0+PAD+kw+6, y), val, font=MONO_(10), fill=DISC_VAL)
        y += ROW_H

    y += PAD
    draw.line([(x0+PAD, y),(x1-PAD, y)], fill=DISC_BDR, width=1)
    y += PAD + 1

    # Output section
    draw.text((x0+PAD, y), "OUTPUT", font=BOLD(9), fill=DISC_SECT)
    y += SECT_H
    for key, val in [("items", "Array[4]  — campaigns matching query"),
                     ("total", "4")]:
        draw.text((x0+PAD, y), key+":", font=UI(10), fill=DISC_KEY)
        kw = twidth(key+":", UI(10))
        draw.text((x0+PAD+kw+6, y), val, font=UI(10), fill=DISC_VAL)
        y += ROW_H

    # citation footnote
    draw.text((x0+PAD, y+4),
              "¹  Results cited inline in the response above",
              font=UI(9), fill=DISC_TIME)

def tool_disclosure_raw(draw, x0, y0, x1, y1, measure=False):
    lines = [
        ("// MCP tool call — input",                        CODE_TEXT),
        ('{',                                               CODE_TEXT),
        ('  "tool":   "crm.searchCampaigns",',              CODE_BLUE),
        ('  "input":  {',                                   CODE_TEXT),
        ('    "status": "active",',                         CODE_GREEN),
        ('    "region": "EMEA"',                            CODE_GREEN),
        ('  }',                                             CODE_TEXT),
        ('}',                                               CODE_TEXT),
        ('',                                                CODE_TEXT),
        ("// MCP tool call — output",                       CODE_TEXT),
        ('{',                                               CODE_TEXT),
        ('  "items": [',                                    CODE_BLUE),
        ('    {"id":"CA-2038","name":"EMEA Launch"},',       CODE_YELLOW),
        ('    {"id":"CA-2039","name":"EU Growth"},',         CODE_YELLOW),
        ('    {"id":"CA-2040","name":"DACH Expand"},',       CODE_YELLOW),
        ('    {"id":"CA-2041","name":"UK Scale"}',           CODE_YELLOW),
        ('  ],',                                            CODE_BLUE),
        ('  "total": 4',                                    CODE_GREEN),
        ('}',                                               CODE_TEXT),
    ]
    lh, pad = 16, 12
    h = pad*2 + len(lines)*lh
    if measure: return h
    if draw:
        draw.rectangle([x0, y0, x1, y0+h], fill=CODE_BG)
        mf = MONO_(10)
        for i, (txt, col) in enumerate(lines):
            draw.text((x0+12, y0+pad+i*lh), txt, font=mf, fill=col)

def make_tool_disclosure():
    PANEL_W = 580
    OUTER   = 36
    GAP     = 48
    W       = OUTER*2 + PANEL_W*2 + GAP

    user_msg = "Show me all active campaigns in EMEA."
    asst_msg = ("I searched for active campaigns in EMEA and found 4 results.¹  "
                "Here are the matching campaigns:")
    title    = "Tool Call"

    probe = Image.new("RGB", (W, 1000), PAGE_BG)
    y_bot, embed_h = paint_thread(probe, OUTER, OUTER, PANEL_W,
                                  user_msg, asst_msg, title,
                                  'rendered', tool_disclosure_rendered)
    H = y_bot + OUTER
    img = Image.new("RGB", (W, H), PAGE_BG)
    paint_thread(img, OUTER, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'rendered', tool_disclosure_rendered)
    draw = ImageDraw.Draw(img)
    gx = OUTER + PANEL_W + GAP//2
    draw.line([(gx, OUTER+10),(gx, H-OUTER-10)], fill=DIVIDER, width=1)
    paint_thread(img, OUTER+PANEL_W+GAP, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'raw', tool_disclosure_raw,
                 fixed_embed_h=embed_h)
    return img


# ═══════════════════════════════════════════════════════════════════════════
#  11 — SYNTAX-HIGHLIGHTED CODE BLOCK
# ═══════════════════════════════════════════════════════════════════════════
SYN_KW      = (197, 134, 192)
SYN_STR     = (206, 145, 120)
SYN_CMT     = (106, 153,  85)
SYN_FUNC    = (220, 220, 170)
SYN_TYPE    = ( 78, 201, 176)
SYN_NUM     = (181, 206, 168)
SYN_PUNC    = (204, 204, 204)
SYN_LINE_NO = ( 90,  97, 109)
SYN_LINE_HL = ( 30,  36,  46)
LN_W        = 32

_CODE_LINES = [
    [("// Fetch active campaigns for a tenant", SYN_CMT)],
    [("import ", SYN_KW), ("{ CRMClient } ", CODE_TEXT), ("from ", SYN_KW), ('"@acme/crm-sdk"', SYN_STR), (";", SYN_PUNC)],
    [("", CODE_TEXT)],
    [("async ", SYN_KW), ("function ", SYN_KW), ("getActiveCampaigns", SYN_FUNC), ("(", SYN_PUNC)],
    [("  tenantId", CODE_TEXT), (": ", SYN_PUNC), ("string", SYN_TYPE), (",", SYN_PUNC)],
    [("  region",   CODE_TEXT), (": ", SYN_PUNC), ('"AMER"', SYN_STR), (" | ", SYN_PUNC), ('"EMEA"', SYN_STR), (" | ", SYN_PUNC), ('"APAC"', SYN_STR)],
    [(")", SYN_PUNC), (": ", SYN_PUNC), ("Promise", SYN_TYPE), ("<", SYN_PUNC), ("Campaign", SYN_TYPE), ("[]>", SYN_PUNC), (" {", SYN_PUNC)],
    [("  const ", SYN_KW), ("client ", CODE_TEXT), ("= ", SYN_PUNC), ("new ", SYN_KW), ("CRMClient", SYN_TYPE), ("({ tenantId });", SYN_PUNC)],
    [("  const ", SYN_KW), ("results ", CODE_TEXT), ("= ", SYN_PUNC), ("await ", SYN_KW), ("client.campaigns.", CODE_TEXT), ("list", SYN_FUNC), ("({", SYN_PUNC)],
    [("    status", CODE_TEXT), (": ", SYN_PUNC), ('"active"', SYN_STR), (",", SYN_PUNC)],
    [("    region,", CODE_TEXT)],
    [("    limit",  CODE_TEXT), (": ", SYN_PUNC), ("100", SYN_NUM), (",", SYN_PUNC)],
    [("  });", SYN_PUNC)],
    [("  return ", SYN_KW), ("results.items;", CODE_TEXT)],
    [("}", SYN_PUNC)],
]

def code_rendered(draw, x0, y0, x1, y1, measure=False):
    LH  = 19
    PAD = 12
    h   = PAD*2 + len(_CODE_LINES)*LH
    if measure: return h
    if draw is None: return

    draw.rectangle([x0, y0, x1, y0+h], fill=CODE_BG)
    lang = "TypeScript"
    lf   = UI(10)
    lw_  = twidth(lang, lf)
    draw.text((x1-lw_-6, y0+5), lang, font=lf, fill=SYN_LINE_NO)

    mf = MONO_(11)
    for i, segs in enumerate(_CODE_LINES):
        ry = y0 + PAD + i*LH
        if i == 8:
            draw.rectangle([x0+LN_W+1, ry-1, x1, ry+LH-1], fill=SYN_LINE_HL)
        # line number
        ln  = str(i+1)
        lnw = twidth(ln, mf)
        draw.text((x0+LN_W-lnw-4, ry+1), ln, font=mf, fill=SYN_LINE_NO)
        draw.line([(x0+LN_W, y0),(x0+LN_W, y0+h)], fill=(40,46,56), width=1)
        # tokens
        tx = x0 + LN_W + 10
        for text, col in segs:
            draw.text((tx, ry+1), text, font=mf, fill=col)
            tx += twidth(text, mf)

def code_raw(draw, x0, y0, x1, y1, measure=False):
    raw_lines = [
        ("```typescript",                                   CODE_TEXT),
        ("// Fetch active campaigns for a tenant",          SYN_CMT),
        ('import { CRMClient } from "@acme/crm-sdk";',     CODE_TEXT),
        ("",                                                CODE_TEXT),
        ("async function getActiveCampaigns(",              CODE_TEXT),
        ("  tenantId: string,",                             CODE_TEXT),
        ('  region: "AMER" | "EMEA" | "APAC"',             CODE_TEXT),
        ("): Promise<Campaign[]> {",                        CODE_TEXT),
        ("  const client = new CRMClient({ tenantId });",   CODE_TEXT),
        ("  const results = await client.campaigns.list({", CODE_TEXT),
        ('    status: "active",',                           CODE_TEXT),
        ("    region,",                                     CODE_TEXT),
        ("    limit: 100,",                                 CODE_TEXT),
        ("  });",                                           CODE_TEXT),
        ("  return results.items;",                         CODE_TEXT),
        ("}",                                               CODE_TEXT),
        ("```",                                             CODE_TEXT),
    ]
    lh, pad = 17, 12
    h = pad*2 + len(raw_lines)*lh
    if measure: return h
    if draw:
        draw.rectangle([x0, y0, x1, y0+h], fill=CODE_BG)
        mf = MONO_(10)
        for i, (txt, col) in enumerate(raw_lines):
            draw.text((x0+12, y0+pad+i*lh), txt, font=mf, fill=col)

def make_code():
    PANEL_W = 580
    OUTER   = 36
    GAP     = 48
    W       = OUTER*2 + PANEL_W*2 + GAP

    user_msg = "Write a TypeScript function to fetch active campaigns for a tenant."
    asst_msg = "Here's an async function using the CRM SDK that filters by status and region:"
    title    = "Code Block"

    probe = Image.new("RGB", (W, 1000), PAGE_BG)
    y_bot, embed_h = paint_thread(probe, OUTER, OUTER, PANEL_W,
                                  user_msg, asst_msg, title,
                                  'rendered', code_rendered)
    H = y_bot + OUTER
    img = Image.new("RGB", (W, H), PAGE_BG)
    paint_thread(img, OUTER, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'rendered', code_rendered)
    draw = ImageDraw.Draw(img)
    gx = OUTER + PANEL_W + GAP//2
    draw.line([(gx, OUTER+10),(gx, H-OUTER-10)], fill=DIVIDER, width=1)
    paint_thread(img, OUTER+PANEL_W+GAP, OUTER, PANEL_W,
                 user_msg, asst_msg, title, 'raw', code_raw,
                 fixed_embed_h=embed_h)
    return img


# ── Run ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    renders = {
        "01-mermaid":         make_mermaid,
        "02-vega-lite":       make_vegalite,
        "03-data-table":      make_table,
        "04-json-inspector":  make_json,
        "05-math":            make_math,
        "06-markdown":        make_markdown,
        "07-pdf":             make_pdf,
        "08-feedback-card":   make_feedback,
        "09-write-proposal":  make_write_proposal,
        "10-tool-disclosure": make_tool_disclosure,
        "11-code-block":      make_code,
    }
    for name, fn in renders.items():
        path = os.path.join(OUT_DIR, f"{name}.png")
        fn().save(path)
        print(f"  ✓  {path}")
