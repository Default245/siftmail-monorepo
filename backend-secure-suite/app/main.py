
import os, uuid, time, json, httpx, re
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Request, Response, HTTPException, Body, Query, Path as FPath, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse
from dotenv import load_dotenv
from itsdangerous import URLSafeSerializer, BadSignature
from pydantic import BaseModel

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

load_dotenv()

# ---------- Config ----------
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8080/auth/callback")
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")]
SESSION_SECRET = os.getenv("SESSION_SECRET", "dev-secret-change-me")
API_KEY = os.getenv("API_KEY")

TOKEN_STORE = Path(os.getenv("TOKEN_STORE", "./tokens"))
DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", "30"))
DEFAULT_QUARANTINE_LABEL = os.getenv("DEFAULT_QUARANTINE_LABEL", "Sift/Quarantine")

for p in [TOKEN_STORE, DATA_DIR / "settings", DATA_DIR / "rules", DATA_DIR / "logs"]:
    p.mkdir(parents=True, exist_ok=True)

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
GOOGLE_REVOKE_URL = "https://oauth2.googleapis.com/revoke"
SCOPES = "openid email https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/gmail.modify"

app = FastAPI(title="Sift Mail Backend (Secure Suite)", version="0.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS + ["http://localhost:3000","http://127.0.0.1:3000","http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

signer = URLSafeSerializer(SESSION_SECRET, salt="siftmail-oauth")

# ---------- API key guard ----------
def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="Server API key not configured")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True

# ---------- Persistence helpers ----------
def user_key(email:str)->str:
    return email.replace("/", "_")

def token_path(email:str) -> Path:
    return TOKEN_STORE / f"{user_key(email)}.json"

def save_tokens(email:str, data:dict):
    token_path(email).write_text(json.dumps(data, indent=2))

def load_tokens(email:str) -> dict:
    p = token_path(email)
    if not p.exists():
        raise FileNotFoundError("No tokens for user")
    return json.loads(p.read_text())

def settings_path(email:str)->Path:
    return DATA_DIR / "settings" / f"{user_key(email)}.json"

def load_settings(email:str)->dict:
    p = settings_path(email)
    if p.exists():
        return json.loads(p.read_text())
    return {"shadow": True}

def save_settings(email:str, data:dict):
    settings_path(email).write_text(json.dumps(data, indent=2))

def rules_path(email:str)->Path:
    return DATA_DIR / "rules" / f"{user_key(email)}.json"

def load_rules(email:str)->dict:
    p = rules_path(email)
    if p.exists():
        return json.loads(p.read_text())
    return {"allow": [], "block": []}

def save_rules(email:str, data:dict):
    rules_path(email).write_text(json.dumps(data, indent=2))

def audit_path(email:str)->Path:
    return DATA_DIR / "logs" / f"{user_key(email)}.jsonl"

def audit_append(email:str, entry:dict):
    with audit_path(email).open("a") as f:
        f.write(json.dumps(entry) + "\n")

def audit_list(email:str, limit:int=200)->List[dict]:
    p = audit_path(email)
    items = []
    if not p.exists():
        return items
    with p.open() as f:
        for line in f:
            try:
                items.append(json.loads(line))
            except Exception:
                pass
    return items[-limit:]

# ---------- Gmail client ----------
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

# ---------- Scoring ----------
import re
SUS_SUBJECT = re.compile(r"(free|winner|congratulations|urgent|verify|invoice|payment|limited|act now|gift|deal|promo|offer)", re.I)
SUS_FROM = re.compile(r"(noreply@|no-reply@|mailer-daemon|.*\.(ru|cn|tk|xyz|top|icu)$)", re.I)
SUS_DOMAINS = re.compile(r"(bit\\.ly|linktr\\.ee|tinyurl\\.com|t\\.co|kutt\\.it)", re.I)

def sender_parts(headers:Dict[str,str]):
    fromv = headers.get("From","") or ""
    m = re.search(r"<([^>]+)>", fromv)
    addr = (m.group(1) if m else fromv).strip().lower()
    dom = addr.split("@")[-1] if "@" in addr else ""
    return addr, dom

