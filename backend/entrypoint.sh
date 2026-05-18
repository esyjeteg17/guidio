#!/bin/sh
set -e

echo "[entrypoint] waiting for database $DB_HOST:$DB_PORT..."
python <<'PY'
import os, socket, time
host = os.environ.get("DB_HOST", "db")
port = int(os.environ.get("DB_PORT", "5432"))
deadline = time.time() + 60
while time.time() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"[entrypoint] db {host}:{port} is up")
            break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit(f"[entrypoint] database {host}:{port} not reachable")
PY

echo "[entrypoint] applying migrations"
python manage.py migrate --noinput

echo "[entrypoint] collecting static"
python manage.py collectstatic --noinput

exec "$@"
