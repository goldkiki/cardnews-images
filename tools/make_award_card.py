"""라운드 MVP(농구는 MVP·MIP) 카드 1장을 그린다. RULES.md 3-12 참고.

usage: python3 make_award_card.py <설정 json> <출력 png>

설정 json 예:
{
  "sport": "volleyball",                    # basketball | volleyball
  "title": "2026-27 V-리그 여자부 · 2라운드",   # 상단 흰 박스 대회명
  "heading": "1라운드 MVP",
  "sub": "한국배구연맹 발표",                  # 발표 주체·날짜 (확인된 것만)
  "rows": [                                 # 1명(배구) 또는 2명(농구 MVP·MIP)
    {"award": "MVP", "name": "최정민", "team": "IBK기업은행",
     "emblem": "ibk_altos", "outline": false,
     "photo": "players/xxx.png",            # 없으면 생략 → 엠블럼을 크게 넣는다
     "lines": ["기록 한 줄", "기록 한 줄"]}     # 두 곳 이상 확인된 것만, 3줄까지
  ]
}
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

SK = "/root/.claude/skills/synced/cb94fcbf-0c60-4c80-8390-fd8ace2f3e41_81959943-3978-4796-8e6d-d6065c67dbbf"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = json.load(open(sys.argv[1], encoding="utf-8"))
OUT = sys.argv[2]

W, H = 1080, 1350
NAVY, YEL, WHITE = "#1B2A52", "#FFE678", "#FFFFFF"
BOX = "#4A247A" if C["sport"] == "basketball" else "#0C6E77"
NOTO = f"{SK}/card-news-fonts/assets/noto_sans_cjk_kr_bold.otf"


def font(s):
    return ImageFont.truetype(NOTO, s)


def tsize(t, f):
    b = f.getbbox(t)
    return b[2] - b[0], b[3] - b[1], b


def draw_c(d, cx, cy, t, f, fill):
    w, h, b = tsize(t, f)
    d.text((cx - w / 2 - b[0], cy - h / 2 - b[1]), t, font=f, fill=fill)


def draw_l(d, x, cy, t, f, fill):
    w, h, b = tsize(t, f)
    d.text((x - b[0], cy - h / 2 - b[1]), t, font=f, fill=fill)


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


def emblem(name, area, ol):
    im = load(f"{SK}/card-news-logos/assets/teams/{name}.png")
    r = im.width / im.height
    h = (area / r) ** 0.5
    im = im.resize((round(h * r), round(h)), Image.LANCZOS)
    return outline(im) if ol else im


bg = Image.open(f"{SK}/26-27-womens-{C['sport']}-card-news/assets/court_background.png").convert("RGB")
s = max(W / bg.width, H / bg.height)
bg = bg.resize((round(bg.width * s), round(bg.height * s)), Image.LANCZOS)
l, t = (bg.width - W) // 2, (bg.height - H) // 2
im = bg.crop((l, t, l + W, t + H)).convert("RGBA")
d = ImageDraw.Draw(im)
d.rounded_rectangle((100, 64, 980, 160), 48, fill=WHITE)
draw_c(d, 540, 112, C["title"], font(44), NAVY)
d.rounded_rectangle((100, 290, 980, 1220), 48, fill=BOX)

rows = C["rows"]
ROW_H, ROW_GAP = 330, 34
total = 56 + 18 + 32 + 36 + len(rows) * ROW_H + (len(rows) - 1) * ROW_GAP
y = 290 + (930 - total) / 2
draw_c(d, 540, y + 28, C["heading"], font(56), YEL)
y += 56 + 18
draw_c(d, 540, y + 16, C.get("sub", ""), font(28), WHITE)
y += 32 + 36

for row in rows:
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle((140, y, 940, y + ROW_H), 32, fill=(255, 255, 255, 30))
    im.alpha_composite(ov)
    d = ImageDraw.Draw(im)
    if row.get("photo"):
        p = Image.open(os.path.join(REPO, row["photo"])).convert("RGBA").resize((180, 180), Image.LANCZOS)
        im.alpha_composite(p, (170, round(y + 40)))
        e = emblem(row["emblem"], 70 * 70, row.get("outline"))
        im.alpha_composite(e, (round(260 - e.width / 2), round(y + 235)))
    else:
        e = emblem(row["emblem"], 190 * 190, row.get("outline"))
        im.alpha_composite(e, (round(260 - e.width / 2), round(y + ROW_H / 2 - e.height / 2)))
    tx = 400
    f40 = font(40)
    draw_l(d, tx, y + 52, row["award"], f40, YEL)
    w, _, _ = tsize(row["award"], f40)
    draw_l(d, tx + w + 18, y + 52, row["name"], f40, WHITE)
    draw_l(d, tx, y + 108, row["team"], font(32), WHITE)
    for i, ln in enumerate(row.get("lines", [])[:3]):
        draw_l(d, tx, y + 168 + i * 52, ln, font(30), WHITE)
    y += ROW_H + ROW_GAP

im.convert("RGB").save(OUT)
print("ok", OUT)
