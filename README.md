> **🔧 Fork 안내** — 이 저장소는 [rustdesk-server](https://github.com/rustdesk/rustdesk-server)의 fork입니다. 라이선스는 원본과 동일한 **AGPL-3.0**([LICENSE](LICENSE)).
>
> **주요 변경점:** `src/rendezvous_server.rs`에 **WebSocket 피제어 호스트 지원** 추가 — WS로 PK 등록 / 연결요청(punch-hole) push / 온라인 상태 응답 / ID 변경 가용성 체크 / 15초 keepalive 하트비트. 아웃바운드 443만 열리는 망에서 reverse proxy(WSS)로 원격지원이 되게 함.
>
> 수정·빌드·배포 상세 + 상담원용 M365 키 게이트·다운로드 페이지: **[BUILD-HUEN.md](BUILD-HUEN.md)** · **[deploy/](deploy/README.md)**.

---

# RustDesk Server Program

[![build](https://github.com/rustdesk/rustdesk-server/actions/workflows/build.yaml/badge.svg)](https://github.com/rustdesk/rustdesk-server/actions/workflows/build.yaml)

[**Download**](https://github.com/rustdesk/rustdesk-server/releases)

[**Manual**](https://rustdesk.com/docs/en/self-host/)

[**FAQ**](https://github.com/rustdesk/rustdesk/wiki/FAQ)

[**How to migrate OSS to Pro**](https://rustdesk.com/docs/en/self-host/rustdesk-server-pro/installscript/#convert-from-open-source)

Self-host your own RustDesk server, it is free and open source.

## How to build manually

```bash
cargo build --release
```

Three executables will be generated in target/release.

- hbbs - RustDesk ID/Rendezvous server
- hbbr - RustDesk relay server
- rustdesk-utils - RustDesk CLI utilities

You can find updated binaries on the [Releases](https://github.com/rustdesk/rustdesk-server/releases) page.

If you want extra features, [RustDesk Server Pro](https://rustdesk.com/pricing.html) might suit you better.

If you want to develop your own server, [rustdesk-server-demo](https://github.com/rustdesk/rustdesk-server-demo) might be a better and simpler start for you than this repo.

## Installation

Please follow this [doc](https://rustdesk.com/docs/en/self-host/rustdesk-server-oss/)
