
# Sift Mail — Backend Secure Suite (API Key + OAuth + Rules + Shadow + Batch + Digest)

**All non-OAuth endpoints require** `X-API-Key: <your key>`.

## Quick start
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env   # set API_KEY and Google creds
mkdir -p tokens data/settings data/rules data/logs
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

## Notes
- `/auth/start` and `/auth/callback` are open for browser redirects.
- Everything else is protected by API key.
- Shadow Mode keeps actions non-destructive until turned off via `POST /mode`.
