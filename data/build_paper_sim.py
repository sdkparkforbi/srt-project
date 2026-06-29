# -*- coding: utf-8 -*-
"""논문 재산출 — 답변서 방식: 실측 평균RW + 우선손실=예상손실 고정 + 이전비중(10/30/50%).
 검증 데이터(bank_data.csv)만 사용. SEC-SA(SSFA, p=1) 선순위 하한 15%."""
import math, csv, io, json

SEN_FLOOR=0.15; P=1.0
def kssfa(KA,A,D,p):
    a=-1.0/(p*KA); u=D-KA; l=max(A-KA,0.0)
    return (math.exp(a*u)-math.exp(a*l))/(a*(u-l))
def trw(KA,A,D,p=P):
    if D<=KA: return 12.5
    if A>=KA: return max(kssfa(KA,A,D,p)*12.5, SEN_FLOOR)
    return (KA-A)/(D-A)*12.5+(D-KA)/(D-A)*max(kssfa(KA,KA,D,p)*12.5,SEN_FLOOR)
def relief(avgrw, fl, transfer):
    """우선손실[0,fl] 보유 + 메자닌[fl,fl+transfer] 이전 + 선순위[fl+transfer,1] 보유."""
    KA=avgrw*0.08; EAD=1.0/avgrw; sen_lo=fl+transfer
    post=fl*EAD*trw(KA,0.0,fl)+(1.0-sen_lo)*EAD*trw(KA,sen_lo,1.0)
    return 1.0-post

# 검증 데이터
rows=list(csv.DictReader(io.open("bank_data.csv",encoding="utf-8-sig")))
def f(x):
    try: return float(x)
    except: return None

TRANSFERS=[0.10,0.30,0.50]; BASE=0.30
print("="*96)
print("표2용 — 자산군별 평균RW(실측)별 경감률 (우선손실=예상손실 1% 고정)")
print(f"{'자산군(실측 평균RW)':<22}{'이전10%':>9}{'이전30%':>9}{'이전50%':>9}")
for label,rw,el in [("기업 (43%)",0.43,0.010),("기타소매 (30%)",0.30,0.012),("주택담보 (15%)",0.15,0.004),("특수금융·표준 (100%)",1.00,0.010)]:
    print(f"{label:<22}"+"".join(f"{relief(rw,el,t):>9.1%}" for t in TRANSFERS))

print("\n"+"="*96)
print("표3용 — 은행별 기업 ΔRWA (기본=이전비중 30%, 우선손실=각 은행 예상손실), 단위 조원")
print(f"{'은행':<9}{'기업RWA':>9}{'평균RW':>7}{'경감률':>7}{'ΔRWA':>8}{'총RWA':>8}{'CET1':>6}{'新CET1':>7}{'+%p':>6}")
agg_d=agg_corp=0; cet_ups=[]; tbl=[]
for r in rows:
    name=r["은행명"]; cls=r["분류"]; rwa=f(r["기업RWA(억원)"]); arw=f(r["평균위험가중치"]); el=f(r["예상손실률"]) or 0.01
    tot=f(r["총위험가중자산(억원,FISIS)"]); cet1=f(r["보통주자본비율(%,FISIS)"])
    if cls!="실측" or not rwa or not arw:
        tbl.append(dict(name=name,skip=True,cls=cls,tot=tot,cet1=cet1)); continue
    rel=relief(arw, el, BASE); d=rwa*rel
    newcet=cet1*tot/(tot-d); up=newcet-cet1
    agg_d+=d; agg_corp+=rwa; cet_ups.append(up)
    tbl.append(dict(name=name,rwa=rwa,arw=arw,rel=rel,d=d,tot=tot,cet1=cet1,newcet=newcet,up=up))
    print(f"{name:<9}{rwa/10000:>8.1f}조{arw:>7.1%}{rel:>7.1%}{d/10000:>7.1f}조{tot/10000:>7.1f}조{cet1:>6.1f}{newcet:>7.2f}{up:>+6.2f}")
print("-"*96)
print(f"합계/평균  기업RWA {agg_corp/10000:.0f}조  ΔRWA {agg_d/10000:.0f}조(자본 {agg_d*0.08/10000:.1f}조)  평균 CET1 +{sum(cet_ups)/len(cet_ups):.2f}%p  (이전비중 30% 기준)")

# 이전비중별 합산 ΔRWA
print("\n이전비중별 합산 기업 ΔRWA:")
for t in TRANSFERS:
    tot_d=sum((f(r['기업RWA(억원)'])*relief(f(r['평균위험가중치']), f(r['예상손실률']) or 0.01, t)) for r in rows if r['분류']=='실측' and f(r['기업RWA(억원)']) and f(r['평균위험가중치']))
    print(f"  이전 {t:>3.0%}: ΔRWA {tot_d/10000:>5.0f}조 (자본 {tot_d*0.08/10000:.1f}조)")

# 표4 민감도 — 기업 평균RW 36~75%, 기본 이전 30%
print("\n표4용 — 기업 평균RW 민감도 (이전비중 30%, 우선손실 1%):")
for rw in [0.36,0.43,0.51,0.65,0.75]:
    print(f"  평균RW {rw:>4.0%} → 경감률 {relief(rw,0.01,BASE):>6.1%}")

json.dump({"tbl":[t for t in tbl],"agg_d":agg_d,"agg_corp":agg_corp,
           "cet_up_avg":sum(cet_ups)/len(cet_ups),"cet_up_min":min(cet_ups),"cet_up_max":max(cet_ups)},
          io.open("paper_sim.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
print("\n→ paper_sim.json")
