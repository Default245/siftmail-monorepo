from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
import os
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session

load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8080/oauth/callback")
SCOPE = ["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/gmail.modify"]

AUTH_BASE = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

app = FastAPI()

@app.get("/")
def root():
    return {"ok": True, "service": "sift-backend-starter"}

@app.get("/auth/start")
def auth_start():
    if not CLIENT_ID or not CLIENT_SECRET:
        return PlainTextResponse("Missing GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET in .env", status_code=400)
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPE)
    auth_url, state = oauth.authorization_url(AUTH_BASE, access_type="offline", prompt="consent")
    os.environ["OAUTH_STATE"] = state
    return RedirectResponse(auth_url)

@app.get("/oauth/callback")
def oauth_callback(request: Request):
    state = os.environ.get("OAUTH_STATE", None)
    if state is None:
        return PlainTextResponse("Missing OAuth state; start again at /auth/start", status_code=400)
    full_url = str(request.url)
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPE, state=state)
    token = oauth.fetch_token(TOKEN_URL, client_secret=CLIENT_SECRET, authorization_response=full_url)
    access_token = token.get("access_token")
    refresh_token = token.get("refresh_token")
    html = f"""
    <h2>Tokens received</h2>
    <p><b>Access Token:</b> {access_token}</p>
    <p><b>Refresh Token:</b> {refresh_token}</p>
    <p>Copy the <b>Refresh Token</b> into your <code>.env</code> as <code>GOOGLE_REFRESH_TOKEN</code>.</p>
    """
    print("=== OAUTH TOKENS ===")
    print("ACCESS:", access_token)
    print("REFRESH:", refresh_token)
    print("====================")
    return HTMLResponse(content=html)
