# SRT AI 안내소 (qna) — 안내봇 리포

중요위험이전(SRT) 연구를 쉬운 말로 설명하는 AI 안내봇. **글로 묻기**(텍스트, OpenAI gpt-4o-mini)와 **아바타와**(LiveAvatar + LiveKit 얼굴 대화) 두 모드.

**라이브:** https://aiforalab.com/srt/qna/ (AIForALab 서버 자체 호스팅 — PHP. GitHub Pages는 PHP 미지원이라 라이브는 서버에서만 동작)

## 구성
- `index.html` — 프론트엔드(탭: 글로 묻기 / 아바타와)
- `openai-chat.php` — TTT/FTF 공용 두뇌(gpt-4o-mini, SRT 지식, JSON {reply, ttsReply, action})
- `token.php` — LiveAvatar 세션 토큰 발급 + 시작(LiveKit 접속정보 반환)
- `session.php` — 세션 keep-alive / stop
- `config.php.example` — 키 템플릿. 서버에서 `config.php`로 복사해 키 입력(권한 640 user2:apache, **git 커밋 금지**)
- `.htaccess` — 캐시 비활성 + config 직접접근 차단

## 배포(AIForALab 서버, Vercel 불필요)
```
/var/www/html/srt/  ← 정적 + PHP API 한 폴더에서 동작 (Apache/PHP)
```
키는 `config.php`에만(640 user2:apache). 프론트엔드에는 어떤 비밀키도 없음.
