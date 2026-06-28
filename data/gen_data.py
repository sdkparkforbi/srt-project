# -*- coding: utf-8 -*-
"""점검용 데이터셋(CSV) 및 검증 페이지(data.html) 생성."""
import csv, io

# 은행코드(은행연합회 통일공시 view), 은행명, 분류, 기업EAD, 기업RWA, 평균RW, 예상손실률, 총RWA(FISIS), CET1(FISIS)
# 단위: 억원. 실측=리스크관리 공시 직접추출, 추정=평균RW 42% 적용, 표준법=IRB 미적용
ROWS=[
 ("115","KB국민","실측",1389480,568815,0.409,0.0060,2407399,14.91),
 ("117","신한","실측",1759383,632943,0.360,0.0047,2301064,14.57),
 ("114","하나","실측",1614543,624946,0.387,0.0061,2051350,16.42),
 ("112","우리","실측",1507651,584233,0.388,0.0062,1861435,14.13),
 ("102","IBK기업","실측",2616625,1321566,0.505,0.0113,2640865,11.48),
 ("103","NH농협","실측",763085,330599,0.433,0.0093,1485726,15.23),
 ("101","KDB산업","실측",1309097,539442,0.412,0.0064,3585085,13.40),
 ("104","수협","실측",175317,85043,0.485,0.0116,210878,16.66),
 ("122","부산","실측",330036,159984,0.485,0.0119,358681,14.61),
 ("126","경남","추정",None,105763,0.42,0.008,246840,12.86),
 ("123","광주","추정",None,55451,0.42,0.008,146805,14.92),
 ("124","제주","표준법",None,None,None,None,37027,13.32),
]
HDR=["은행코드","은행명","분류","기업EAD(억원)","기업RWA(억원)","평균위험가중치","예상손실률","총위험가중자산(억원,FISIS)","보통주자본비율(%,FISIS)","통일공시_링크"]
def url(code): return f"https://www.kfb.or.kr/publicdata/business_regular_view.php?code={code}"

with io.open("bank_data.csv","w",encoding="utf-8-sig",newline="") as f:
    w=csv.writer(f); w.writerow(HDR)
    for code,name,cls,ead,rwa,arw,elr,tot,cet1 in ROWS:
        w.writerow([code,name,cls,
            "" if ead is None else int(ead),
            "" if rwa is None else int(rwa),
            "" if arw is None else arw,
            "" if elr is None else elr,
            int(tot),cet1,url(code)])
print("bank_data.csv 생성")

# data.html (검증 페이지)
def cell(v,pct=False,won=False):
    if v is None or v=="" : return "—"
    if pct: return f"{v:.1%}" if v<1.5 else f"{v}"
    if won: return f"{v:,.0f}"
    return str(v)
trs=""
for code,name,cls,ead,rwa,arw,elr,tot,cet1 in ROWS:
    badge={"실측":"m","추정":"e","표준법":"s"}[cls]
    rwa_disp=cell(rwa,won=True)+("<sup>†</sup>" if cls=="추정" and rwa else "")
    trs+=(f'<tr><td class="l">{name}</td><td><span class="b {badge}">{cls}</span></td>'
          f'<td>{cell(ead,won=True)}</td><td>{rwa_disp}</td>'
          f'<td>{cell(arw,pct=True)}</td><td>{("—" if elr is None else f"{elr:.2%}")}</td>'
          f'<td>{cell(tot,won=True)}</td><td>{cell(cet1)}</td>'
          f'<td class="l"><a href="{url(code)}" target="_blank">통일공시 ↗</a></td></tr>\n')

