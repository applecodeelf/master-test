# PocketOrigin Runbook

Use these commands from Termux.

## Start Public Panel

```sh
cd /sdcard/codexfiles/master-test
sh scripts/start_public_panel.sh
```

This starts PocketOrigin on port `7860`.

Open on the phone:

```text
http://127.0.0.1:7860
```

The username is:

```text
pocket
```

The password is written to:

```text
/sdcard/codexfiles/master-test/PUBLIC_PASSWORD.txt
```

## Start Public Tunnel

```sh
cd /sdcard/codexfiles/master-test
sh scripts/start_tunnel.sh
```

The script prints the current public URL, for example:

```text
https://xxxx.lhr.life
```

localhost.run URLs are temporary. If the tunnel restarts, the URL can change.

## Show Current Tunnel URL

```sh
grep -o 'https://[^ ]*\.lhr\.life' /sdcard/codexfiles/master-test/.pocketorigin/tunnel.log | tail -n 1
```

## Stop Everything

```sh
cd /sdcard/codexfiles/master-test
sh scripts/stop_all.sh
```

## Useful Local URLs

Phone itself:

```text
http://127.0.0.1:7860
```

Same Wi-Fi:

```text
http://PHONE_LAN_IP:7860
```

