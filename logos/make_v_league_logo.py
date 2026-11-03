import glob, random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
S=glob.glob('/root/.claude/skills/synced/*/')[0]
GT=S+'card-news-fonts/assets/gimpo_title.ttf'
random.seed(7)
def mask(txt,size):
    f=ImageFont.truetype(GT,size); b=f.getbbox(txt)
    m=Image.new('L',(b[2]-b[0]+4,b[3]-b[1]+4),0)
    ImageDraw.Draw(m).text((2-b[0],2-b[1]),txt,font=f,fill=255); return m
def gold_line(txt,size,stroke):
    m=mask(txt,size); w,h=m.size; pad=stroke+16
    M=Image.new('L',(w+2*pad,h+2*pad),0); M.paste(m,(pad,pad))
    # gradient: light top -> rich gold -> dark amber bottom, with a bright band
    g=Image.new('RGB',M.size); px=g.load()
    stops=[(0,(255,244,170)),(0.35,(255,206,60)),(0.55,(236,160,20)),(0.78,(255,205,70)),(1,(196,120,10))]
    H=M.height
    for y in range(H):
        t=y/(H-1)
        for i in range(len(stops)-1):
            if stops[i][0]<=t<=stops[i+1][0]:
                a,c0=stops[i]; b,c1=stops[i+1]; k=(t-a)/(b-a)
                c=tuple(int(c0[j]+(c1[j]-c0[j])*k) for j in range(3)); break
        for x in range(M.width): px[x,y]=c
    fill=g.convert('RGBA'); fill.putalpha(M)
    # inner highlight (top-left bevel) & shade
    blur=M.filter(ImageFilter.GaussianBlur(3))
    hi=ImageChops.subtract(M,ImageChops.offset(blur,3,3)).point(lambda v:min(255,v*3))
    hl=Image.new('RGBA',M.size,(255,255,235,0)); hl.putalpha(ImageChops.multiply(hi,M)); fill.alpha_composite(hl)
    # thin darker gold rim
    rim=ImageChops.subtract(M,M.filter(ImageFilter.MinFilter(9)))
    rm=Image.new('RGBA',M.size,(150,84,4,0)); rm.putalpha(rim.point(lambda v:min(255,int(v*1.2)))); fill.alpha_composite(rm)
    # white outline
    ow=M.filter(ImageFilter.MaxFilter(stroke*2+1))
    nw=M.filter(ImageFilter.MaxFilter((stroke+7)*2+1))
    big=Image.new('RGBA',(M.width+16,M.height+16),(0,0,0,0)); 
    nv=Image.new('RGBA',M.size,(0,0,0,0)); nv.paste(Image.new('RGBA',M.size,(6,62,69,255)),(0,0),nw)
    out=nv
    out.paste(Image.new('RGBA',M.size,(255,255,255,255)),(0,0),ow)
    out.alpha_composite(fill); return out
def sparkle(d,x,y,r,a=255):
    pts=[]
    for i in range(8):
        ang=i*math.pi/4; rad=r if i%2==0 else r*0.22
        pts.append((x+rad*math.cos(ang),y+rad*math.sin(ang)))
    d.polygon(pts,fill=(255,196,40,a),outline=(190,110,5,255))
    pts2=[(x+(p[0]-x)*0.5,y+(p[1]-y)*0.5) for p in pts]
    d.polygon(pts2,fill=(255,252,230,a))
l1=gold_line('2026-27',110,17); l2=gold_line('V-리그 여자부',230,26)
gap=-16
W=max(l1.width,l2.width)+80; H=l1.height+l2.height+gap+80
im=Image.new('RGBA',(W,H),(0,0,0,0))
im.alpha_composite(l1,((W-l1.width)//2,30)); im.alpha_composite(l2,((W-l2.width)//2,30+l1.height+gap))
a=im.split()[3]; sh=Image.new('RGBA',im.size,(120,80,10,0))
sh.putalpha(a.point(lambda v:int(v*0.40)).filter(ImageFilter.GaussianBlur(9)))
out=Image.new('RGBA',im.size,(0,0,0,0)); out.alpha_composite(sh,(0,10)); out.alpha_composite(im)
# sparkles on letters (only where opaque)
d=ImageDraw.Draw(out)
sp=[(0.05,0.32,34),(0.97,0.36,38),(0.27,0.88,24),(0.74,0.93,28),(0.80,0.10,22)]
for fx,fy,r in sp:
    sparkle(d,int(W*fx),int(H*fy),r)
out=out.crop(out.getbbox()); out.save('v_league_gold4.png'); print(out.size)
# cover
exec(open('make.py').read().split('# ---------- 1 cover')[0])
im=base(); d=ImageDraw.Draw(im)
w=400; lg=out.resize((w,round(out.height*w/out.width)),Image.LANCZOS); print(lg.height)
im.alpha_composite(lg,(540-w//2,186))
ctext(d,540,358,"IBK기업은행 홈 개막전",font(GT,64),NAVY)
ctext(d,540,450,"11월 3일 경기 결과",font(GT,64),NAVY)
box(im,100,525,980,975); d=ImageDraw.Draw(im)
ctext(d,540,625,'IBK기업은행 3 : 0 현대건설',font(NB,44),WHITE)
for i,s_ in enumerate(['1세트 25 - 23','2세트 25 - 23','3세트 25 - 20']): ctext(d,540,695+i*56,s_,font(NB,36),WHITE)
ctext(d,540,880,'마나베 감독 정규리그 데뷔승!',font(NB,37),YEL)
paste_c(im,char('jersey_cheer_1',290),540,1040)
im.convert('RGB').save('cover_gold4.png')
im.convert('RGB').crop((200,170,880,330)).resize((1360,320),Image.LANCZOS).save('crop_gold4.png')
