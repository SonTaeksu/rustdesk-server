> **🔧 HUEN fork — 핵심: WebSocket으로 방화벽 포트 개방 없는 원격지원 (서버는 앞단 reverse proxy 필수)**
>
> [rustdesk-server](https://github.com/rustdesk/rustdesk-server)의 fork입니다 (License **AGPL-3.0**, [LICENSE](LICENSE)).
>
> **★ 주 기능 — WebSocket 피제어 호스트 지원** (`src/rendezvous_server.rs`): 피제어 PC가 **WSS(443)** 로 등록·연결요청 수신·온라인표시·ID변경까지 처리됩니다. 덕분에 고객은 **방화벽 포트(21115-21119·UDP)를 열 필요 없이** 아웃바운드 443만으로 원격지원을 받습니다. (stock은 전용 포트/UDP 필요)
>
> ⚠️ **서버는 반드시 앞단에 reverse proxy(예: Nginx Proxy Manager)를 두어야 합니다** — hbbs/hbbr 자체는 TLS/443을 처리하지 않으므로, reverse proxy가 **WSS/443을 종단해 hbbs/hbbr의 WS 포트(21118/21119)로 프록시**해야 동작합니다. 설정은 [deploy/](deploy/README.md).
>
> WS 변경 상세(PK 등록·punch-hole push·OnlineResponse·15s keepalive) + 빌드·배포 + 상담원용 M365 키 게이트/다운로드 페이지: **[BUILD-HUEN.md](BUILD-HUEN.md)** · **[deploy/](deploy/README.md)**.

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
