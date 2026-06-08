#!/data/data/com.termux/files/usr/bin/sh
set -eu

cd "$(dirname "$0")/.."
mkdir -p .pocketorigin

if [ -f .pocketorigin/tunnel.pid ]; then
  PID="$(cat .pocketorigin/tunnel.pid)"
  if kill -0 "$PID" 2>/dev/null; then
    echo "Tunnel is already running: PID $PID"
    grep -o 'https://[^ ]*\.lhr\.life' .pocketorigin/tunnel.log 2>/dev/null | tail -n 1 || true
    exit 0
  fi
fi

nohup ssh \
  -o ServerAliveInterval=30 \
  -o StrictHostKeyChecking=accept-new \
  -R 80:127.0.0.1:7860 \
  nokey@localhost.run > .pocketorigin/tunnel.log 2>&1 &

echo "$!" > .pocketorigin/tunnel.pid
sleep 8

echo "Tunnel started."
grep -o 'https://[^ ]*\.lhr\.life' .pocketorigin/tunnel.log | tail -n 1 || {
  echo "No tunnel URL yet. Check .pocketorigin/tunnel.log"
}

