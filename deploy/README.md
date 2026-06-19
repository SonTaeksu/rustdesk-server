# deploy/ — 클라이언트 배포 + M365 게이트 (샘플)

hbbs/hbbr(Rust)와 **별개**로, 클라이언트 배포와 상담원용 키 발급(M365)을 담당하는 웹 레이어 **샘플**입니다. 전부 reverse proxy(예: Nginx Proxy Manager) 뒤에 둡니다.

> ⚠️ 전부 **샘플/템플릿**입니다. 실제 도메인·서버키·다운로드 링크·숨김경로는 **저장소에 두지 말고** 배포 시 환경변수/리네임으로 주입하세요.

```
deploy/
├─ authconfig/                      # M365 인증 게이트 (Flask 샘플)
│  ├─ app.py
│  ├─ requirements.txt
│  └─ Dockerfile
└─ webroot/
   ├─ index.html                    # 고객용 다운로드 (공개)
   └─ __RENAME_TO_SECRET_PATH__/    # 상담원용 다운로드 (숨김 경로)
      └─ index.html
```

---

## 1. M365 게이트 (`authconfig/`)

상담원 클라이언트(`huen_aad_gate.dart`)의 흐름:

1. device-code 로그인 — `login.microsoftonline.com/<tenant>/oauth2/v2.0/devicecode`·`/token`
2. 받은 **ID 토큰**을 `GET <CONFIG_URL>` 에 `Authorization: Bearer <idToken>` 헤더로 전송
3. 게이트가 토큰을 **검증**(서명/issuer/audience/만료 + 허용 사용자) 후 `{"key":"<서버 공개키>"}` 반환
4. 클라가 키를 메모리에 주입 → 서버 접속

> 🔒 **검증 없이 키를 주면 누구나 키를 받습니다.** 그래서 게이트는 반드시 토큰을 검증해야 합니다(`app.py` 참고). 서버 공개키 자체는 "비밀"은 아니지만(모든 클라에 baked), 발급을 사내 계정으로 한정하는 게 이 게이트의 목적입니다.

### 배포 (예)
```sh
cd deploy/authconfig
docker build -t authconfig .
docker run -d --name authconfig -p 8000:8000 \
  -e AAD_TENANT=<tenant-guid> \
  -e AAD_CLIENT=<app(client)-id> \
  -e RUSTDESK_KEY=<발급할 서버 공개키> \
  -e ALLOWED_DOMAIN=<yourcompany.com> \   # (선택) 이 도메인 계정만 허용
  authconfig
```
reverse proxy에서 `https://<server>/authconfig/` → `http://authconfig:8000/` 프록시.
클라 빌드의 `RUSTDESK_AAD_CONFIG_URL = https://<server>/authconfig/config`.

---

## 2. 다운로드 페이지 (`webroot/`)

reverse proxy의 정적 웹 루트로 `webroot/`를 서빙합니다.

- **`index.html`** (고객용) — 공개. 고객이 받아 실행 → 표시되는 ID/비번을 상담원에게 전달.
- **상담원용** — `__RENAME_TO_SECRET_PATH__` 폴더를 **추측 불가능한 임의 문자열로 바꾸세요**:
  ```sh
  mv webroot/__RENAME_TO_SECRET_PATH__ webroot/$(openssl rand -hex 8)
  # 예: webroot/a3f9c1e7b2d48506/  →  상담원 URL = https://<server>/a3f9c1e7b2d48506/
  ```
  - 고객 페이지에는 **링크하지 않습니다** → 브라우징으로 발견 불가.
  - 두 페이지 모두 `<meta name="robots" content="noindex">` → 검색 비노출.

> ⚠️ **숨김 경로는 보안 경계가 아닙니다.** 진짜 게이트는 M365 로그인입니다(상담원 클라는 로그인 전엔 키를 못 받음). 숨김 경로는 상담원용 빌드를 *공개적으로 광고하지 않으려는* 용도입니다.

각 페이지의 `<...>` 다운로드 링크는 본인이 호스팅하는 EXE/APK URL로 교체하세요.

---

## 3. 상담원 페이지 M365 인증 (선택 — 강도별 3단계)

| 단계 | 방법 | 경계 | 필요 |
|---|---|---|---|
| 1 | 숨김 경로만 (`webroot/.../index.html`) | 약함 (URL 비밀) | 폴더 rename |
| 2 | **MSAL.js 로그인 월** (`webroot/.../index.msal.html`) | 중간 (JS 게이트) | Entra **SPA** redirect URI (시크릿 X) |
| 3 | **oauth2-proxy** (`auth-oauth2proxy/`) | 강함 (서버측) | Entra **Web** redirect URI + **client secret** |

- **2단계 (MSAL.js)** — `index.msal.html`을 `index.html`로 쓰면 로그인해야 다운로드 버튼이 보입니다. 파일 안 `<AAD_TENANT>`/`<AAD_CLIENT>` 교체 + Entra 앱에 **SPA** redirect URI(이 페이지 URL) 추가. 정적 파일은 서빙되므로 약한 경계.
- **3단계 (oauth2-proxy)** — `auth-oauth2proxy/README.md` 참고. **로그인 전엔 페이지 자체가 안 열림**(진짜 경계). confidential 앱(client secret) 필요.

> 상담원 **클라이언트 자체가 M365 게이트**라(로그인 전엔 키를 못 받음), 페이지 인증은 주로 "공개 노출 방지"입니다. 강한 보장을 원하면 3단계.