def score_email(headers: Dict[str,str], snippet:str="", allow:list=None, block:list=None) -> Dict[str, Any]:
    allow = allow or []
    block = block or []
    score = 0.0
    reasons = []
    subj = headers.get("Subject", "") or ""
    addr, dom = sender_parts(headers)
    rp = headers.get("Return-Path", "") or ""

    if any(e.lower() in (addr, "@"+dom) for e in [a.lower() for a in allow]):
        return {"score": 0.0, "reasons": ["allowlist"]}
    if any(e.lower() in (addr, "@"+dom, dom) for e in [b.lower() for b in block]):
        score += 0.6; reasons.append("blocklist")

    if SUS_SUBJECT.search(subj): score += 0.3; reasons.append("subject_pattern")
    if SUS_FROM.search(addr) or SUS_FROM.search(rp): score += 0.25; reasons.append("sender_pattern")
    if "List-Unsubscribe" not in headers: score += 0.1; reasons.append("no_unsubscribe")
    if SUS_DOMAINS.search(snippet or ""): score += 0.15; reasons.append("link_shortener")
    if snippet and len(snippet) < 20: score += 0.05; reasons.append("short_snippet")
    score = min(score, 1.0)
    return {"score": round(score,2), "reasons": reasons}

# ---------- Models ----------
class ModeIn(BaseModel):
    email: str
    shadow: bool

class RulesIn(BaseModel):
    email: str
    entries: List[str]

# ---------- Routes ----------
@app.get("/health")  # keep open or lock with key if you prefer
def health():
    return {"ok": True, "time": int(time.time())}

# OAuth endpoints remain OPEN (browser redirects can't set headers easily)
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
    response.set_cookie("oauth_state", URLSafeSerializer(SESSION_SECRET, salt="siftmail-oauth").dumps(state), httponly=True, samesite="lax", max_age=600)
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
    email = None
    async with httpx.AsyncClient(timeout=20.0) as client:
        r2 = await client.get(GOOGLE_USERINFO_URL, headers={"Authorization": f"Bearer {tokens.get('access_token')}"})
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
    s = load_settings(email); s.setdefault("shadow", True); save_settings(email, s)
    audit_append(email, {"ts": int(time.time()), "event":"oauth_connected", "email": email})

    html = f"<html><body><h2>Connected ✓</h2><p>Account: <strong>{email}</strong></p><p>You can close this tab and return to the app.</p></body></html>"
    resp = HTMLResponse(content=html)
    resp.delete_cookie("oauth_state")
    return resp

# ---- Protected endpoints (require X-API-Key) ----
@app.post("/account/revoke", dependencies=[Depends(verify_api_key)])
async def account_revoke(email: str = Body(..., embed=True)):
    try:
        t = load_tokens(email)
        token = t.get("access_token") or t.get("refresh_token")
        async with httpx.AsyncClient(timeout=15.0) as c:
            await c.post(GOOGLE_REVOKE_URL, data={"token": token}, headers={"Content-Type":"application/x-www-form-urlencoded"})
    except Exception:
        pass
    try: token_path(email).unlink(missing_ok=True)
    except Exception: pass
    audit_append(email, {"ts": int(time.time()), "event":"account_revoked"})
    return {"ok": True}

@app.post("/account/delete", dependencies=[Depends(verify_api_key)])
def account_delete(email: str = Body(..., embed=True)):
    try: token_path(email).unlink(missing_ok=True)
    except Exception: pass
    for p in [DATA_DIR / "settings" / f"{user_key(email)}.json",
              DATA_DIR / "rules" / f"{user_key(email)}.json",
              DATA_DIR / "logs" / f"{user_key(email)}.jsonl"]:
        try: Path(p).unlink(missing_ok=True)
        except Exception: pass
    return {"ok": True}

@app.get("/mode", dependencies=[Depends(verify_api_key)])
def get_mode(email: str):
    return load_settings(email)

@app.post("/mode", dependencies=[Depends(verify_api_key)])
def set_mode(body: ModeIn):
    s = load_settings(body.email)
    s["shadow"] = bool(body.shadow)
    save_settings(body.email, s)
    audit_append(body.email, {"ts": int(time.time()), "event":"mode_set", "shadow": s["shadow"]})
    return s

