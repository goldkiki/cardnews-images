import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SK = "/root/.claude/skills/synced/cb94fcbf-0c60-4c80-8390-fd8ace2f3e41_81959943-3978-4796-8e6d-d6065c67dbbf"
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

W, H = 1080, 1350
NAVY = "#1B2A52"; BOX = "#4A247A"; YEL = "#FFE678"; WHITE = "#FFFFFF"
GIMPO = f"{SK}/card-news-fonts/assets/gimpo_title.ttf"
NOTO = f"{SK}/card-news-fonts/assets/noto_sans_cjk_kr_bold.otf"
F = {}
def font(path, size):
    k = (path, size)
    if k not in F: F[k] = ImageFont.truetype(path, size)
    return F[k]

def trim(im):
    return im.crop(im.split()[-1].getbbox())

def load(p): return trim(Image.open(p).convert("RGBA"))

bg0 = Image.open(f"{SK}/26-27-womens-basketball-card-news/assets/court_background.png").convert("RGB")
s = max(W / bg0.width, H / bg0.height)
bg0 = bg0.resize((round(bg0.width * s), round(bg0.height * s)), Image.LANCZOS)
l = (bg0.width - W) // 2; t = (bg0.height - H) // 2
BG = bg0.crop((l, t, l + W, t + H)).convert("RGBA")

def outline(im, px=3):
    a = im.split()[-1]
    big = a.filter(ImageFilter.MaxFilter(px * 2 + 1))
    base = Image.new("RGBA", im.size, (255, 255, 255, 0)); base.putalpha(big)
    pad = Image.new("RGBA", (im.width, im.height), (0, 0, 0, 0))
    pad.alpha_composite(base); pad.alpha_composite(im)
    return pad

def padded(im, px):
    p = Image.new("RGBA", (im.width + 2 * px, im.height + 2 * px), (0, 0, 0, 0)); p.paste(im, (px, px)); return p

WOORI = load(f"{SK}/card-news-logos/assets/teams/woori_bank.png")
KB = load(f"{SK}/card-news-logos/assets/teams/kb_stars.png")
WKBL = load(f"{SK}/card-news-logos/assets/tournaments/wkbl_2026_27.png")
CH = {n: load(f"{SK}/kiki-characters/assets/basketball/{n}.png") for n in ["kiki_dribble_1", "kiki_hoodie_hold_1", "kiki_dream_hold_1"]}

def emblem_pair(area):
    # equal visible area; woori gets thin white outline (dark emblem on purple)
    def sz(im):
        r = im.width / im.height; h = (area / r) ** 0.5; return (round(h * r), round(h))
    w = WOORI.resize(sz(WOORI), Image.LANCZOS)
    w = outline(padded(w, 4), 3)
    k = KB.resize(sz(KB), Image.LANCZOS)
    return w, k

def by_h(im, h): return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
def by_w(im, w): return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)

def text_size(txt, f):
    b = f.getbbox(txt); return b[2] - b[0], b[3] - b[1], b

def draw_text_c(d, cx, top, txt, f, fill):
    w, h, b = text_size(txt, f)
    d.text((cx - w / 2 - b[0], top - b[1]), txt, font=f, fill=fill)
    return h

def base_card(title):
    im = BG.copy(); d = ImageDraw.Draw(im)
    d.rounded_rectangle((100, 64, 980, 160), 48, fill=WHITE)
    f = font(NOTO, 44); w, h, b = text_size(title, f)
    d.text((540 - w / 2 - b[0], 64 + (96 - h) / 2 - b[1]), title, font=f, fill=NAVY)
    return im, d

TITLE = "2026-27 WKBL 정규리그"

# block layout: items = (kind, payload, height, gap_after)
def layout(im, d, items, y0, y1):
    total = sum(h + g for _, _, h, g in items) - items[-1][3]
    y = y0 + (y1 - y0 - total) / 2
    for kind, p, h, g in items:
        if kind == "text":
            txt, f, fill = p; draw_text_c(d, 540, y, txt, f, fill)
        elif kind == "img":
            im.alpha_composite(p, (round(540 - p.width / 2), round(y)))
        elif kind == "fn":
            p(im, d, y)
        y += h + g

def T(txt, size, fill, g, fp=NOTO):
    f = font(fp, size); _, h, _ = text_size(txt, f)
    return ("text", (txt, f, fill), h, g)

