#!/data/data/com.termux/files/usr/bin/sh
set -eu

cd "$(dirname "$0")/.."
mkdir -p .pocketorigin

if [ -f .pocketorigin/panel.pid ]; then
  PID="$(cat .pocketorigin/panel.pid)"
  if kill -0 "$PID" 2>/dev/null; then
    echo "PocketOrigin is already running: PID $PID"
    exit 0
  fi
fi

if [ -f .pocketorigin/public_password ]; then
  PASS="$(cat .pocketorigin/public_password)"
else
  PASS="$(python - <<'PY'
import secrets
print(secrets.token_urlsafe(12))
PY
)"
  printf '%s' "$PASS" > .pocketorigin/public_password
fi

printf '%s' "$PASS" > PUBLIC_PASSWORD.txt

POCKETORIGIN_HOST="${POCKETORIGIN_HOST:-::}" \
POCKETORIGIN_PASSWORD="$PASS" \
nohup python -m pocketorigin > .pocketorigin/panel.log 2>&1 &

echo "$!" > .pocketorigin/panel.pid
echo "PocketOrigin started."
echo "Local: http://127.0.0.1:7860"
echo "Username: pocket"
echo "Password: $PASS"

