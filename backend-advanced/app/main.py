
import os, uuid, time, json, httpx, re
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Request, Response, HTTPException, Body, Query, Path as FPath
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from dotenv import load_dotenv
from itsdangerous import URLSafeSerializer, BadSignature

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8080/auth/callback")
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")]
SESSION_SECRET = os.getenv("SESSION_SECRET", "dev-secret-change-me")
TOKEN_STORE = Path(os.getenv("TOKEN_STORE", "./tokens"))
TOKEN_STORE.mkdir(parents=True, exist_ok=True)

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
SCOPES = "openid email https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/gmail.modify"

app = FastAPI(title="Sift Mail Backend", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS + ["http://localhost:3000","http://127.0.0.1:3000","http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

signer = URLSafeSerializer(SESSION_SECRET, salt="siftmail-oauth")

def token_path(email:str) -> Path:
    safe = email.replace("/", "_")
    return TOKEN_STORE / f"{safe}.json"

def save_tokens(email:str, data:dict):
    token_path(email).write_text(json.dumps(data, indent=2))

def load_tokens(email:str) -> dict:
    p = token_path(email)
    if not p.exists():
        raise FileNotFoundError("No tokens for user")
    return json.loads(p.read_text())

def gmail_service_from_email(email:str):
    data = load_tokens(email)
    creds = Credentials(
        token=data.get("access_token"),
        refresh_token=data.get("refresh_token"),
        token_uri=GOOGLE_TOKEN_URL,
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=SCOPES.split(" ")
    )
    return build("gmail", "v1", credentials=creds)

@app.get("/health")
def health():
    return {"ok": True, "time": int(time.time())}

@app.get("/auth/start")
def auth_start(response: Response, redirect_uri: Optional[str]=None):
    state = str(uuid.uuid4())
    response = RedirectResponse(
        url=(
            f"{GOOGLE_AUTH_URL}?response_type=code"
            f"&client_id={GOOGLE_CLIENT_ID}"
            f"&redirect_uri={(redirect_uri or GOOGLE_REDIRECT_URI)}"
            f"&scope={SCOPES}"
            f"&access_type=offline&prompt=consent"
            f"&state={state}"
        ),
        status_code=302,
    )
    response.set_cookie("oauth_state", signer.dumps(state), httponly=True, samesite="lax", max_age=600)
    return response

@app.get("/auth/callback")
async def auth_callback(request: Request, code: Optional[str]=None, state: Optional[str]=None):
    cookie = request.cookies.get("oauth_state")
    if not (code and state and cookie):
        raise HTTPException(status_code=400, detail="Missing code/state/cookie")
    try:
        original_state = URLSafeSerializer(SESSION_SECRET, salt="siftmail-oauth").loads(cookie)
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid state signature")
    if original_state != state:
        raise HTTPException(status_code=400, detail="State mismatch")

    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.post(GOOGLE_TOKEN_URL, data=data, headers={"Content-Type":"application/x-www-form-urlencoded"})
    if r.status_code != 200:
        return JSONResponse(status_code=r.status_code, content={"error":"token_exchange_failed","detail":r.text})

    tokens = r.json()

    # Get user email via userinfo
    email = None
    async with httpx.AsyncClient(timeout=20.0) as client:
        r2 = await client.get("https://openidconnect.googleapis.com/v1/userinfo", headers={"Authorization": f"Bearer {tokens.get('access_token')}"})
        if r2.status_code == 200:
            email = r2.json().get("email")
    if not email:
        try:
            svc = build("gmail","v1",credentials=Credentials(tokens.get("access_token")))
            email = svc.users().getProfile(userId="me").execute().get("emailAddress")
        except Exception:
            email = None
    if not email:
        return JSONResponse(status_code=500, content={"error":"email_lookup_failed"})

    save_tokens(email, tokens)
    html = f"<html><body><h2>Connected ✓</h2><p>Account: <strong>{email}</strong></p></body></html>"
    resp = JSONResponse(content={"ok": True, "email": email})
    resp.delete_cookie("oauth_state")
    return resp

# Helpers
def ensure_label(svc, name: str) -> str:
    lbls = svc.users().labels().list(userId="me").execute().get("labels", [])
    for l in lbls:
        if l.get("name") == name:
            return l.get("id")
    created = svc.users().labels().create(userId="me", body={"name": name, "labelListVisibility":"labelShow","messageListVisibility":"show"}).execute()
    return created.get("id")

def get_message_headers(svc, msg_id: str) -> Dict[str, Any]:
    full = svc.users().messages().get(userId="me", id=msg_id, format="metadata", metadataHeaders=[
        "From","Subject","Return-Path","Received","List-Unsubscribe","Delivered-To","To","Date","Message-ID"
    ]).execute()
    headers = {h["name"]: h["value"] for h in full.get("payload", {}).get("headers", [])}
    return {"id": msg_id, "snippet": full.get("snippet"), "internalDate": full.get("internalDate"), "headers": headers}

SUS_SUBJECT = re.compile(r"(free|winner|congratulations|urgent|verify|invoice|payment|limited|act now|gift|deal|promo|offer)", re.I)
SUS_FROM = re.compile(r"(noreply@|no-reply@|mailer-daemon|.*\.(ru|cn|tk|xyz|top|icu)$)", re.I)
SUS_DOMAINS = re.compile(r"(bit\.ly|linktr\.ee|tinyurl\.com|t\.co|kutt\.it)", re.I)

def score_email(headers: Dict[str,str], snippet:str="") -> Dict[str, Any]:
    score = 0.0
    reasons = []
    subj = headers.get("Subject", "") or ""
    fromv = headers.get("From", "") or ""
    rp = headers.get("Return-Path", "") or ""

    if SUS_SUBJECT.search(subj): score += 0.3; reasons.append("subject_pattern")
    if SUS_FROM.search(fromv) or SUS_FROM.search(rp): score += 0.25; reasons.append("sender_pattern")
    if "List-Unsubscribe" not in headers: score += 0.1; reasons.append("no_unsubscribe")
    if SUS_DOMAINS.search(snippet or ""): score += 0.15; reasons.append("link_shortener")
    if snippet and len(snippet) < 20: score += 0.05; reasons.append("short_snippet")
    score = min(score, 1.0)
    return {"score": round(score,2), "reasons": reasons}

@app.get("/gmail/profile")
def gmail_profile(email: str = Query(...)):
    try:
        svc = gmail_service_from_email(email)
        return svc.users().getProfile(userId="me").execute()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/gmail/labels")
def gmail_labels(email: str):
    try:
        svc = gmail_service_from_email(email)
        return {"labels": svc.users().labels().list(userId="me").execute().get("labels", [])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/gmail/messages")
def gmail_messages(email: str, label: str = "INBOX", max_results: int = 25, q: Optional[str]=None):
    try:
        svc = gmail_service_from_email(email)
        res = svc.users().messages().list(userId="me", labelIds=[label] if label else None, q=q, maxResults=max_results).execute()
        out = [get_message_headers(svc, m["id"]) for m in res.get("messages", [])]
        return {"messages": out}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/gmail/messages/{message_id}")
def gmail_message(email: str, message_id: str = FPath(...)):
    try:
        svc = gmail_service_from_email(email)
        return get_message_headers(svc, message_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/gmail/score")
def gmail_score(email: str = Body(..., embed=True), message_id: str = Body(..., embed=True)):
    try:
        svc = gmail_service_from_email(email)
        meta = get_message_headers(svc, message_id)
        sc = score_email(meta["headers"], meta.get("snippet",""))
        return {"id": message_id, **sc}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/gmail/quarantine")
def gmail_quarantine(email: str = Body(..., embed=True), message_id: str = Body(..., embed=True), label_name: str = Body("Sift/Quarantine", embed=True)):
    try:
        svc = gmail_service_from_email(email)
        qid = ensure_label(svc, label_name)
        svc.users().messages().modify(userId="me", id=message_id, body={"addLabelIds":[qid], "removeLabelIds":["INBOX"]}).execute()
        return {"ok": True, "label": label_name}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/gmail/undo")
def gmail_undo(email: str = Body(..., embed=True), message_id: str = Body(..., embed=True), label_name: str = Body("Sift/Quarantine", embed=True)):
    try:
        svc = gmail_service_from_email(email)
        qid = None
        for l in svc.users().labels().list(userId="me").execute().get("labels", []):
            if l.get("name") == label_name:
                qid = l.get("id"); break
        svc.users().messages().modify(userId="me", id=message_id, body={"addLabelIds":["INBOX"], "removeLabelIds":[qid] if qid else []}).execute()
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/gmail/batch-classify")
def gmail_batch_classify(email: str = Body(..., embed=True), label: str = Body("INBOX", embed=True), max_results: int = Body(50, embed=True), quarantine_threshold: float = Body(0.7, embed=True), dry_run: bool = Body(True, embed=True), quarantine_label: str = Body("Sift/Quarantine", embed=True)):
    try:
        svc = gmail_service_from_email(email)
        res = svc.users().messages().list(userId="me", labelIds=[label] if label else None, maxResults=max_results).execute()
        qid = ensure_label(svc, quarantine_label) if not dry_run else None
        results = []
        to_quarantine = []

        for m in res.get("messages", []):
            meta = get_message_headers(svc, m["id"])
            sc = score_email(meta["headers"], meta.get("snippet",""))
            action = "none"
            if sc["score"] >= quarantine_threshold:
                action = "quarantine" if not dry_run else "would_quarantine"
                if not dry_run: to_quarantine.append(m["id"])
            results.append({"id": m["id"], "score": sc["score"], "reasons": sc["reasons"], "action": action})

        if not dry_run:
            for mid in to_quarantine:
                svc.users().messages().modify(userId="me", id=mid, body={"addLabelIds":[qid], "removeLabelIds":["INBOX"]}).execute()

        return {"email": email, "label": label, "threshold": quarantine_threshold, "dry_run": dry_run, "count": len(results), "items": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

