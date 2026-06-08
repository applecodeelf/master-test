# PocketOrigin

Turn an Android phone into a tiny public server from Termux.

PocketOrigin is a zero-dependency web control panel for running small services
from an Android phone. It is designed for Termux, old phones, student projects,
Minecraft servers, file sharing, webhooks, and tiny API demos.

## Features

- Phone-friendly web dashboard
- Start/stop service templates
- View service logs from the browser
- Battery, storage, memory, uptime, and process status
- Built-in templates for:
  - file server
  - hello API
  - webhook receiver
  - Minecraft Java 1.7.10 server integration
- No Python package install required

## Quick Start

```sh
cd /sdcard/codexfiles/master-test
python -m pocketorigin
```

Open:

```text
http://127.0.0.1:7860
```

On the same Wi-Fi, open the phone LAN IP:

```text
http://PHONE_IP:7860
```

## Why

Android phones are cheap, battery-backed Linux-ish machines. Termux makes them
useful, but service management, logs, tunnels, and repeatable deployment are
still awkward. PocketOrigin aims to make "phone as server" practical.

## Roadmap

- One-click tunnel setup for playit.gg / cloudflared / frp
- Install recipes for common services
- QR-code sharing page
- Auto-start on boot via Termux:Boot
- Backup and restore
- Plugin API

## Public Test Run

```sh
cd /sdcard/codexfiles/master-test
sh scripts/start_public_panel.sh
sh scripts/start_tunnel.sh
```

See [RUNBOOK.md](RUNBOOK.md) for restart, tunnel URL, and stop commands.

## Safety

Do not expose sensitive services without authentication. Public internet tunnels
can expose your phone to the internet.
