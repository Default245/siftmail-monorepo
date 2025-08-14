# Sift Backend Starter (FastAPI + Gmail OAuth)

This is a minimal backend to finish the Gmail OAuth flow and verify your Google Workspace setup.

## What this does
- Serves an **/auth/start** route that redirects you to Google for consent
- Receives the callback on **/oauth/callback**
- Exchanges the code for **access_token** and **refresh_token**
- Prints tokens in the server log and shows them in your browser once, so you can paste them into `.env`

## Quick start (macOS)
1) Install Python 3.10+ (macOS already has Python, but 3.10+ recommended)
2) In Terminal:
```bash
cd sift-backend-starter
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Open .env in a text editor and fill in GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET
# If you're running locally, leave GOOGLE_REDIRECT_URI=http://localhost:8080/oauth/callback
# Save the file, then run:
bash run.sh
```
3) Visit: http://localhost:8080/auth/start
4) Approve the Google consent screen (use your admin@siftmail.app account)
5) After redirect, the page will show your **refresh_token**. Copy it into `.env`:
```
GOOGLE_REFRESH_TOKEN=...paste here...
```
6) Restart the server (`Ctrl+C` then `bash run.sh`). You're set.

## Routes
- GET `/` — health check
- GET `/auth/start` — begins OAuth consent
- GET `/oauth/callback` — receives code, exchanges tokens

## Next steps
- Wire `/v0/gmail/webhook` and Pub/Sub later.
- Use the tokens to call Gmail API endpoints (users.watch, users.history.list, users.messages.*).
