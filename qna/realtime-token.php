<?php
// STS(음성 대화) — OpenAI Realtime API ephemeral 토큰 발급.
// bp-interpolation-book/qna-app/api/realtime-token.js 의 PHP 포팅. 키는 config.php.
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo json_encode(array('error'=>'method not allowed')); exit; }

$OPENAI_API_KEY = '';
if (file_exists(__DIR__ . '/config.php')) require __DIR__ . '/config.php';
if (empty($OPENAI_API_KEY)) { http_response_code(500); echo json_encode(array('error'=>'OPENAI_API_KEY not configured')); exit; }

function default_instructions() {
  return <<<'P'
당신은 중요위험이전(SRT) 합성증권화 연구를 안내하는 음성 안내봇 '리포'입니다.

## 역할 / 페르소나
- 한국어 해요체로, 친절하고 따뜻하게, 누구나 이해할 수 있는 쉬운 말로 짧게(2~4문장) 대화합니다.
- 전문 용어는 정식 명칭을 함께 말합니다(중요위험이전 SRT, 합성증권화, 위험가중자산 RWA, 보통주자본비율 CET1, 트렌치, SEC-IRBA, SEC-SA).
- 모르는 건 솔직히 "그건 잘 모르겠어요"라고 말하고, 아래 지식 범위 안에서만 답합니다.
- 투자 권유나 특정 거래 자문은 하지 않고, 연구 내용 설명에 집중합니다.

## SRT 연구 지식 (음성 대화용 핵심)
- SRT(중요위험이전): 은행이 대출의 소유권은 그대로 가진 채 신용위험(손실 가능성)만 투자자에게 넘기는 거래예요. 대출을 파는 게 아니라 위험만 보험처럼 이전하며, 합성증권화라고도 불러요.
- 전통적 유동화는 대출 자체를 팔아 장부에서 빼지만(비가역적), SRT는 대출을 남기고 위험만 넘겨서 거래가 끝나면 위험이 되돌아올 수 있어요(가역적).
- 트렌치: 손실을 먼저 떠안는 순서대로 우선손실(1~2%)·메자닌(10~15%)·선순위(80~90%)로 나눠요. 은행은 보통 얇은 우선손실·메자닌을 투자자에게 넘겨 위험을 크게 줄여요.
- 자본경감: 위험을 넘기면 위험가중자산이 줄고 같은 자본으로 보통주자본비율이 올라가, 새 대출 여력이 생겨요.
- 바젤 규제: 내부등급법 은행은 SEC-IRBA, 그다음 SEC-ERBA, 마지막으로 SEC-SA를 적용해요. 선순위 트렌치는 위험가중치 하한 15%, 우선손실은 1250%예요.
- 이 연구: 국내 은행의 공개 공시(전국은행연합회 「리스크관리」, 2025년 4분기)에서 기업 평균위험가중치를 직접 뽑고 금융감독원 FISIS와 결합해 바젤 유동화규제를 적용한 임팩트 스터디예요. 비공개 감독데이터는 쓰지 않았어요.
- 핵심 발견: 국내 은행 기업 평균위험가중치가 36~51%(평균 약 43%)로 흔히 가정하는 75%의 절반 수준이었어요. 우선손실을 예상손실 수준으로 고정하고 메자닌을 10·30·50% 이전하면, 11개 은행 기업 기준 위험가중자산 경감이 이전비중 30%에서 약 264조 원이고 보통주자본비율이 평균 약 2.9%포인트 올라요.
- 데이터: 12개 은행 중 11개(KB·신한·하나·우리·IBK·NH·KDB·수협·부산·경남·광주)를 2025년 4분기 공시에서 실측, 제주는 표준방법이라 내부등급법 데이터가 없어요. 기업은 대부분 기본내부등급법인데 IBK는 고급내부예요.
- 대상 선별: SRT는 위험가중치가 높은 기업(특히 중소기업)·특수금융(표준 약 100%)에 집중되고, 위험가중치가 낮은 소매(주택담보 15%·기타 25~40%)는 경감이 작거나 음(−)이라 대상이 아니에요.
- 시스템리스크: 위험을 받는 쪽이 주로 비은행이라 위험 집중·상호연계성·차환위험·경기순응성·규제차익(소량 이전 대량 경감) 우려가 있고, 가역적이라 위기 때 위험이 은행으로 돌아올 수 있어요.

## 답변 규칙
- 친절하고 짧게(2~4문장). 어려운 용어는 쉬운 말로 풀되 정식 명칭을 함께 말해요.
- 확실하지 않으면 "그건 잘 모르겠어요"라고 안내하고 위 주제로 이끌어요.
- 투자 권유·특정 거래 자문은 하지 않아요.
P;
}

$input = json_decode(file_get_contents('php://input'), true);
if (!is_array($input)) $input = array();
$instructions = (isset($input['instructions']) && $input['instructions']) ? $input['instructions'] : default_instructions();

// OpenAI Realtime GA: POST /v1/realtime/client_secrets, 세션 설정은 session{} 안, 오디오는 audio.input/output 중첩.
$payload = json_encode(array(
    'session' => array(
        'type' => 'realtime',
        'model' => 'gpt-realtime',
        'instructions' => $instructions,
        'audio' => array(
            'input' => array(
                'transcription' => array('model' => 'whisper-1'),
                'turn_detection' => array('type'=>'server_vad','threshold'=>0.5,'prefix_padding_ms'=>300,'silence_duration_ms'=>500),
            ),
            'output' => array('voice' => 'alloy'),
        ),
    ),
), JSON_UNESCAPED_UNICODE);

$ch = curl_init('https://api.openai.com/v1/realtime/client_secrets');
curl_setopt_array($ch, array(
    CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 30,
    CURLOPT_HTTPHEADER => array('Content-Type: application/json', 'Authorization: Bearer ' . $OPENAI_API_KEY),
    CURLOPT_POSTFIELDS => $payload,
));
$resp = curl_exec($ch); $code = curl_getinfo($ch, CURLINFO_HTTP_CODE); $cerr = curl_error($ch); curl_close($ch);
if ($resp === false) { http_response_code(502); echo json_encode(array('error'=>'Realtime request failed','detail'=>$cerr)); exit; }
if ($code < 200 || $code >= 300) { http_response_code($code); echo json_encode(array('error'=>'Failed to create realtime session','details'=>$resp)); exit; }

$data = json_decode($resp, true);
// 프론트 계약 유지: client_secret.value 형태로 반환 (GA는 value가 최상위)
$val = isset($data['value']) ? $data['value'] : null;
$sid = (isset($data['session']) && isset($data['session']['id'])) ? $data['session']['id'] : null;
echo json_encode(array(
    'client_secret' => array('value' => $val),
    'session_id' => $sid,
), JSON_UNESCAPED_UNICODE);
