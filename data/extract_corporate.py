# -*- coding: utf-8 -*-
"""CR6 포트폴리오명 추적 → 기업 부문 합계행만 합산 (EAD·RWA·EL)."""
import fitz, re, json, io
BANKS={"115":"KB국민","117":"신한","114":"하나","112":"우리","102":"IBK기업",
 "103":"NH농협","101":"KDB산업","122":"부산","126":"경남","104":"수협","123":"광주","124":"제주"}
def num(s):
    s=s.replace(",","").replace("%","").strip()
    return float(s) if re.fullmatch(r"-?\d+(\.\d+)?", s) else None
def lines_of(doc): return [l.strip() for i in range(doc.page_count) for l in doc[i].get_text().split("\n") if l.strip()]

def is_corp_header(t):  # t: 공백제거
    if len(t)>14: return False
    if any(x in t for x in ["소매","주거용","기타","적격회전","주식","집합투자","유동화","파생","정부","은행","합계","소계","총"]): return False
    return any(x in t for x in ["대기업","중소기업","기업형","일반기업","소기업"]) or t=="기업"
def is_other_header(t):
    if len(t)>16: return False
    return any(x in t for x in ["소매","주거용","기타소매","적격회전","주식","집합투자","유동화","장외파생","특수금융"])

def extract(L):
    cur_corp=False; EAD=RWA=EL=0.0; parts=[]
    i=0
    while i<len(L):
        t=L[i].replace(" ","")
        if is_corp_header(t): cur_corp=True; cur_name=t
        elif is_other_header(t): cur_corp=False
        elif (t=="합계" or t=="소계") :
            nums=[]; j=i
            # 같은 줄 + 이후
            for tok in re.split(r"[/\s%]+", L[i]):
                v=num(tok)
                if v is not None: nums.append(v)
            j=i+1
            while j<len(L) and len(nums)<12:
                nxt=L[j].replace(" ","")
                if is_corp_header(nxt) or is_other_header(nxt): break  # 다음 포트폴리오 시작
                for tok in re.split(r"[/\s%]+", L[j]):
                    v=num(tok)
                    if v is not None: nums.append(v)
                    if len(nums)>=12: break
                j+=1
            if len(nums)>=11:
                e,r,el,pd,lgd,rw=nums[3],nums[8],nums[10],nums[4],nums[6],nums[9]
                if 0<=pd<=100 and 0<=lgd<=100 and 0<=rw<=1500 and e>100 and r>10 and cur_corp:
                    EAD+=e; RWA+=r; EL+=el; parts.append((cur_name,e,r,el))
            cur_corp=False
        i+=1
    return EAD,RWA,EL,parts

res={}; log=io.open("real_extract3.txt","w",encoding="utf-8")
def w(s=""): log.write(s+"\n"); print(s)
w(f"{'은행':<9}{'기업EAD(조)':>11}{'기업RWA(조)':>11}{'평균RW':>8}{'EL률':>7}{'구성':>5}")
w("-"*52)
for code,name in BANKS.items():
    doc=fitz.open(f"{code}_risk.pdf"); L=lines_of(doc)
    EAD,RWA,EL,parts=extract(L)
    avgrw=RWA/EAD if EAD else None; elr=EL/EAD if EAD else None
    res[code]=dict(name=name,EAD=EAD,RWA=RWA,EL=EL,avgrw=avgrw,elr=elr,parts=parts)
    g=lambda x:f"{x/10000:.1f}" if x else "—"
    w(f"{name:<9}{g(EAD):>11}{g(RWA):>11}{(avgrw or 0):>7.1%}{(elr or 0):>7.2%}{len(parts):>5}")
json.dump(res,open("real_corp.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
log.close()
w(""); w("[구성 상세]")
for code,r in res.items():
    if r.get('parts'):
        w(r['name']+": "+", ".join(p[0]+"(RWA%.1f조)"%(p[2]/10000) for p in r['parts']))
print("→ real_corp.json")
