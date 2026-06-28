<?php
// dementia-avatar-liveavatar / session.php
// LiveAvatar 세션 관리: keep-alive, stop (cha-interview-bot-liveavatar/api/liveavatar-session.js 포팅)
// 키는 같은 폴더 config.php 에서 로드.
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo json_encode(array('error'=>'method not allowed')); exit; }

$LIVEAVATAR_API_KEY = '';
if (file_exists(__DIR__ . '/config.php')) require __DIR__ . '/config.php';
if (empty($LIVEAVATAR_API_KEY)) { http_response_code(500); echo json_encode(array('error'=>'API key not configured')); exit; }

$input = json_decode(file_get_contents('php://input'), true);
if (!is_array($input)) $input = array();
$action    = isset($input['action']) ? $input['action'] : '';
$sessionId = isset($input['session_id']) ? $input['session_id'] : '';
$reason    = isset($input['reason']) ? $input['reason'] : 'USER_DISCONNECTED';
if (!$sessionId) { http_response_code(400); echo json_encode(array('error'=>'session_id required')); exit; }

function la_post($url, $headers, $body) {
    $ch = curl_init($url);
    curl_setopt_array($ch, array(
        CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true, CURLOPT_TIMEOUT => 15,
        CURLOPT_HTTPHEADER => $headers, CURLOPT_POSTFIELDS => $body,
    ));
    $resp = curl_exec($ch); $code = curl_getinfo($ch, CURLINFO_HTTP_CODE); curl_close($ch);
    return array($code, json_decode($resp, true));
}

$headers = array('Content-Type: application/json', 'X-API-KEY: ' . $LIVEAVATAR_API_KEY);

if ($action === 'keep-alive') {
    list($code, $data) = la_post('https://api.liveavatar.com/v1/sessions/keep-alive',
        $headers, json_encode(array('session_id' => $sessionId)));
    http_response_code($code ?: 500); echo json_encode($data); exit;
}

if ($action === 'stop') {
    list($code, $data) = la_post('https://api.liveavatar.com/v1/sessions/stop',
        $headers, json_encode(array('session_id' => $sessionId, 'reason' => $reason)));
    http_response_code($code ?: 500); echo json_encode($data); exit;
}

http_response_code(400);
echo json_encode(array('error'=>'invalid action (keep-alive|stop)'));
