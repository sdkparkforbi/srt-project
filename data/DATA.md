# 데이터 점검 (Data Review)

본 폴더는 SRT 연구에 사용한 데이터와 추출·시뮬레이션 스크립트입니다. 모든 수치는 공개 공시로 검증 가능합니다.

## 파일
| 파일 | 내용 |
|---|---|
| `bank_data.csv` | 은행별 기업 EAD·RWA·평균위험가중치·예상손실률·총RWA·CET1 + 통일공시 링크 |
| `real_corp.json` | 리스크관리 공시에서 추출한 원자료(내부등급법 은행, 대기업/중소기업 분해 포함) |
| `extract_corporate.py` | 「리스크관리」 보고서 → 기업 EAD/RWA/예상손실 자동 추출 |
| `simulate_secirba.py` | SEC-SA / SEC-IRBA 자본경감 시뮬레이션 |
| `download_risk_reports.py` | 은행연합회 통일공시에서 「리스크관리」 보고서 일괄 다운로드 |

→ 사람이 보기 좋은 점검표: **[data.html](https://sdkparkforbi.github.io/srt-project/data.html)**

## 출처 (기준시점: 모두 2025년말)
- **기업 EAD·RWA·LGD·예상손실**: 각 은행 「리스크관리」 공시(전국은행연합회 은행경영통일공시, **2025년말 4분기**)의 내부등급법 표(CR6). `bank_data.csv`의 `통일공시_링크`에서 원본 확인.
- **총위험가중자산·보통주자본비율(CET1)**: 금융감독원 금융통계정보시스템(FISIS) 통계표 SA014(자본적정성), **2025년 4분기**. https://fisis.fss.or.kr
- ※ 12개 은행 전부 **2025년 4분기(말)** 기준. 부산·경남·광주는 CR6 표가 좌우 페이지로 분리돼 자동 추출이 어려웠으나 좌표 기반 재구성으로 2025년 4분기 실측(부산 48.5%·경남 45.9%·광주 45.9%, 광주는 대기업+중소기업 소계 합산).

## 분류
- **실측(11개)**: KB국민·신한·하나·우리·IBK기업·NH농협·KDB산업·수협·부산·경남·광주 — 2025년 4분기 공시 직접 추출. (CR6 합계 RWA가 「실제 위험가중자산」 표와 교차일치하여 검증됨)
- **표준법(1개)**: 제주 — 내부등급법 미적용.

## 재현
```bash
python download_risk_reports.py   # 리스크관리 보고서 다운로드
python extract_corporate.py       # 기업 EAD/RWA/EL 추출 → real_corp.json
python simulate_secirba.py        # SEC-SA/IRBA 경감 시뮬레이션
```

## 한계
- 트렌치 구조(우선손실=예상손실, 메자닌 이전비중)는 거래설계 가정 일부 포함.
- 총RWA(FISIS, 2025Q4)와 자산RWA(공시) 기준시점이 분기 단위로 다를 수 있음.
- 비공개 감독데이터는 일절 사용하지 않음.