@app.get("/rules", dependencies=[Depends(verify_api_key)])
def get_rules(email: str):
    return load_rules(email)

@app.post("/rules/allow", dependencies=[Depends(verify_api_key)])
def add_allow(body: RulesIn):
    r = load_rules(body.email)
    r["allow"] = sorted(list(set(r.get("allow", []) + body.entries)))
    save_rules(body.email, r)
    audit_append(body.email, {"ts": int(time.time()), "event":"rules_allow_add", "entries": body.entries})
    return r

@app.post("/rules/block", dependencies=[Depends(verify_api_key)])
def add_block(body: RulesIn):
    r = load_rules(body.email)
    r["block"] = sorted(list(set(r.get("block", []) + body.entries)))
    save_rules(body.email, r)
    audit_append(body.email, {"ts": int(time.time()), "event":"rules_block_add", "entries": body.entries})
    return r

def get_message_headers(svc, msg_id: str) -> Dict[str, Any]:
    full = svc.users().messages().get(userId="me", id=msg_id, format="metadata", metadataHeaders=[
        "From","Subject","Return-Path","Received","List-Unsubscribe","Delivered-To","To","Date","Message-ID"
    ]).execute()
    headers = {h["name"]: h["value"] for h in full.get("payload", {}).get("headers", [])}
    return {"id": msg_id, "snippet": full.get("snippet"), "internalDate": full.get("internalDate"), "headers": headers}

def ensure_label(svc, name: str) -> str:
    lbls = svc.users().labels().list(userId="me").execute().get("labels", [])
    for l in lbls:
        if l.get("name") == name:
            return l.get("id")
    created = svc.users().labels().create(userId="me", body={"name": name, "labelListVisibility":"labelShow","messageListVisibility":"show"}).execute()
    return created.get("id")

@app.get("/gmail/profile", dependencies=[Depends(verify_api_key)])
def gmail_profile(email: str = Query(...)):
    try:
        svc = gmail_service_from_email(email)
        return svc.users().getProfile(userId="me").execute()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/gmail/labels", dependencies=[Depends(verify_api_key)])
