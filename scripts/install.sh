#!/data/data/com.termux/files/usr/bin/sh
set -eu

cd "$(dirname "$0")/.."

if command -v termux-wake-lock >/dev/null 2>&1; then
  termux-wake-lock || true
fi

echo "PocketOrigin is ready."
echo "Start it with:"
echo "  cd $(pwd)"
echo "  python -m pocketorigin"

