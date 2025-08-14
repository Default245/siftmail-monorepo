
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import datetime

app = FastAPI(title="SiftMail Backend")

class Email(BaseModel):
    id: str
    subject: str
    sender: str
    body: str

class ClassificationResult(BaseModel):
    id: str
    classification: str

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.datetime.utcnow()}

@app.post("/classify_batch", response_model=List[ClassificationResult])
def classify_batch(emails: List[Email]):
    results = []
    for email in emails:
        classification = "spam" if "buy now" in email.body.lower() else "inbox"
        results.append({"id": email.id, "classification": classification})
    return results

@app.post("/quarantine")
def quarantine_email(email_id: str):
    return {"status": "quarantined", "email_id": email_id}

@app.get("/digest")
def daily_digest():
    return {"digest": "Daily summary of quarantined and classified emails."}
