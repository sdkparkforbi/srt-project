# -*- coding: utf-8 -*-
"""SEC-SA(표준법) vs SEC-IRBA(기본내부등급법) 자본경감 비교.
 동일 K=평균RW*8%, 동일 트렌치. 차이는 감독계수 p (SA: p=1, IRBA: 산식).
 데이터: FISIS 검증 12개 은행 (총RWA·CET1) + 공시 자산유형별 RWA."""
import math, json, io

# name, corp, oret, spec, total_rwa(억,FISIS), cet1(FISIS 2025Q4)
BANKS=[
 ("기업은행",1590965,132986,101917,2640865,11.48),
 ("신한",     985948,548219,203168,2301064,14.57),
 ("산업은행",1063867, 10686,513310,3585085,13.40),
 ("국민",     978209,263138, 86218,2407399,14.91),
 ("하나",     944226,255339,145911,2051350,16.42),
 ("우리",     742160,229403, 59634,1861435,14.13),
 ("농협",     409616,262095, 40465,1485726,15.23),
 ("부산",     173225, 51818, 24099, 358681,14.61),
 ("경남",     105763, 46348, 36158, 246840,12.86),
 ("수협",     101532, 18564, 46119, 210878,16.66),
 ("광주",      55451, 33493, 11918, 146805,14.92),
 ("제주",      14205, 11204,  4934,  37027,13.32),
]
AVGRW=dict(corp=0.75,oret=0.75,spec=1.00)
# SEC-IRBA p 계수 (CRR Art.259 / Basel CRE44), 선순위 트렌치
IRBA_P={  # [A,B,C,D,E], LGD, retail?
 "corp":dict(A=0,B=3.56,C=-1.85,D=0.55,E=0.07, LGD=0.45, N=100, retail=False),
 "spec":dict(A=0,B=3.56,C=-1.85,D=0.55,E=0.07, LGD=0.45, N=100, retail=False),
 "oret":dict(A=0,B=0,  C=-7.48,D=0.71,E=0.24, LGD=0.45, N=100, retail=True),
}
M_T=5.0  # 트렌치 만기(1~5), 보수적
FL=(0.0,0.02); MEZZ=(0.02,0.12); SEN=(0.12,1.0); RW_FLOOR=0.15

def kssfa(KA,A,D,p):
    a=-1.0/(p*KA); u=D-KA; l=max(A-KA,0.0)
    return (math.exp(a*u)-math.exp(a*l))/(a*(u-l))
def tranche_rw(KA,A,D,p):
    if D<=KA: return 12.5
    if A>=KA: return max(kssfa(KA,A,D,p)*12.5, RW_FLOOR)
    return (KA-A)/(D-A)*12.5+(D-KA)/(D-A)*max(kssfa(KA,KA,D,p)*12.5,RW_FLOOR)
def p_irba(key,KIRB):
    c=IRBA_P[key]
    p=c["A"]+c["B"]/c["N"]+c["C"]*KIRB+c["D"]*c["LGD"]+c["E"]*M_T
    return max(0.30,p)
def relief(key, avgrw, fl_top, method):
    KA=avgrw*0.08; EAD=1.0/avgrw
    p = 1.0 if method=="SA" else p_irba(key,KA)
    sen=(SEN[0],SEN[1]); flr=(0.0,fl_top)
    post=(flr[1]-flr[0])*EAD*tranche_rw(KA,flr[0],flr[1],p)+(sen[1]-sen[0])*EAD*tranche_rw(KA,sen[0],sen[1],p)
    return (1-post), p

out=io.open("../srt-study/data/secirba_results.txt","w",encoding="utf-8") if False else io.open("secirba_results.txt","w",encoding="utf-8")
def w(s=""): out.write(s+"\n"); print(s)

w("="*78)
w("자산군별 경감률 & 선순위 p (기본 시나리오: 우선손실 2% 보유)")
w(f"{'자산군':<10}{'평균RW':>7}{'SA경감':>9}{'IRBA경감':>9}{'IRBA_p':>8}")
for key in ["corp","oret","spec"]:
    rsa,_=relief(key,AVGRW[key],0.02,"SA")
    rib,p=relief(key,AVGRW[key],0.02,"IRBA")
    w(f"{key:<10}{AVGRW[key]:>6.0%}{max(0,rsa):>9.1%}{max(0,rib):>9.1%}{p:>8.3f}")

w("\n"+"="*92)
w("은행별 ΔRWA(주택담보 제외, 기본 시나리오) — SA vs IRBA, 단위 조원")
w(f"{'은행':<9}{'총RWA':>9}{'CET1':>6}{'ΔRWA_SA':>9}{'ΔRWA_IRBA':>11}{'CET1_SA':>8}{'CET1_IRBA':>10}")
w("-"*92)
rSA={k:relief(k,AVGRW[k],0.02,"SA")[0] for k in AVGRW}
rIB={k:relief(k,AVGRW[k],0.02,"IRBA")[0] for k in AVGRW}
aggSA=aggIB=aggT=0; rows=[]
for name,corp,oret,spec,tot,cet1 in BANKS:
    dSA=corp*rSA["corp"]+oret*rSA["oret"]+spec*rSA["spec"]
    dIB=corp*rIB["corp"]+oret*rIB["oret"]+spec*rIB["spec"]
    cetSA=cet1/100*tot/(tot-dSA)*100; cetIB=cet1/100*tot/(tot-dIB)*100
    rows.append(dict(name=name,total=tot,cet1=cet1,dSA=dSA,dIB=dIB,cetSA=round(cetSA,2),cetIB=round(cetIB,2),
                     upSA=round(cetSA-cet1,2),upIB=round(cetIB-cet1,2)))
    aggSA+=dSA; aggIB+=dIB; aggT+=tot
    w(f"{name:<9}{tot/10000:>8.1f}조{cet1:>6.1f}{dSA/10000:>8.1f}조{dIB/10000:>10.1f}조{cetSA:>8.2f}{cetIB:>10.2f}")
w("-"*92)
w(f"합계  ΔRWA  SA {aggSA/10000:>6.0f}조(자본 {aggSA*0.08/10000:.1f}조)  |  IRBA {aggIB/10000:>6.0f}조(자본 {aggIB*0.08/10000:.1f}조)")
w(f"평균 CET1 상승  SA +{sum(r['upSA'] for r in rows)/len(rows):.2f}%p  |  IRBA +{sum(r['upIB'] for r in rows)/len(rows):.2f}%p")
json.dump({"asset_relief":{k:{"SA":rSA[k],"IRBA":rIB[k]} for k in AVGRW},
           "rows":rows,"aggSA":aggSA,"aggIB":aggIB,"aggT":aggT},
          open("secirba_results.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
out.close(); print("→ secirba_results.json")
