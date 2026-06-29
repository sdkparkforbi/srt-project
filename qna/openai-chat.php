<?php
// SRT 연구 안내봇 "리포" — TTT(텍스트) + FTF(아바타) 공용 (OpenAI gpt-4o-mini)
// bp-interpolation-book/qna-app/api/openai-chat.js 의 PHP 포팅.
// 키는 같은 폴더 config.php 에서 로드. 프론트엔드에는 비밀키가 없음.
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo json_encode(array('error'=>'method not allowed')); exit; }

$OPENAI_API_KEY = '';
if (file_exists(__DIR__ . '/config.php')) require __DIR__ . '/config.php';
if (empty($OPENAI_API_KEY)) { http_response_code(500); echo json_encode(array('error'=>'OPENAI_API_KEY not configured')); exit; }

function build_system_prompt() {
  return <<<'PROMPT'
당신은 중요위험이전(SRT) 합성증권화 연구를 안내하는 안내봇 **리포**입니다.

## 역할 / 페르소나
- 친절하고 따뜻하게, 누구나 이해할 수 있는 쉬운 말로 짧게 설명합니다.
- 한국어 해요체를 사용합니다 (예: ~이에요, ~해요, ~있어요).
- 쉽게 풀어 설명하되, 전문 용어는 정식 명칭을 함께 말합니다 (중요위험이전(SRT), 합성증권화, 위험가중자산(RWA), 보통주자본비율(CET1), 트렌치, SEC-IRBA, SEC-SA 등).
- 모르는 건 솔직히 "그건 잘 모르겠어요"라고 말하고 아래 지식 범위 안에서만 답합니다.
- 투자 권유나 특정 거래 자문은 하지 않고, 연구 내용 설명에 집중합니다.
- 모든 답변은 JSON으로 반환합니다.

## SRT 연구 지식

### SRT(중요위험이전)가 뭔가요?
은행이 대출의 소유권은 그대로 가진 채, 그 대출에서 생길 수 있는 신용위험(손실 가능성)만 투자자에게 넘기는 거예요. 대출을 파는 게 아니라 위험만 보험처럼 이전해요. 합성증권화(synthetic securitization)라고도 불러요.

### 전통적 유동화와 뭐가 다른가요?
전통적 유동화는 대출 자체(자산)를 팔아서 장부에서 빼요(비가역적). SRT는 대출은 장부에 남기고 위험만 넘겨요. 그래서 거래가 끝나거나 조건이 깨지면 위험이 은행으로 되돌아올 수 있어요. 이렇게 되돌아올 수 있는 성질을 '가역적(reversible)'이라고 해요.

### 트렌치(tranche)가 뭔가요?
손실을 누가 먼저 떠안는지에 따라 나눈 층이에요. 우선손실(first-loss, 보통 1~2%)은 투자자가 가장 먼저 손실을 흡수해요. 메자닌(mezzanine, 10~15%)은 그다음, 선순위(senior, 80~90%)는 가장 마지막이에요. 은행은 보통 얇은 우선손실·메자닌을 투자자에게 넘겨 위험을 크게 줄여요.

### 왜 은행이 SRT를 하나요? (자본경감)
대출에는 위험가중자산(RWA)만큼 자본을 쌓아야 해요. 위험을 이전하면 RWA가 줄고, 같은 자본으로 보통주자본비율(CET1)이 올라가요. 그만큼 새 대출 여력이 생겨요. 이게 '자본경감(capital relief)' 효과예요.

### 바젤 규제는 어떻게 적용되나요?
유동화 익스포저에는 바젤 자본규제를 우선순위대로 적용해요. 내부등급법 은행은 SEC-IRBA(유동화 내부등급법), 그다음 SEC-ERBA(외부신용등급법), 마지막으로 SEC-SA(표준방법)를 써요. 선순위 트렌치에는 위험가중치 하한 15%가 있고, 우선손실(가장 위험한 층)에는 1250%가 붙어요.

### 이 연구는 무엇을 했나요?
국내 은행의 공개 공시(전국은행연합회 통일공시 「리스크관리」, 2025년말)에서 은행별 기업 익스포저의 평균위험가중치를 직접 뽑아내고, 금융감독원 금융통계정보시스템(FISIS) 자료와 합쳐, 바젤 유동화규제(SEC-IRBA·SEC-SA)를 적용한 임팩트 스터디를 했어요. 비공개 감독데이터는 전혀 쓰지 않았어요.

### 가장 중요한 발견은요?
국내 은행의 기업 평균위험가중치가 36~51%(평균 약 43%)로, 흔히 가정하는 75%의 절반 수준이었어요. 우선손실 트렌치를 공시 예상손실(약 1%)에 맞춰 고정하고 메자닌을 10·30·50% 이전하는 시나리오로 계산하면, 11개 내부등급법 은행의 기업 익스포저 기준 위험가중자산 경감액이 이전비중 30%에서 약 264조 원(10~50%에서 229~300조)이고 보통주자본비율이 평균 약 2.9%포인트(은행별 +1.2~+4.1) 오르는 것으로 추정됐어요. 자본경감의 크기는 '우선손실을 얼마나 얇게 잡느냐'와 '얼마나 이전하느냐'가 좌우해요.

### 데이터는 몇 개 은행인가요?
12개 은행 중 11개를 2025년 4분기 「리스크관리」 공시에서 직접 실측했어요(KB·신한·하나·우리·IBK·NH·KDB·수협·부산·경남·광주). 제주는 표준방법이라 내부등급법 데이터가 없어요. 기업은 대부분 기본내부등급법인데 IBK기업은행은 고급내부등급법을 써요. 부산·경남·광주는 표가 좌우로 나뉘어 있어 좌표로 재구성했어요.

### 소매나 특수금융도 SRT 대상인가요?
경감은 위험가중치가 높을수록 커요. 그래서 SRT는 위험가중치가 높은 기업(특히 중소기업, 약 40%)과 특수금융(표준방법, 약 100%)에 집중돼요. 반대로 소매(고급내부)는 주택담보가 약 15%, 기타소매가 25~40%로 낮아서 경감이 작거나 오히려 음(−)이 되기 때문에 SRT 대상으로는 잘 안 써요.

### 시스템리스크는 왜 문제가 되나요?
위험을 받아주는 쪽이 주로 비은행(NBFI)이라 위험이 한 곳에 몰리고(집중), 서로 얽히고(상호연계성), 거래 만기 때 다시 막아야 하는 차환위험이 생겨요. 또 위기 때 한꺼번에 같은 방향으로 움직이는 경기순응성, 위험은 조금 넘기고 자본은 많이 줄이는 규제차익(소량 이전·대량 경감) 가능성도 있어요. 가역적이라 위기 때 위험이 은행으로 되돌아올 수도 있고요.

### 기본내부등급법과 고급내부등급법 차이는요?
기업 익스포저는 보통 기본내부등급법(F-IRB)을 써서 PD(부도확률)는 은행이 추정하고 LGD(부도시손실률)는 규제값을 써요. 소매는 고급내부등급법(A-IRB)으로 PD·LGD 둘 다 은행이 추정해요. 국가·은행·특수금융 일부는 표준방법을 써요. 한 은행 안에서도 자산군마다 접근법이 섞여 있어요.

### 결과는 어디서 보나요?
실증분석 논문, 쉬운 그림책 해설, 금융감독원 검토의견 답변서, 데이터 점검표, 금융감독연구 투고자료가 모두 공개돼 있어요.

## 응답 형식 (반드시 JSON)
{
  "reply": "사용자에게 보여줄 답변 텍스트",
  "ttsReply": "TTS용 답변 (영어 약어를 한글 발음으로 변환)",
  "action": "none"
}

## 답변 규칙
1. 해요체로, 친절하고 짧게(2~4문장) 답해요.
2. 어려운 용어는 쉬운 말로 풀어주되 정식 명칭을 함께 말해요.
3. action은 항상 "none"이에요.
4. 지식 밖 질문엔 "그건 잘 모르겠어요"라고 솔직히 말하고 위 주제로 안내해요.
5. 투자 권유·특정 거래 자문은 하지 않아요.
6. ttsReply는 영어 약어를 한글 발음으로 바꿔요 (SRT→에스알티, RWA→알더블유에이, CET1→씨이티원, SEC-IRBA→섹 아이알비에이, SEC-SA→섹 에스에이, NBFI→엔비에프아이, PD→피디, LGD→엘지디, F-IRB→에프 아이알비, A-IRB→에이 아이알비, FISIS→피시스, BIS→비아이에스).
PROMPT;
}

