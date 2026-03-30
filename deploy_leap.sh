#!/bin/bash
set -Eeuo pipefail

APP_DIR="/home/myadmin/LEAP"
VENV_DIR="$APP_DIR/myenv"
SOCKET_PATH="$APP_DIR/gunicorn.sock"
NOHUP_LOG="$APP_DIR/nohup.out"
ACCESS_LOG="$APP_DIR/server.log"
GUNICORN_MATCH="gunicorn.*LeapWeb.wsgi:application"

log() {
  printf '[deploy] %s\n' "$1"
}

dump_debug() {
  log "gunicorn processes"
  pgrep -af "$GUNICORN_MATCH" || true
  log "socket listing"
  ls -l "$SOCKET_PATH" 2>/dev/null || true
  log "nohup tail"
  tail -n 80 "$NOHUP_LOG" 2>/dev/null || true
  log "server log tail"
  tail -n 80 "$ACCESS_LOG" 2>/dev/null || true
}

trap 'log "deployment failed"; dump_debug' ERR

cd "$APP_DIR"
source "$VENV_DIR/bin/activate"

log "installing dependencies"
pip install -r requirements.txt

log "running migrations"
python manage.py migrate --noinput

log "collecting static files"
python manage.py collectstatic --noinput

log "stopping existing gunicorn"
pkill -f "$GUNICORN_MATCH" || true

if [ -e "$SOCKET_PATH" ]; then
  log "removing stale socket"
  rm -f "$SOCKET_PATH"
fi

log "starting gunicorn"
nohup "$VENV_DIR/bin/python3" "$VENV_DIR/bin/gunicorn" \
  --access-logfile "$ACCESS_LOG" \
  --workers 3 \
  --umask 007 \
  --bind "unix:$SOCKET_PATH" \
  LeapWeb.wsgi:application \
  >"$NOHUP_LOG" 2>&1 &

for attempt in 1 2 3 4 5; do
  sleep 2
  if [ -S "$SOCKET_PATH" ]; then
    log "gunicorn socket created"
    log "setting socket permissions for nginx"
    chmod 666 "$SOCKET_PATH"
    ls -l "$SOCKET_PATH"
    log "verifying gunicorn over unix socket"
    UNIX_STATUS="$(curl --silent --show-error --output /dev/null --write-out '%{http_code}' --unix-socket "$SOCKET_PATH" http://localhost/)"
    log "gunicorn unix-socket status: $UNIX_STATUS"
    case "$UNIX_STATUS" in
      200|301|302) ;;
      *)
        log "unexpected unix-socket status"
        dump_debug
        exit 1
        ;;
    esac
    log "verifying nginx HTTPS upstream"
    HTTPS_STATUS="$(curl --silent --show-error --insecure --output /dev/null --write-out '%{http_code}' -H "Host: leapnitpy.org" https://127.0.0.1/)"
    log "nginx HTTPS status: $HTTPS_STATUS"
    case "$HTTPS_STATUS" in
      200|301|302) ;;
      *)
        log "unexpected nginx HTTPS status"
        dump_debug
        exit 1
        ;;
    esac
    pgrep -af "$GUNICORN_MATCH" || true
    exit 0
  fi
  log "waiting for gunicorn socket ($attempt/5)"
done

log "gunicorn socket was not created"
dump_debug
exit 1
