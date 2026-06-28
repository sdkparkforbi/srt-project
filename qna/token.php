<?php
// dementia-avatar-liveavatar / token.php
// LiveAvatar 세션 토큰 생성 + 세션 시작 (cha-interview-bot-liveavatar/api/liveavatar-token.js 포팅)
// 키는 같은 폴더 config.php 에서 로드 (.htaccess SetEnv 의존 안 함).
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo json_encode(array('error'=>'method not allowed')); exit; }

$LIVEAVATAR_API_KEY = '';
$LIVEAVATAR_VOICE_ID = '';   // config.php 에서 설정 (이 아바타는 voice_id 필수)
if (file_exists(__DIR__ . '/config.php')) require __DIR__ . '/config.php';
if (empty($LIVEAVATAR_API_KEY)) { http_response_code(500); echo json_encode(array('error'=>'API key not configured')); exit; }

$input = json_decode(file_get_contents('php://input'), true);
if (!is_array($input)) $input = array();
$avatarId      = isset($input['avatar_id']) ? $input['avatar_id'] : '';
$contextId     = isset($input['context_id']) ? $input['context_id'] : null;
$voiceId       = isset($input['voice_id']) && $input['voice_id'] ? $input['voice_id'] : $LIVEAVATAR_VOICE_ID;
$interactivity = isset($input['interactivity_type']) ? $input['interactivity_type'] : 'CONVERSATIONAL';
if (!$avatarId) { http_response_code(400); echo json_encode(array('error'=>'avatar_id required')); exit; }

function la_post($url, $headers, $body) {
    $ch = curl_init($url);
    curl_setopt_array($ch, array(
        CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 30,
        CURLOPT_HTTPHEADER => $headers, CURLOPT_POSTFIELDS => $body,
    ));
    $resp = curl_exec($ch); $code = curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_close($ch);
    return array($code, json_decode($resp, true));
}

// Step 1: 세션 토큰 생성 (FULL 모드 — 외부 텍스트 발화 avatar.speak_text 허용)
$tokenBody = json_encode(array(
    'mode' => 'FULL',
    'avatar_id' => $avatarId,
    'is_sandbox' => false,
    'video_settings' => array('quality' => 'medium', 'encoding' => 'H264'),
    'avatar_persona' => array(
        'context_id' => $contextId,
        'language' => 'ko',
        'voice_id' => $voiceId,
        'voice_settings' => array('model' => 'eleven_flash_v2_5', 'speed' => 1.0),
        'stt_config' => array('provider' => 'deepgram'),
    ),
    'interactivity_type' => $interactivity,
), JSON_UNESCAPED_UNICODE);

list($tCode, $tData) = la_post('https://api.liveavatar.com/v1/sessions/token',
    array('Content-Type: application/json', 'X-API-KEY: ' . $LIVEAVATAR_API_KEY), $tokenBody);
if ($tCode < 200 || $tCode >= 300 || !isset($tData['code']) || $tData['code'] !== 1000) {
    http_response_code($tCode ?: 500); echo json_encode(array('error'=>'Token creation failed','detail'=>$tData)); exit;
}
$sessionToken = $tData['data']['session_token'];
$sessionId    = $tData['data']['session_id'];

// Step 2: 세션 시작 → LiveKit 접속 정보
list($sCode, $sData) = la_post('https://api.liveavatar.com/v1/sessions/start',
    array('Content-Type: application/json', 'Authorization: Bearer ' . $sessionToken), '');
if ($sCode < 200 || $sCode >= 300 || !isset($sData['code']) || $sData['code'] !== 1000) {
    http_response_code($sCode ?: 500); echo json_encode(array('error'=>'Session start failed','detail'=>$sData)); exit;
}

echo json_encode(array(
    'session_id' => $sessionId,
    'session_token' => $sessionToken,
    'livekit_url' => $sData['data']['livekit_url'],
    'livekit_client_token' => $sData['data']['livekit_client_token'],
));
