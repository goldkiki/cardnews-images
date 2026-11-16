"""라운드 순위표 카드 1장을 그린다. RULES.md 3-10 참고.

usage: python3 make_standings_card.py <설정 json> <출력 png>

설정 json 예:
{
  "sport": "basketball",                # basketball | volleyball
  "title": "2026-27 WKBL 정규리그",       # 상단 흰 박스 대회명
  "heading": "1라운드 최종 순위",
  "asof": "11월 18일 경기까지",
  "last_col": "승률",                     # 농구는 "승률", 배구는 "승점"
  "rows": [                               # 순위 순서대로
    {"rank": 1, "file": "samsung_life", "name": "삼성생명", "g": 5, "w": 4, "l": 1, "last": "0.800", "outline": true},
    ...
  ]
}
"""
import json
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SK = "/root/.claude/skills/synced/cb94fcbf-0c60-4c80-8390-fd8ace2f3e41_81959943-3978-4796-8e6d-d6065c67dbbf"
C = json.load(open(sys.argv[1], encoding="utf-8"))
OUT = sys.argv[2]

W, H = 1080, 1350
NAVY, YEL, WHITE = "#1B2A52", "#FFE678", "#FFFFFF"
BOX = "#4A247A" if C["sport"] == "basketball" else "#0C6E77"
BG_PATH = f"{SK}/26-27-womens-{C['sport']}-card-news/assets/court_background.png"
NOTO = f"{SK}/card-news-fonts/assets/noto_sans_cjk_kr_bold.otf"


def font(size):
    return ImageFont.truetype(NOTO, size)


def text_size(txt, f):
    b = f.getbbox(txt)
    return b[2] - b[0], b[3] - b[1], b


def draw_c(d, cx, cy, txt, f, fill):
    """cx, cy를 글자가 실제로 차지하는 영역의 가운데로 맞춰 그린다."""
    w, h, b = text_size(txt, f)
    d.text((cx - w / 2 - b[0], cy - h / 2 - b[1]), txt, font=f, fill=fill)


def load(p):
    im = Image.open(p).convert("RGBA")
    return im.crop(im.split()[-1].getbbox())


def outline(im, px=3):
    pad = Image.new("RGBA", (im.width + 2 * (px + 2), im.height + 2 * (px + 2)), (0, 0, 0, 0))
    pad.paste(im, (px + 2, px + 2))
    a = pad.split()[-1].filter(ImageFilter.MaxFilter(px * 2 + 1))
    base = Image.new("RGBA", pad.size, (255, 255, 255, 0))
    base.putalpha(a)
    base.alpha_composite(pad)
    return base


def emblem(row, area):
    im = load(f"{SK}/card-news-logos/assets/teams/{row['file']}.png")
    r = im.width / im.height
    h = (area / r) ** 0.5
    im = im.resize((round(h * r), round(h)), Image.LANCZOS)
    return outline(im) if row.get("outline") else im


# 배경과 상단 대회명 박스 (결과 카드와 같은 틀)
bg = Image.open(BG_PATH).convert("RGB")
s = max(W / bg.width, H / bg.height)
bg = bg.resize((round(bg.width * s), round(bg.height * s)), Image.LANCZOS)
l, t = (bg.width - W) // 2, (bg.height - H) // 2
im = bg.crop((l, t, l + W, t + H)).convert("RGBA")
d = ImageDraw.Draw(im)
d.rounded_rectangle((100, 64, 980, 160), 48, fill=WHITE)
draw_c(d, 540, 112, C["title"], font(44), NAVY)
d.rounded_rectangle((100, 290, 980, 1220), 48, fill=BOX)

rows = C["rows"]
ROW_H = 88 if len(rows) <= 6 else 82
HEAD_H, GAP1, GAP2, COLHEAD_H = 60, 14, 36, 44
total = HEAD_H + GAP1 + 40 + GAP2 + COLHEAD_H + 8 + ROW_H * len(rows)
y = 290 + (930 - total) / 2

draw_c(d, 540, y + HEAD_H / 2, C["heading"], font(52), YEL)
y += HEAD_H + GAP1
draw_c(d, 540, y + 20, C["asof"], font(28), WHITE)
y += 40 + GAP2

# 열 가운데 x: 순위, 엠블럼, 팀명(왼쪽 정렬 시작), 경기, 승, 패, 마지막 열
X_RANK, X_EMB, X_NAME = 160, 240, 290
X_G, X_W, X_L, X_LAST = 610, 690, 770, 880
f_head = font(28)
for x, label in ((X_RANK, "순위"), (X_G, "경기"), (X_W, "승"), (X_L, "패"), (X_LAST, C["last_col"])):
    draw_c(d, x, y + COLHEAD_H / 2, label, f_head, YEL)
w, h, b = text_size("팀", f_head)
d.text((X_NAME - b[0], y + COLHEAD_H / 2 - h / 2 - b[1]), "팀", font=f_head, fill=YEL)
y += COLHEAD_H + 8

ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
od = ImageDraw.Draw(ov)
for i in range(len(rows)):
    if i % 2 == 0:
        ry = y + i * ROW_H
        od.rounded_rectangle((120, ry + 4, 960, ry + ROW_H - 4), 16, fill=(255, 255, 255, 34))
im.alpha_composite(ov)
d = ImageDraw.Draw(im)

f_num, f_name = font(34), font(34)
for i, row in enumerate(rows):
    cy = y + i * ROW_H + ROW_H / 2
    top = row["rank"] == 1
    draw_c(d, X_RANK, cy, str(row["rank"]), f_num, YEL if top else WHITE)
    e = emblem(row, (ROW_H - 26) ** 2)
    im.alpha_composite(e, (round(X_EMB - e.width / 2), round(cy - e.height / 2)))
    w, h, b = text_size(row["name"], f_name)
    d.text((X_NAME - b[0], cy - h / 2 - b[1]), row["name"], font=f_name, fill=YEL if top else WHITE)
    for x, key in ((X_G, "g"), (X_W, "w"), (X_L, "l"), (X_LAST, "last")):
        draw_c(d, x, cy, str(row[key]), f_num, YEL if top else WHITE)

im.convert("RGB").save(OUT)
print("ok", OUT)
