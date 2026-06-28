# -*- coding: utf-8 -*-
"""12개 은행 '리스크관리' 연말(4분기) 보고서 다운로드 (내부등급법 상세 포함)."""
import subprocess, re, urllib.parse, os, time

UA="Mozilla/5.0"; REF="https://www.kfb.or.kr/"
BANKS={"115":"KB국민","117":"신한","114":"하나","112":"우리","102":"IBK기업",
 "103":"NH농협","101":"KDB산업","122":"부산","126":"경남","104":"수협","123":"광주","124":"제주"}

def curl_t(url,ref=None):
    c=["curl","-sL","-k","-A",UA,"--max-time","40"]
    if ref:c+=["-e",ref]
    return subprocess.run(c+[url],capture_output=True).stdout.decode("euc-kr","ignore")
def curl_b(url,out,ref):
    subprocess.run(["curl","-sL","-k","-A",UA,"-e",ref,"--max-time","90",url,"-o",out])

ok=[]
for code,name in BANKS.items():
    got=False
    for yr in ["2025","2024"]:
        view=curl_t(f"https://www.kfb.or.kr/publicdata/business_regular_view.php?code={code}&data_year={yr}",REF)
        # 리스크관리, 가장 최근 분기(4>3>2>1) 우선
        cand=re.findall(r'href=\"(\.\./include/download\.php\?enc_para=[^\"]+)\"[^>]*title=\"리스크관리\s*(\d)분기\s*\[([^\]]+)\]',view)
        if not cand: continue
        cand.sort(key=lambda x:-int(x[1]))  # 4분기 우선
        link,q,fn=cand[0]
        dl="https://www.kfb.or.kr/include/download.php?enc_para="+link.split("enc_para=")[1]
        html=curl_t(dl,REF); m=re.search(r'location\.href=\"([^\"]+)\"',html)
        if not m: continue
        pr=urllib.parse.urlparse(m.group(1)); qs=urllib.parse.parse_qs(pr.query)
        f=qs.get("filename",[""])[0]; e=urllib.parse.quote(f,encoding="euc-kr")
        url=f'{pr.scheme}://{pr.netloc}{pr.path}?filename={e}&path={urllib.parse.quote(qs.get("path",["open/upload_file2/"])[0])}&realfile={e}'
        out=f"{code}_risk.pdf"; curl_b(url,out,REF)
        sz=os.path.getsize(out) if os.path.exists(out) else 0
        if sz>50000 and open(out,'rb').read(5)==b'%PDF-':
            print(f"{name:<9} {yr} {q}분기  {sz:,}B  OK ({fn[:40]})"); ok.append(code); got=True; break
    if not got: print(f"{name:<9} 실패")
    time.sleep(0.3)
print("\n성공:",len(ok),"/",len(BANKS))
import json; json.dump(ok,open("risk_ok.json","w"))
