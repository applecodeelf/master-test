#!/data/data/com.termux/files/usr/bin/sh
set -eu

cd "$(dirname "$0")/.."

stop_pid_file() {
  file="$1"
  name="$2"
  if [ -f "$file" ]; then
    PID="$(cat "$file")"
    if kill -0 "$PID" 2>/dev/null; then
      kill "$PID" 2>/dev/null || true
      echo "Stopped $name: PID $PID"
    fi
  fi
}

stop_pid_file .pocketorigin/tunnel.pid "tunnel"
stop_pid_file .pocketorigin/panel.pid "PocketOrigin"

ps -ef | grep 'python -m pocketorigin' | grep -v grep | awk '{print $2}' | while read PID; do
  kill "$PID" 2>/dev/null || true
  echo "Stopped PocketOrigin process: PID $PID"
done

ps -ef | grep 'localhost.run' | grep -v grep | awk '{print $2}' | while read PID; do
  kill "$PID" 2>/dev/null || true
  echo "Stopped tunnel process: PID $PID"
done

