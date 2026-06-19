# HUEN rustdesk-server fork — 수정·빌드·배포 노트

OSS [rustdesk-server](https://github.com/rustdesk/rustdesk-server)의 fork. **WebSocket(WS) 기반 피제어 호스트 지원**을 추가해서, 아웃바운드 443만 열리는 방화벽 뒤 고객 PC도 reverse proxy(WSS/443)로 원격지원이 되게 한 것이 목적입니다.

> **비밀값은 저장소에 없습니다.** 서버 키(`id_ed25519` / `.pub`)는 **런타임에** 주입합니다(아래 3번). 식별 도메인/호스트/IP도 소스에 없습니다.

---

## 1. stock 대비 변경점 (전부 `src/rendezvous_server.rs`, `// HUEN:` 표시)

OSS hbbs는 피제어 호스트의 등록·연결요청을 **UDP** 중심으로 처리합니다 → UDP/inbound가 막힌 망에선 호스트가 안 잡힙니다. 이 fork는 **WS 한 연결**로 등록·연결요청 수신·온라인표시·ID변경이 모두 되게 합니다.

| 변경 | 내용 |
|---|---|
| **`ws_peers` 맵** (struct 필드 + init) | `id -> mpsc::UnboundedSender` — WS로 붙은 피제어 호스트에 서버가 메시지를 **push**하는 채널 |
| **`register_pk_common()`** (신규 헬퍼) | PK 등록 공용화 + **ID 변경 가용성 체크**: `pk`가 비면 "new_id 써도 되나?" 질의로 간주 → 비었거나 같은 uuid면 `OK`, 다른 uuid가 점유 중이면 `ID_EXISTS` (이때는 저장 안 함). 클라가 `OK`를 받으면 새 id로 진짜 pk를 재등록 |
| **`handle_tcp` OnlineRequest 분기** (신규) | 온라인 상태 질의를 현재 WS/TCP sink로 `OnlineResponse` 응답. stock은 UDP 경로에서만 처리 → WS 조회자는 응답을 못 받아 **피어목록 점이 회색**이던 문제 해결 (`last_reg_time.elapsed() < REG_TIMEOUT`로 판정) |
| **`handle_tcp` RegisterPk 분기** | stock의 `NOT_SUPPORT` → **WS/TCP 등록 허용** (검증 후 `update_pk`) |
| **`handle_punch_hole` / `_request` 라우팅** | 대상 id가 `ws_peers`에 있으면 UDP(`tx.send(Data::Msg)`) 대신 **WS 채널로 connection 요청 push** |
| **WS 수신 루프** (`handle_listener_inner`) | `tokio::select!`로 재작성: (a) push 채널 수신 → 해당 WS로 전송, (b) **15초 idle → 빈 하트비트로 WS 유지 + `last_reg_time` 갱신**(호스트 온라인 유지), (c) 빈 프레임 = 클라 하트비트 echo → skip, (d) `RegisterPk` → `register_pk_common`, `OK`면 `ws_peers`에 `id→sender` 등록 + `reg_id` 기억, (e) 그 외 → `handle_tcp`. 연결 종료 시 `ws_peers`에서 제거 |
| TCP(비WS) 타임아웃 | 30초 → 15초 |

서브모듈 `libs/hbb_common`: `83419b6` → `387603f` (클라이언트 fork와 동일 커밋).

---

## 2. 빌드

### Docker (배포용 — `Dockerfile.huen`)
```sh
docker build -f Dockerfile.huen -t <your-registry>/rustdesk-server:latest .
docker push <your-registry>/rustdesk-server:latest
```
`rust:bookworm`에서 `cargo build --release --bin hbbs --bin hbbr` → `debian:bookworm-slim`에 두 바이너리만 복사. 노출 포트 21115–21119(+21116/udp).

### 네이티브 (개발/테스트)
```sh
git submodule update --init --recursive
cargo build --release --bin hbbs --bin hbbr
```

---

## 3. 배포 / 키 주입 (★비밀값은 여기서만★)

서버 키는 저장소에 없고, `docker/rootfs/.../s6-rc.d/key-secret/up.real`(스톡)이 **런타임에** 다음 중 하나에서 읽습니다:
- **docker secret**: `/run/secrets/key_priv`, `/run/secrets/key_pub`
- **ENV**: `KEY_PRIV`, `KEY_PUB`
- **볼륨**: `/data`에 `id_ed25519`(+`.pub`) 직접 배치
- 아무것도 없으면 hbbs가 새로 생성 (생성된 공개키를 클라에 baked)

기본 포트: `21115`(NAT type test) · `21116`(+udp; 등록/punch-hole) · `21117`(relay) · `21118`(hbbs WS) · `21119`(hbbr WS).

### 443-only(WSS) 환경
방화벽이 아웃바운드 443만 허용하는 고객망을 위해, **reverse proxy**(예: Nginx Proxy Manager)로 WSS/443을 hbbs/hbbr의 WS 포트(21118/21119)에 프록시합니다. 클라이언트는 `allow-websocket` + 서버 도메인만으로 접속합니다(클라이언트 fork의 `BUILD-HUEN.md` 참고). 실제 도메인/프록시 설정값은 저장소에 두지 마세요.

> 클라이언트 **배포(다운로드) 페이지** + 상담원용 **M365 키 발급 게이트** 샘플은 [`deploy/`](deploy/README.md) 참고.

---

## 4. Windows에서 개발 시 주의

- **`core.fileMode`**: Windows 체크아웃은 Unix 실행비트(100755)를 잃어 `docker/rootfs/.../s6-rc.d/*`·`healthcheck.sh` 등이 전부 "modified"로 보입니다(내용 변경 0줄, 권한 비트만). **그대로 커밋하면 컨테이너의 s6 스크립트가 실행 불가가 됩니다.** → `git config core.fileMode false`로 무시하세요.
- `*.bak` (작업 백업)은 커밋 금지 — `.gitignore`로 제외.
- 빌드 전 `git submodule update --init --recursive`.
