#!/data/data/com.termux/files/usr/bin/sh
set -eu

if [ -z "${POCKETORIGIN_PASSWORD:-}" ]; then
  echo "Set POCKETORIGIN_PASSWORD before exposing PocketOrigin publicly."
  echo "Example:"
  echo "  POCKETORIGIN_PASSWORD='change-this' sh scripts/start_public.sh"
  exit 1
fi

cd "$(dirname "$0")/.."
python -m pocketorigin