html=f'''<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>데이터 점검 — SRT 연구 사용 데이터</title>
<meta name="description" content="SRT 연구에 사용한 은행별 기업 익스포저·위험가중자산·평균위험가중치·예상손실 데이터와 출처. 검증용."/>
<meta property="og:title" content="데이터 점검 — SRT 연구 사용 데이터"/>
<meta property="og:description" content="은행별 기업 EAD·RWA·평균위험가중치·예상손실 및 출처(은행연합회 통일공시·FISIS). 재현 스크립트 포함."/>
<meta property="og:image" content="https://sdkparkforbi.github.io/srt-project/assets/project_thumb.png"/>
<meta property="og:url" content="https://sdkparkforbi.github.io/srt-project/data.html"/>
<link rel="preconnect" href="https://fonts.googleapis.com"/><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet"/>
<style>
 body{{margin:0;background:#f5f6f8;color:#1f2733;font-family:'Noto Sans KR',sans-serif;line-height:1.7}}
 .wrap{{max-width:1000px;margin:0 auto;background:#fff;min-height:100vh;box-shadow:0 1px 40px rgba(20,30,50,.08)}}
 header{{background:linear-gradient(150deg,#1d3b6e,#16305c);color:#fff;padding:40px clamp(20px,4vw,56px)}}
 header h1{{margin:.2em 0;font-size:clamp(1.4rem,3vw,1.9rem)}}
 header p{{color:#cdddf5;margin:.3em 0;font-size:.95rem}}
 header a{{color:#fff}}
 main{{padding:24px clamp(20px,4vw,56px) 56px}}
 .src{{background:#f1f4f8;border-left:4px solid #1d3b6e;border-radius:0 8px 8px 0;padding:14px 18px;font-size:.9rem;margin:18px 0}}
 .tw{{overflow-x:auto;margin:18px 0}}
 table{{width:100%;border-collapse:collapse;font-size:.85rem}}
 th,td{{border:1px solid #e3e7ec;padding:8px 9px;text-align:right;white-space:nowrap}}
 th{{background:#1d3b6e;color:#fff;font-weight:500}} td.l,th.l{{text-align:left}}
 tbody tr:nth-child(even){{background:#fafbfc}}
 .b{{font-size:.72rem;padding:2px 8px;border-radius:20px;color:#fff}}
 .b.m{{background:#15803d}}.b.e{{background:#b8860b}}.b.s{{background:#5d6675}}
 a{{color:#0f766e}}
 h2{{font-size:1.15rem;color:#1d3b6e;border-bottom:2px solid #e3e7ec;padding-bottom:.3em;margin-top:1.8em}}
 ul{{padding-left:1.2em}} li{{margin:.4em 0}}
 code{{background:#f1f4f8;padding:2px 6px;border-radius:5px;font-size:.85rem}}
 .note{{font-size:.82rem;color:#5d6675}}
</style></head><body><div class="wrap">
<header>
 <p><a href="index.html">← 프로젝트 홈</a></p>
 <h1>데이터 점검 (Data Review)</h1>
 <p>SRT 연구에 사용한 은행별 기업 익스포저·위험가중자산·예상손실과 그 출처입니다. 각 숫자는 공개 공시로 검증 가능합니다.</p>
</header>
<main>
 <div class="src">
  <b>출처 및 기준시점(모두 2025년말).</b> ① 기업 EAD·RWA·LGD·예상손실 = 각 은행 「리스크관리」 공시(은행연합회 통일경영공시, <b>2025년말(4분기)</b>)의 내부등급법 표(CR6) 직접 추출. ② 총위험가중자산·보통주자본비율(CET1) = 금융감독원 금융통계정보시스템(FISIS), 통계표 SA014, <b>2025년 4분기</b>. 단위는 억원.<br>
  <span style="color:#b8860b">※ 추정 2개(경남·광주)의 기업 RWA(<sup>†</sup>)는 2025년말 상세표가 PDF에서 추출되지 않아 부득이 <b>2026년 1분기 통일공시</b> 기준을 사용했습니다(평균RW 42% 적용). 부산은 30쪽 근방 신용리스크 CR6 표에서 2025년말 실측 전환 완료.</span>
 </div>
 <h2>은행별 데이터</h2>
 <div class="tw"><table>
  <thead><tr><th class="l">은행</th><th>분류</th><th>기업 EAD</th><th>기업 RWA</th><th>평균RW</th><th>예상손실률</th><th>총RWA(FISIS)</th><th>CET1(%)</th><th class="l">출처</th></tr></thead>
  <tbody>
{trs}  </tbody>
 </table></div>
 <p class="note"><span class="b m">실측</span> 리스크관리 공시에서 직접 추출(9개) · <span class="b e">추정</span> EAD 추출 불가로 평균위험가중치 42%(실측 평균) 적용(2개) · <span class="b s">표준법</span> 내부등급법 미적용(1개)</p>

 <h2>검증 방법</h2>
 <ul>
  <li><b>원본 대조</b>: 표의 '통일공시 ↗' 링크에서 각 은행 「리스크관리」(연말) 보고서를 열어, 내부등급법 기업(대기업·중소기업) 포트폴리오의 EAD·위험가중자산·예상손실과 대조.</li>
  <li><b>총량·비율 대조</b>: 금융감독원 FISIS(<a href="https://fisis.fss.or.kr" target="_blank">fisis.fss.or.kr</a>) 통계표 SA014(자본적정성)에서 총위험가중자산·CET1 대조.</li>
  <li><b>재현</b>: <code>data/extract_corporate.py</code>(리스크관리 보고서→기업 EAD/RWA/EL 추출), <code>data/simulate_secirba.py</code>(SEC-SA/IRBA 시뮬레이션), 원자료 <code>data/real_corp.json</code>.</li>
 </ul>
 <h2>한계 (점검 시 참고)</h2>
 <ul>
  <li>경남·광주: 기본내부등급법 승인 은행이나, 리스크관리 보고서 CR6 표의 EAD가 PDF 텍스트로 추출되지 않아 <b>평균위험가중치를 동종(42%) 추정</b>함. (부산은 30쪽 근방 CR6 표에서 평균RW 48.5%로 2025년말 실측 전환 완료.)</li>
  <li>제주: 내부등급법 미적용(표준방법)으로 기업 IRB 데이터 없음.</li>
  <li>SRT 트렌치 구조(우선손실=예상손실, 메자닌 이전비중)는 거래설계 가정이 일부 포함됨.</li>
 </ul>
</main></div></body></html>'''
io.open("../data.html","w",encoding="utf-8").write(html)
print("data.html 생성")
