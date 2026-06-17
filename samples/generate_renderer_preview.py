"""
Generates renderer preview PNGs showing each content type inline within a
chat thread, the way it would appear in Claude Desktop or the AI Chat Platform.

Each PNG shows two chat thread panels side by side:
  Left  — Raw state   (pill: Raw active)
  Right — Rendered state (pill: Rendered active)

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
WHITE        = (255, 255, 255)
THREAD_BG    = (255, 255, 255)        # chat background
MSG_BG       = (255, 255, 255)        # assistant message bg (same as thread)
USER_MSG_BG  = (246, 247, 249)        # user bubble
BORDER       = (218, 220, 224)
CARD_BG      = (255, 255, 255)
CARD_HEADER  = (250, 251, 252)
TEXT_DARK    = ( 32,  33,  36)
TEXT_MID     = ( 95,  99, 104)
TEXT_LIGHT   = (154, 160, 166)
AVATAR_USER  = (168, 85, 247)         # purple
AVATAR_ASST  = ( 26, 127,  55)        # green (brand-neutral)
CODE_BG      = ( 30,  31,  41)
CODE_TEXT    = (248, 248, 242)
CODE_PINK    = (255, 121, 198)
CODE_YELLOW  = (241, 250, 140)
CODE_CYAN    = (139, 233, 253)
CODE_GREEN   = ( 80, 250, 123)
CODE_PURPLE  = (189, 147, 249)
CODE_ORANGE  = (255, 184, 108)
NODE_FILL    = (232, 240, 254)
NODE_BORDER  = ( 66, 133, 244)
ARROW_COL    = (100, 116, 139)
PILL_REND    = ( 66, 133, 244)        # blue — rendered active
PILL_RAW     = ( 32,  33,  36)        # dark — raw active
PILL_IDLE    = (241, 243, 244)
PILL_BORDER  = (218, 220, 224)
PILL_ON      = (255, 255, 255)
PILL_OFF     = ( 95,  99, 104)
BADGE_REND   = (232, 240, 254)
BADGE_RAW    = (241, 243, 244)
BADGE_REND_T = ( 26,  86, 219)
BADGE_RAW_T  = ( 95,  99, 104)
DIVIDER_COL  = (229, 231, 235)

# ── Fonts ──────────────────────────────────────────────────────────────────
def fnt(path, size):
    try:   return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()

UI   = lambda s: fnt(SANS, s)
BOLD = lambda s: fnt(SANS_BOLD, s)
MONO_F = lambda s: fnt(MONO, s)

# ── Helpers ────────────────────────────────────────────────────────────────
def tw(draw_or_font, text, font=None):
    f = font if font else draw_or_font
    bb = f.getbbox(text)
    return bb[2] - bb[0]

def rrect(draw, xy, r, fill=None, outline=None, lw=1):
    x0,y0,x1,y1 = xy
    if fill:
        draw.rectangle([x0+r,y0,x1-r,y1], fill=fill)
        draw.rectangle([x0,y0+r,x1,y1-r], fill=fill)
        for ex,ey in [(x0,y0),(x1-2*r,y0),(x0,y1-2*r),(x1-2*r,y1-2*r)]:
            draw.ellipse([ex,ey,ex+2*r,ey+2*r], fill=fill)
    if outline:
        for a0,a1,ex,ey in [(180,270,x0,y0),(270,360,x1-2*r,y0),
                             (90,180,x0,y1-2*r),(0,90,x1-2*r,y1-2*r)]:
            draw.arc([ex,ey,ex+2*r,ey+2*r], a0, a1, fill=outline, width=lw)
        draw.line([x0+r,y0,x1-r,y0], fill=outline, width=lw)
        draw.line([x0+r,y1,x1-r,y1], fill=outline, width=lw)
        draw.line([x0,y0+r,x0,y1-r], fill=outline, width=lw)
        draw.line([x1,y0+r,x1,y1-r], fill=outline, width=lw)

def avatar(draw, cx, cy, r, color, initial):
    draw.ellipse([cx-r,cy-r,cx+r,cy+r], fill=color)
    f = BOLD(r-1)
    iw = tw(None, initial, f)
    draw.text((cx-iw//2, cy-r//2-1), initial, font=f, fill=WHITE)

def wrapped_text(draw, text, x, y, max_w, font, color=TEXT_DARK, line_h=19):
    words = text.split()
    line, lines = [], []
    for w in words:
        test = ' '.join(line + [w])
        if tw(None, test, font) <= max_w:
            line.append(w)
        else:
            if line: lines.append(' '.join(line))
            line = [w]
    if line: lines.append(' '.join(line))
    for i, l in enumerate(lines):
        draw.text((x, y + i*line_h), l, font=font, fill=color)
    return y + len(lines) * line_h

def arrow_h(draw, x0, y, x1, color=ARROW_COL, head=7):
    if x1 <= x0+head: return
    draw.line([(x0,y),(x1-head,y)], fill=color, width=2)
    draw.polygon([(x1-head,y-head//2),(x1,y),(x1-head,y+head//2)], fill=color)

def node(draw, cx, cy, w, h, label, r=5):
    x0,y0 = cx-w//2, cy-h//2
    rrect(draw, [x0,y0,x0+w,y0+h], r, fill=NODE_FILL, outline=NODE_BORDER, lw=2)
    f = BOLD(12)
    iw = tw(None, label, f)
    draw.text((cx-iw//2, cy-8), label, font=f, fill=TEXT_DARK)

# ── Card chrome ────────────────────────────────────────────────────────────
HDR_H  = 38
PILL_W = 116
PILL_H = 24
CARD_R = 8

def render_card(draw, img, x0, y0, card_w, title, active_side, content_fn):
    """
    Draw a renderer card at (x0, y0) with width card_w.
    content_fn(draw, cx0, cy0, cx1, cy1) draws the card body.
    Returns bottom y of card.
    """
    # measure content height by calling with a dummy
    probe_img = Image.new("RGB", (card_w, 600), WHITE)
    probe_draw = ImageDraw.Draw(probe_img)
    content_h = content_fn(probe_draw, 0, 0, card_w, 600, measure=True)

    total_h = HDR_H + 8 + content_h + 12   # header + badge gap + content + bottom pad
    x1, y1 = x0+card_w, y0+total_h

    # card shadow
    for i in range(4,0,-1):
        rrect(draw, [x0+i,y0+i,x1+i,y1+i], CARD_R, fill=(0,0,0,7))

    # card body
    rrect(draw, [x0,y0,x1,y1], CARD_R, fill=CARD_BG, outline=BORDER, lw=1)

    # header
    draw.rectangle([x0+1,y0+1,x1-1,y0+HDR_H], fill=CARD_HEADER)
    draw.line([(x0,y0+HDR_H),(x1,y0+HDR_H)], fill=BORDER, width=1)

    # title
    draw.text((x0+12, y0+11), title, font=BOLD(12), fill=TEXT_DARK)

    # pill
    px = x1 - PILL_W - 10
    py = y0 + (HDR_H - PILL_H)//2
    hw = PILL_W // 2
    rrect(draw, [px,py,px+PILL_W,py+PILL_H], PILL_H//2, fill=PILL_IDLE, outline=PILL_BORDER, lw=1)
    pf = UI(10)
    if active_side == 'rendered':
        rrect(draw, [px,py,px+hw,py+PILL_H], PILL_H//2, fill=PILL_REND)
        draw.text((px+6,  py+7), "Rendered", font=pf, fill=PILL_ON)
        draw.text((px+hw+6, py+7), "Raw",    font=pf, fill=PILL_OFF)
    else:
        rrect(draw, [px+hw,py,px+PILL_W,py+PILL_H], PILL_H//2, fill=PILL_RAW)
        draw.text((px+6,  py+7), "Rendered", font=pf, fill=PILL_OFF)
        draw.text((px+hw+6, py+7), "Raw",    font=pf, fill=PILL_ON)

    # state badge
    badge_txt  = "Rendered" if active_side=='rendered' else "Raw"
    badge_fill = BADGE_REND  if active_side=='rendered' else BADGE_RAW
    badge_col  = BADGE_REND_T if active_side=='rendered' else BADGE_RAW_T
    bf = UI(10)
    bw = tw(None, badge_txt, bf) + 14
    bx, by = x0+10, y0+HDR_H+6
    rrect(draw, [bx,by,bx+bw,by+16], 3, fill=badge_fill)
    draw.text((bx+7, by+3), badge_txt, font=bf, fill=badge_col)

    # content area
    cy0 = y0 + HDR_H + 28
    content_fn(draw, x0+1, cy0, x1-1, y1-1, measure=False)

    return y1

# ── Thread painter ─────────────────────────────────────────────────────────
AV_R    = 14
AV_COL  = 20     # avatar left margin
MSG_L   = AV_COL + AV_R*2 + 10
THREAD_PAD = 20

def paint_thread(img, tx, ty, tw_px, user_text, asst_text, card_title,
                 active_side, content_fn, bg=THREAD_BG):
    """
    Paint a chat thread into img at (tx,ty) with width tw_px.
    Returns bottom y.
    """
    draw = ImageDraw.Draw(img)
    x = tx
    y = ty
    max_msg_w = tw_px - MSG_L - THREAD_PAD

    # ── User message ──────────────────────────────────────────────────────
    avatar(draw, x + AV_COL + AV_R, y + AV_R, AV_R, AVATAR_USER, "U")
    draw.text((x + MSG_L, y + 2), "You", font=BOLD(12), fill=TEXT_DARK)
    y_end = wrapped_text(draw, user_text, x+MSG_L, y+18, max_msg_w, UI(13), TEXT_MID)
    y = y_end + 22

    # separator
    draw.line([(x+THREAD_PAD, y),(x+tw_px-THREAD_PAD, y)], fill=DIVIDER_COL, width=1)
    y += 18

    # ── Assistant message ─────────────────────────────────────────────────
    avatar(draw, x + AV_COL + AV_R, y + AV_R, AV_R, AVATAR_ASST, "A")
    draw.text((x + MSG_L, y + 2), "Assistant", font=BOLD(12), fill=TEXT_DARK)
    y += 20
    y_end = wrapped_text(draw, asst_text, x+MSG_L, y, max_msg_w, UI(13), TEXT_MID)
    y = y_end + 14

    # ── Inline card ───────────────────────────────────────────────────────
    card_w = tw_px - MSG_L - THREAD_PAD
    y_bot = render_card(draw, img, x+MSG_L, y, card_w, card_title, active_side, content_fn)

    return y_bot + THREAD_PAD

# ── Content functions ──────────────────────────────────────────────────────
def mermaid_raw(draw, x0, y0, x1, y1, measure=False):
    lines = [
        ("```mermaid",           CODE_TEXT),
        ("flowchart LR",         CODE_PINK),
        ("",                     CODE_TEXT),
        ("    A[Data Sources]",  CODE_CYAN),
        ("    B[Transform]",     CODE_CYAN),
        ("    C[Output]",        CODE_CYAN),
        ("",                     CODE_TEXT),
        ("    A --> B --> C",    CODE_YELLOW),
        ("```",                  CODE_TEXT),
    ]
    lh, pad = 18, 14
    h = pad*2 + len(lines)*lh
    if measure: return h
    draw.rectangle([x0,y0,x1,y1], fill=CODE_BG)
    mf = MONO_F(12)
    for i,(txt,col) in enumerate(lines):
        draw.text((x0+14, y0+pad+i*lh), txt, font=mf, fill=col)

def mermaid_rendered(draw, x0, y0, x1, y1, measure=False):
    h = 160
    if measure: return h
    draw.rectangle([x0,y0,x1,y1], fill=WHITE)
    pcx = (x0+x1)//2
    pcy = y0 + h//2
    nw, nh, gap = 96, 36, 38
    n1x = pcx - nw - gap
    n3x = pcx + nw + gap
    for nx,lbl in [(n1x,"Data Sources"),(pcx,"Transform"),(n3x,"Output")]:
        node(draw, nx, pcy, nw, nh, lbl)
    arrow_h(draw, n1x+nw//2, pcy, pcx-nw//2)
    arrow_h(draw, pcx+nw//2, pcy, n3x-nw//2)

# ═══════════════════════════════════════════════════════════════════════════
#  01 — MERMAID
# ═══════════════════════════════════════════════════════════════════════════
def make_mermaid():
    PANEL_W = 440
    GAP     = 32
    MARGIN  = 24
    W = MARGIN*2 + PANEL_W*2 + GAP

    user_msg = "Can you show me a simple data pipeline diagram?"
    asst_msg = "Here's a flowchart showing the three stages of the pipeline:"
    title    = "Mermaid Diagram"

    # Probe height for left panel
    probe = Image.new("RGB", (W, 900), THREAD_BG)
    y_bot = paint_thread(probe, MARGIN, MARGIN, PANEL_W, user_msg, asst_msg,
                         title, 'raw', mermaid_raw, bg=THREAD_BG)
    H = y_bot + MARGIN

    img = Image.new("RGB", (W, H), THREAD_BG)

    # Left — Raw
    paint_thread(img, MARGIN, MARGIN, PANEL_W, user_msg, asst_msg,
                 title, 'raw', mermaid_raw)

    # Right — Rendered
    paint_thread(img, MARGIN+PANEL_W+GAP, MARGIN, PANEL_W, user_msg, asst_msg,
                 title, 'rendered', mermaid_rendered)

    # Thin gap divider
    draw = ImageDraw.Draw(img)
    gx = MARGIN + PANEL_W + GAP//2
    draw.line([(gx, MARGIN+20),(gx, H-MARGIN-20)], fill=DIVIDER_COL, width=1)

    return img

# ── Run ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    renders = {"01-mermaid": make_mermaid}
    for name, fn in renders.items():
        path = os.path.join(OUT_DIR, f"{name}.png")
        fn().save(path)
        print(f"  ✓  {path}")
