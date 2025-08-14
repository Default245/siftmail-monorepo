
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import os, datetime

load_dotenv()
API_KEY = os.getenv("API_KEY")

def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if API_KEY is None:
        # No key set -> lock down by default
        raise HTTPException(status_code=500, detail="Server API key not configured")
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True

app = FastAPI(title="SiftMail Backend (API Key Protected)")

class Email(BaseModel):
    id: str
    subject: str
    sender: str
    body: str

class ClassificationResult(BaseModel):
    id: str
    classification: str

@app.get("/health", dependencies=[Depends(verify_api_key)])
def health_check():
    return {"status": "ok", "timestamp": datetime.datetime.utcnow().isoformat()}

@app.post("/classify_batch", response_model=List[ClassificationResult], dependencies=[Depends(verify_api_key)])
def classify_batch(emails: List[Email]):
    results = []
    for email in emails:
        text = (email.subject + " " + email.body).lower()
        classification = "spam" if any(k in text for k in ["buy now", "free", "limited offer"]) else "inbox"
        results.append({"id": email.id, "classification": classification})
    return results

@app.post("/quarantine", dependencies=[Depends(verify_api_key)])
def quarantine_email(email_id: str):
    # placeholder action
    return {"status": "quarantined", "email_id": email_id}

@app.get("/digest", dependencies=[Depends(verify_api_key)])
def daily_digest():
    # placeholder content
    return {"digest": "Daily summary of quarantined and classified emails."}
