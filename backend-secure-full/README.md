
# Sift Mail — Backend Secure FULL

Adds `/messages/recent` and `/messages/action` on top of OAuth + rules + shadow + batch + digest + audit.
All non-OAuth endpoints require: `X-API-Key: <your key>`.

## Run
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env
mkdir -p tokens data/settings data/rules data/logs
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