# ---------- 01 cover ----------
im, d = base_card(TITLE)
logo = by_w(WKBL, 190); im.alpha_composite(logo, (540 - logo.width // 2, 188))
for cy, txt in ((372, "11월 9일"), (464, "경기 결과")):
    f = font(GIMPO, 72); w, h, b = text_size(txt, f); d.text((540 - w / 2 - b[0], cy - h / 2 - b[1]), txt, font=f, fill=NAVY)
d.rounded_rectangle((100, 525, 980, 975), 48, fill=BOX)
layout(im, d, [
    T("우리은행 57 : 51 KB스타즈", 46, WHITE, 26),
    T("전반 31-29 · 후반 26-22", 36, WHITE, 22),
    T("강이슬 결장에도 원정에서 승리", 34, WHITE, 18),
    T("김단비 15점 14리바운드 더블더블", 34, WHITE, 28),
    T("우리은행 2연승!", 46, YEL, 22),
    T("김단비 역대 3호 통산 8000점", 36, YEL, 0),
], 525, 975)
c = by_h(CH["kiki_dribble_1"], 290); im.alpha_composite(c, (540 - c.width // 2, 1000))
im.convert("RGB").save(f"{OUT}/01.png")

# ---------- 02 result ----------
im, d = base_card(TITLE)
d.rounded_rectangle((100, 290, 980, 1220), 48, fill=BOX)
we, ke = emblem_pair(160 * 160)
EH = max(we.height, ke.height)
def score_row(im, d, y):
    im.alpha_composite(we, (250 - we.width // 2, round(y + (EH - we.height) / 2)))
    im.alpha_composite(ke, (830 - ke.width // 2, round(y + (EH - ke.height) / 2)))
    f = font(NOTO, 100); w, h, b = text_size("57 : 51", f)
    d.text((540 - w / 2 - b[0], y + (EH - h) / 2 - b[1]), "57 : 51", font=f, fill=YEL)
    f2 = font(NOTO, 42)
    for cx, nm in ((250, "우리은행"), (830, "KB스타즈")):
        draw_text_c(d, cx, y + EH + 20, nm, f2, WHITE)
NAMEH = text_size("우리은행", font(NOTO, 42))[1]
def boxes(im, d, y):
    labels = [("전반", "31-29"), ("후반", "26-22")]
    bw, gap = 200, 13; tot = len(labels) * bw + (len(labels) - 1) * gap; x = 540 - tot / 2
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for i in range(len(labels)):
        od.rounded_rectangle((x + i * (bw + gap), y, x + i * (bw + gap) + bw, y + 100), 16, fill=(255, 255, 255, 46))
    im.alpha_composite(ov)
    for i, (a, b2) in enumerate(labels):
        cx = x + i * (bw + gap) + bw / 2
        draw_text_c(d, cx, y + 12, a, font(NOTO, 31), YEL)
        draw_text_c(d, cx, y + 52, b2, font(NOTO, 46), WHITE)
ch = by_h(CH["kiki_hoodie_hold_1"], 150)
layout(im, d, [
    T("11월 9일 · 청주체육관", 32, YEL, 34),
    ("fn", score_row, EH + 20 + NAMEH, 30),
    ("fn", boxes, 100, 14),
    T("점수는 우리은행 - KB스타즈 순", 24, WHITE, 34),
    T("주요 선수 기록", 36, YEL, 18),
    T("우리은행 김단비 15점 14리바운드 · 이명관 14점", 31, WHITE, 12),
    T("KB스타즈 허예은 10점 4어시스트", 31, WHITE, 26),
    ("img", ch, ch.height, 0),
], 290, 1220)
im.convert("RGB").save(f"{OUT}/02.png")

# ---------- 03 flow ----------
im, d = base_card(TITLE)
d.rounded_rectangle((100, 290, 980, 1220), 48, fill=BOX)
ws, ks = emblem_pair(100 * 100)
SH = max(ws.height, ks.height)
def vs_row(im, d, y):
    im.alpha_composite(ws, (250 - ws.width // 2, round(y + (SH - ws.height) / 2)))
    im.alpha_composite(ks, (830 - ks.width // 2, round(y + (SH - ks.height) / 2)))
    f = font(NOTO, 54); w, h, b = text_size("VS", f); d.text((540 - w / 2 - b[0], y + (SH - h) / 2 - b[1]), "VS", font=f, fill=YEL)
layout(im, d, [
    ("fn", vs_row, SH, 26),
    T("이렇게 이겼다", 66, WHITE, 34),
    T("전반 31-29", 36, YEL, 14),
    T("이명관이 1쿼터부터 공격을 이끌었고", 30, WHITE, 10),
    T("김단비는 전반 2점으로 숨을 골랐다", 30, WHITE, 30),
    T("3쿼터", 36, YEL, 14),
    T("김단비가 3쿼터에만 7점을 올리며 주도권", 30, WHITE, 10),
    T("이 쿼터에 WKBL 역대 3호 통산 8000점", 30, WHITE, 30),
    T("4쿼터 · 최종 57-51", 36, YEL, 14),
    T("변하정·이명관의 3점슛으로 달아났고", 30, WHITE, 10),
    T("KB스타즈의 4점 차 추격을 끝까지 막아냈다", 30, WHITE, 0),
], 290, 1220)
im.convert("RGB").save(f"{OUT}/03.png")

# ---------- 04 closing ----------
im, d = base_card(TITLE)
d.rounded_rectangle((100, 290, 980, 1220), 48, fill=BOX)
ch = by_h(CH["kiki_dream_hold_1"], 295)
layout(im, d, [
    T("우리은행 2연승!", 52, YEL, 30),
    T("우리은행 57 : 51 KB스타즈", 38, WHITE, 18),
    T("강이슬 결장에도 원정에서 승리", 38, WHITE, 18),
    T("김단비 역대 3호 통산 8000점", 38, WHITE, 34),
    T("다음 경기 결과도 황금키키와 함께해요", 32, WHITE, 40),
    ("img", ch, ch.height, 0),
], 290, 1220)
im.convert("RGB").save(f"{OUT}/04.png")
print("ok")
