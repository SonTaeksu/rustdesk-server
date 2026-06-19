# auth-oauth2proxy — 상담원 페이지 서버측 M365 게이트 (샘플)

상담원 다운로드 페이지를 **oauth2-proxy**로 감싸서, **M365 로그인 전엔 페이지 자체가 안 열리게** 합니다(진짜 경계). 정적 파일은 인증 통과 전까지 절대 서빙되지 않습니다.

```
[browser] → NPM(443/TLS) → oauth2-proxy:4180 (M365 인증) → staffweb (정적 상담원 페이지)
```

## 1. Entra(Azure AD) 앱 설정
device-code용 **공개 클라이언트**와 달리, oauth2-proxy는 **confidential 클라이언트**(시크릿 필요)입니다. 기존 앱에 추가하거나 새 앱을 만드세요.
1. **Authentication → Add a platform → Web** → Redirect URI: `https://<STAFF_HOST>/oauth2/callback`
2. **Certificates & secrets → New client secret** → 값 복사 (= `AAD_CLIENT_SECRET`)
3. (선택) ID 토큰에 email/그룹 클레임 추가

## 2. 설정 + 실행
```sh
cd deploy/auth-oauth2proxy
cp .env.example .env && nano .env          # 값 채우기 (COOKIE_SECRET = openssl rand -base64 32)
mkdir -p staff-site
cp ../webroot/<당신의-상담원폴더>/index.html staff-site/index.html   # 상담원 페이지 배치
docker compose up -d
```

## 3. reverse proxy (NPM)
- **Proxy Host** 추가: 도메인 `STAFF_HOST` → Forward `http://<docker-host>:4180`
- SSL(Let's Encrypt) 켜기, **Websockets Support** 켜기
- 끝. `https://<STAFF_HOST>/` 접속 → M365 로그인 → 통과해야 상담원 페이지

## 참고
- **허용 범위**: `--email-domain`(.env의 `ALLOWED_DOMAIN`)으로 도메인 제한. 그룹 제한은 `--allowed-group` + 토큰 groups 클레임 필요.
- **서브도메인 권장**: oauth2-proxy가 `/oauth2/*` 경로를 점유하므로 전용 호스트(`staff.example.com`)가 깔끔. 한 도메인 하위 경로에 얹으려면 `--proxy-prefix`로 엔드포인트를 옮겨야 함.
- oauth2-proxy는 서버측 인증이라 **숨김 경로(obscurity)는 불필요**합니다(원하면 추측 어려운 호스트명을 써도 됨).
- 실제 시크릿이 든 `.env` 는 **커밋 금지** (저장소 `.gitignore`에 추가됨).
