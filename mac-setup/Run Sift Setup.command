#!/bin/bash
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR/sift-backend-starter"

# Prompt for Client ID/Secret
echo "Enter your GOOGLE_CLIENT_ID:"
read CLIENT_ID
echo "Enter your GOOGLE_CLIENT_SECRET:"
read CLIENT_SECRET

# Create .env
cat > .env <<EOF
GOOGLE_CLIENT_ID=$CLIENT_ID
GOOGLE_CLIENT_SECRET=$CLIENT_SECRET
GOOGLE_REDIRECT_URI=http://localhost:8080/oauth/callback
PORT=8080
SESSION_SECRET=$(openssl rand -hex 16 2>/dev/null || echo dev-secret)
ENV=development
GOOGLE_REFRESH_TOKEN=
GOOGLE_ACCESS_TOKEN=
EOF

# Python venv
if command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  echo "python3 not found. Install Xcode Command Line Tools or Python 3."
  exit 1
fi

$PY -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Start server
open "http://localhost:8080/auth/start" || true
uvicorn app.main:app --host 0.0.0.0 --port 8080