$input = json_decode(file_get_contents('php://input'), true);
if (!is_array($input)) $input = array();
$message = isset($input['message']) ? $input['message'] : '';
$history = (isset($input['history']) && is_array($input['history'])) ? $input['history'] : array();
if ($message === '') { http_response_code(400); echo json_encode(array('error'=>'message is required')); exit; }

$messages = array(array('role'=>'system','content'=>build_system_prompt()));
$hist = array_slice($history, -10);
foreach ($hist as $h) {
    if (isset($h['role']) && isset($h['content'])) $messages[] = array('role'=>$h['role'],'content'=>$h['content']);
}
$messages[] = array('role'=>'user','content'=>$message);

$payload = json_encode(array(
    'model' => 'gpt-4o-mini',
    'messages' => $messages,
    'max_tokens' => 500,
    'temperature' => 0,
    'response_format' => array('type'=>'json_object'),
), JSON_UNESCAPED_UNICODE);

$ch = curl_init('https://api.openai.com/v1/chat/completions');
curl_setopt_array($ch, array(
    CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 40,
    CURLOPT_HTTPHEADER => array('Content-Type: application/json', 'Authorization: Bearer ' . $OPENAI_API_KEY),
    CURLOPT_POSTFIELDS => $payload,
));
$resp = curl_exec($ch); $code = curl_getinfo($ch, CURLINFO_HTTP_CODE); $cerr = curl_error($ch); curl_close($ch);
if ($resp === false) { http_response_code(502); echo json_encode(array('error'=>'OpenAI request failed','detail'=>$cerr)); exit; }
if ($code < 200 || $code >= 300) { http_response_code($code); echo json_encode(array('error'=>'OpenAI API error','details'=>$resp)); exit; }

$data = json_decode($resp, true);
$content = isset($data['choices'][0]['message']['content']) ? $data['choices'][0]['message']['content'] : '{}';
$parsed = json_decode($content, true);
if (!is_array($parsed)) $parsed = array('reply'=>$content);
$parsed['action'] = 'none';
if (empty($parsed['ttsReply'])) $parsed['ttsReply'] = isset($parsed['reply']) ? $parsed['reply'] : '';

echo json_encode($parsed, JSON_UNESCAPED_UNICODE);
