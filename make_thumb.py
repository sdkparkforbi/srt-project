# -*- coding: utf-8 -*-
"""답변서·프로젝트 허브 썸네일(1200x630)."""
from PIL import Image, ImageDraw, ImageFont
mb="C:/Windows/Fonts/malgunbd.ttf"; mr="C:/Windows/Fonts/malgun.ttf"
def F(p,s): return ImageFont.truetype(p,s)
def grad(d,W,H,top,bot):
    for y in range(H):
        t=y/H
        d.line([(0,y),(W,y)],fill=tuple(int(top[k]+(bot[k]-top[k])*t) for k in range(3)))

# 1) 답변서 썸네일
W,H=1200,630
img=Image.new("RGB",(W,H),"#16305c"); d=ImageDraw.Draw(img)
grad(d,W,H,(29,59,110),(16,48,92))
d.rectangle([0,0,14,H],fill="#b3261e")
d.text((70,60),"검토의견 답변서 · RESPONSE TO REVIEW · 2026",font=F(mb,22),fill="#9fc0ee")
d.text((70,108),"중요위험이전(SRT) 연구",font=F(mb,52),fill="#fff")
d.text((70,172),"검토의견 8개 항목 답변",font=F(mb,52),fill="#fff")
d.text((70,256),"수신: 금융감독원 은행리스크검사2팀",font=F(mr,25),fill="#cdddf5")
# 8 points chips
pts=["①범위·시스템리스크","②표준법/내부등급법 구분","③기본·적극 차이","④10/30/50% 이전 시나리오",
     "⑤RWA 증감 분해","⑥유럽사례 비교","⑦신규 대출여력","⑧시스템리스크 통제"]
x0,y0=70,320;
for i,p in enumerate(pts):
    cx=x0+(i%2)*560; cy=y0+(i//2)*52
    d.rounded_rectangle([cx,cy,cx+540,cy+42],radius=10,fill="#1b3a72",outline="#2f5596",width=1)
    d.text((cx+16,cy+9),p,font=F(mr,21),fill="#e8eefb")
img.save("assets/response_thumb.png","PNG"); print("response_thumb OK")

# 2) 프로젝트 허브 썸네일
img=Image.new("RGB",(W,H),"#16305c"); d=ImageDraw.Draw(img)
grad(d,W,H,(29,59,110),(16,48,92))
d.text((70,84),"SRT RESEARCH PROJECT · 2026",font=F(mb,24),fill="#9fc0ee")
d.text((70,140),"중요위험이전(SRT) 합성증권화의",font=F(mb,50),fill="#fff")
d.text((70,202),"국내 은행 자본경감 효과",font=F(mb,50),fill="#fff")
d.text((70,286),"논문 · 그림책 · 검토의견 답변서 — 한곳에",font=F(mr,28),fill="#cdddf5")
# three cards
cards=[("📄","실증분석 논문"),("🐻","그림책 해설"),("📝","검토의견 답변서")]
for i,(ic,t) in enumerate(cards):
    cx=70+i*360
    d.rounded_rectangle([cx,380,cx+330,540],radius=16,fill="#1b3a72",outline="#2f5596",width=2)
    d.text((cx+24,404),ic,font=F(mr,46),fill="#fff")
    d.text((cx+24,478),t,font=F(mb,28),fill="#7fd1c7")
img.save("assets/project_thumb.png","PNG"); print("project_thumb OK")