def gmail_labels(email: str):
    try:
        svc = gmail_service_from_email(email)
        return {"labels": svc.users().labels().list(userId="me").execute().get("labels", [])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/gmail/messages", dependencies=[Depends(verify_api_key)])
def gmail_messages(email: str, label: str = "INBOX", max_results: int = 25, q: Optional[str]=None):
    try:
        svc = gmail_service_from_email(email)
        res = svc.users().messages().list(userId="me", labelIds=[label] if label else None, q=q, maxResults=max_results).execute()
        out = [get_message_headers(svc, m["id"]) for m in res.get("messages", [])]
        return {"messages": out}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/gmail/messages/{message_id}", dependencies=[Depends(verify_api_key)])
def gmail_message(email: str, message_id: str = FPath(...)):
    try:
        svc = gmail_service_from_email(email)
        return get_message_headers(svc, message_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/gmail/score", dependencies=[Depends(verify_api_key)])
def gmail_score(email: str = Body(..., embed=True), message_id: str = Body(..., embed=True)):
    try:
        svc = gmail_service_from_email(email)
        rules = load_rules(email)
        meta = get_message_headers(svc, message_id)
        sc = score_email(meta["headers"], meta.get("snippet",""), rules.get("allow"), rules.get("block"))
        return {"id": message_id, **sc}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/gmail/quarantine", dependencies=[Depends(verify_api_key)])
def gmail_quarantine(email: str = Body(..., embed=True), message_id: str = Body(..., embed=True), label_name: str = Body(DEFAULT_QUARANTINE_LABEL, embed=True)):
    try:
        svc = gmail_service_from_email(email)
        settings = load_settings(email)
        rules = load_rules(email)
        meta = get_message_headers(svc, message_id)
        sc = score_email(meta["headers"], meta.get("snippet",""), rules.get("allow"), rules.get("block"))

        action = "would_quarantine" if settings.get("shadow", True) else "quarantine"
        if not settings.get("shadow", True):
            qid = ensure_label(svc, label_name)
            svc.users().messages().modify(userId="me", id=message_id, body={"addLabelIds":[qid], "removeLabelIds":["INBOX"]}).execute()

        audit_append(email, {"ts": int(time.time()), "event": action, "id": message_id, "score": sc["score"], "reasons": sc["reasons"]})
        return {"ok": True, "action": action, "score": sc["score"], "reasons": sc["reasons"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/gmail/undo", dependencies=[Depends(verify_api_key)])
def gmail_undo(email: str = Body(..., embed=True), message_id: str = Body(..., embed=True), label_name: str = Body(DEFAULT_QUARANTINE_LABEL, embed=True)):
    try:
        svc = gmail_service_from_email(email)
        settings = load_settings(email)
        action = "would_restore" if settings.get("shadow", True) else "restore"
        if not settings.get("shadow", True):
            qid = None
            for l in svc.users().labels().list(userId="me").execute().get("labels", []):
                if l.get("name") == label_name:
                    qid = l.get("id"); break
            svc.users().messages().modify(userId="me", id=message_id, body={"addLabelIds":["INBOX"], "removeLabelIds":[qid] if qid else []}).execute()
        audit_append(email, {"ts": int(time.time()), "event": action, "id": message_id})
        return {"ok": True, "action": action}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/gmail/batch-classify", dependencies=[Depends(verify_api_key)])
def gmail_batch_classify(
    email: str = Body(..., embed=True),
    label: str = Body("INBOX", embed=True),
    max_results: int = Body(50, embed=True),
    quarantine_threshold: float = Body(0.7, embed=True),
    dry_run: bool = Body(True, embed=True),
    quarantine_label: str = Body(DEFAULT_QUARANTINE_LABEL, embed=True)
):
    try:
        svc = gmail_service_from_email(email)
        settings = load_settings(email)
        rules = load_rules(email)
        res = svc.users().messages().list(userId="me", labelIds=[label] if label else None, maxResults=max_results).execute()

        apply_actions = (not dry_run) and (not settings.get("shadow", True))
        qid = ensure_label(svc, quarantine_label) if apply_actions else None

        results = []
        for m in res.get("messages", []):
            meta = get_message_headers(svc, m["id"])
            sc = score_email(meta["headers"], meta.get("snippet",""), rules.get("allow"), rules.get("block"))
            action = "none"
            if sc["score"] >= quarantine_threshold:
                action = "would_quarantine"
                if apply_actions:
                    svc.users().messages().modify(userId="me", id=m["id"], body={"addLabelIds":[qid], "removeLabelIds":["INBOX"]}).execute()
                    action = "quarantine"
            results.append({"id": m["id"], "score": sc["score"], "reasons": sc["reasons"], "action": action})
            if action in ("quarantine","would_quarantine"):
                audit_append(email, {"ts": int(time.time()), "event": action, "id": m["id"], "score": sc["score"]})

        return {"email": email, "label": label, "threshold": quarantine_threshold, "dry_run": dry_run or settings.get("shadow", True), "count": len(results), "items": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/digest", dependencies=[Depends(verify_api_key)])
def digest(email: str, label: str = DEFAULT_QUARANTINE_LABEL, limit:int=50, html: bool=False):
    try:
        svc = gmail_service_from_email(email)
        res = svc.users().messages().list(userId="me", labelIds=[label], maxResults=limit).execute()
        items = []
        for m in res.get("messages", []):
            meta = get_message_headers(svc, m["id"])
            items.append({
                "id": m["id"],
                "from": meta["headers"].get("From"),
                "subject": meta["headers"].get("Subject"),
                "snippet": meta.get("snippet",""),
                "date": meta["headers"].get("Date")
            })
        if html:
            rows = "".join([f"<tr><td>{i['from']}</td><td>{i['subject']}</td><td>{i['snippet']}</td><td>{i['date']}</td></tr>" for i in items])
            page = f"<html><body><h2>Sift Mail Digest</h2><table border='1' cellpadding='6'><tr><th>From</th><th>Subject</th><th>Snippet</th><th>Date</th></tr>{rows}</table></body></html>"
            return HTMLResponse(content=page)
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/audit", dependencies=[Depends(verify_api_key)])
def audit(email: str, limit:int=200):
    return {"items": audit_list(email, limit=limit)}
