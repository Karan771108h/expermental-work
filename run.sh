#!/usr/bin/env bash
# RajScore launcher — self-healing: installs deps if missing, reseeds DB if wiped.
# Usage:  ./run.sh            (foreground)   PORT=8001 ./run.sh   (custom port)
set -e
cd "$(dirname "$0")"
PORT="${PORT:-8000}"

export PYTHONPATH="$PWD/.pkgs"
if ! python3 -c "import fastapi, uvicorn" 2>/dev/null; then
  echo "[run.sh] deps missing — installing fastapi+uvicorn into .pkgs/ (one-time)…"
  pip3 install --quiet --target "$PWD/.pkgs" fastapi "uvicorn[standard]"
fi

echo "[run.sh] starting RajScore on 0.0.0.0:$PORT"
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
