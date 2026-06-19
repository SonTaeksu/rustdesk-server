"""
M365(Entra ID) 인증 게이트 — 샘플.

상담원 클라이언트가 device-code 로그인 후 보낸 ID 토큰을 검증하고, 통과하면
서버 공개키를 반환한다. 실제 값(tenant/client/key/도메인)은 전부 환경변수로
주입한다 — 저장소에 키/도메인을 두지 말 것.

  AAD_TENANT      : Entra 테넌트 GUID
  AAD_CLIENT      : 앱(클라이언트) ID  ── ID 토큰의 aud 와 같아야 함
  RUSTDESK_KEY    : 발급할 서버 공개키
  ALLOWED_DOMAIN  : (선택) 허용 이메일 도메인 (예: yourcompany.com)
  ALLOWED_EMAILS  : (선택) 허용 이메일 목록 (콤마 구분)
                    둘 다 비우면 "테넌트 멤버 + 이 앱"이면 통과(aud/iss로 이미 한정).

의존성: Flask, PyJWT[crypto]  (requirements.txt)
"""
import os
import jwt  # PyJWT[crypto]
from flask import Flask, request, jsonify

TENANT = os.environ["AAD_TENANT"]
CLIENT = os.environ["AAD_CLIENT"]
SERVER_KEY = os.environ["RUSTDESK_KEY"]
ALLOWED_DOMAIN = os.environ.get("ALLOWED_DOMAIN", "").lower()
ALLOWED_EMAILS = {
    e.strip().lower()
    for e in os.environ.get("ALLOWED_EMAILS", "").split(",")
    if e.strip()
}

ISSUER = f"https://login.microsoftonline.com/{TENANT}/v2.0"
_JWKS = jwt.PyJWKClient(
    f"https://login.microsoftonline.com/{TENANT}/discovery/v2.0/keys"
)

app = Flask(__name__)


def _verify(authorization: str) -> dict:
    """Bearer ID 토큰 검증 → 클레임. 실패 시 예외."""
    token = authorization.split(" ", 1)[1].strip()  # "Bearer xxx"
    signing_key = _JWKS.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=CLIENT,
        issuer=ISSUER,
        options={"require": ["exp", "iss", "aud"]},
    )


def _allowed(claims: dict) -> bool:
    if not ALLOWED_DOMAIN and not ALLOWED_EMAILS:
        return True  # aud/iss 로 이미 "이 앱 + 이 테넌트"로 한정됨
    email = (claims.get("preferred_username") or claims.get("email") or "").lower()
    if ALLOWED_EMAILS and email in ALLOWED_EMAILS:
        return True
    if ALLOWED_DOMAIN and email.endswith("@" + ALLOWED_DOMAIN):
        return True
    return False


@app.get("/config")
def config():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify(error="missing bearer token"), 401
    try:
        claims = _verify(auth)
    except Exception as e:  # noqa: BLE001 (샘플: 모든 검증 실패를 401로)
        return jsonify(error=f"invalid token: {e}"), 401
    if not _allowed(claims):
        return jsonify(error="not authorized for this resource"), 403
    # 통과 → 서버 공개키 반환. (필요하면 "server" 등 추가 필드를 줄 수 있음)
    return jsonify(key=SERVER_KEY)


@app.get("/healthz")
def healthz():
    return "ok"


if __name__ == "__main__":
    # 개발용. 운영은 gunicorn (Dockerfile 참고).
    app.run(host="0.0.0.0", port=8000)
