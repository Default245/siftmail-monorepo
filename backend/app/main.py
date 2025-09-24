"""SiftMail backend skeleton with richer inbox intelligence endpoints."""

from __future__ import annotations

from collections import Counter
from textwrap import shorten
from typing import Dict, List

from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(title="SiftMail Inbox Platform", version="0.2.0")


class EmailMessage(BaseModel):
    """Minimal representation of an email message we can score and categorize."""

    id: str
    sender: str
    subject: str
    body: str
    account: str = Field(default="primary", description="Account identifier")
    importance: int = Field(
        default=5,
        ge=0,
        le=10,
        description="Relative importance scored 0 (low) to 10 (critical).",
    )
    tags: List[str] = Field(default_factory=list)


class ClassifyRequest(BaseModel):
    message: EmailMessage


class Classification(BaseModel):
    category: str
    is_spam: bool
    phishing_signals: List[str]
    snippet: str
    confidence: float


class BatchRequest(BaseModel):
    messages: List[EmailMessage]


class BatchResponse(BaseModel):
    results: List[Classification]
    totals: Dict[str, int]
    spam_caught: int
    phishing_detected: int


class InboxSnapshotRequest(BaseModel):
    accounts: List[str]
    messages: List[EmailMessage]


class HighValueSummary(BaseModel):
    id: str
    subject: str
    sender: str
    snippet: str
    importance: int
    category: str


class InboxSnapshotResponse(BaseModel):
    synced_accounts: List[str]
    category_totals: Dict[str, int]
    high_value: List[HighValueSummary]
    inbox_zero_plan: Dict[str, int]
    suspicious_messages: int


CATEGORY_RULES = {
    "Finance": ["invoice", "receipt", "payment", "bank", "statement"],
    "Social": ["follow", "like", "comment", "invite", "friend"],
    "Updates": ["newsletter", "digest", "update", "release", "patch"],
    "Promotions": ["sale", "discount", "coupon", "deal", "offer"],
    "Travel": ["itinerary", "boarding", "hotel", "booking", "flight"],
}

PHISHING_CUES = {
    "urgent": "Urgency language detected",
    "wire transfer": "Wire transfer request",
    "reset your password": "Password reset lure",
    "confirm your account": "Account takeover lure",
    "bank details": "Bank credential request",
}

SPAM_KEYWORDS = [
    "free money",
    "act now",
    "winner",
    "click here",
    "weight loss",
    "crypto giveaway",
]


def _analyse_email(email: EmailMessage) -> Classification:
    combined_text = f"{email.subject} {email.body}".lower()
    category = "Primary"
    phishing_signals: List[str] = []
    matches = Counter()

    for label, keywords in CATEGORY_RULES.items():
        match_count = sum(1 for word in keywords if word in combined_text)
        if match_count:
            matches[label] = match_count

    if matches:
        category = matches.most_common(1)[0][0]

    spam_hits = sum(1 for word in SPAM_KEYWORDS if word in combined_text)
    is_spam = spam_hits >= 2

    for cue, description in PHISHING_CUES.items():
        if cue in combined_text:
            phishing_signals.append(description)

    if phishing_signals:
        category = "Security Alert"

    # Confidence increases with more signal matches and high importance.
    base_confidence = 0.55 + (0.08 * matches.get(category, 0))
    confidence = min(0.95, base_confidence + (email.importance * 0.02))

    snippet = shorten(email.body.strip().replace("\n", " "), width=140, placeholder="…")

    return Classification(
        category=category,
        is_spam=is_spam,
        phishing_signals=phishing_signals,
        snippet=snippet,
        confidence=round(confidence, 2),
    )


@app.get("/")
def root():
    return {"message": "SiftMail backend running"}


@app.post("/api/sift/classify", response_model=Classification)
def classify(request: ClassifyRequest):
    """Classify a single email with categories, spam score, and phishing insights."""

    return _analyse_email(request.message)


@app.post("/api/sift/batch", response_model=BatchResponse)
def batch(request: BatchRequest):
    """Classify a batch of emails and return aggregate stats to power the UI."""

    results = [_analyse_email(msg) for msg in request.messages]
    totals = Counter(result.category for result in results)
    spam_caught = sum(1 for result in results if result.is_spam)
    phishing_detected = sum(1 for result in results if result.phishing_signals)

    return BatchResponse(
        results=results,
        totals=dict(totals),
        spam_caught=spam_caught,
        phishing_detected=phishing_detected,
    )


@app.post("/api/inbox/snapshot", response_model=InboxSnapshotResponse)
def inbox_snapshot(request: InboxSnapshotRequest):
    """Summarise an inbox into categories, high-value snippets, and an inbox-zero plan."""

    analyses = [
        (email, _analyse_email(email))
        for email in request.messages
    ]

    totals = Counter(result.category for _, result in analyses)

    high_value_candidates = [
        (email, result)
        for email, result in analyses
        if not result.is_spam
        and not result.phishing_signals
        and email.importance >= 7
    ]

    high_value_sorted = sorted(
        high_value_candidates,
        key=lambda item: item[0].importance,
        reverse=True,
    )

    high_value = [
        HighValueSummary(
            id=email.id,
            subject=email.subject,
            sender=email.sender,
            snippet=result.snippet,
            importance=email.importance,
            category=result.category,
        )
        for email, result in high_value_sorted[:5]
    ]

    inbox_zero_plan = {
        "total_messages": len(request.messages),
        "auto_cleared": sum(1 for _, result in analyses if result.is_spam),
        "needs_review": len(high_value),
        "quick_archive": sum(
            1
            for _, result in analyses
            if result.category in {"Promotions", "Updates"}
            and not result.is_spam
        ),
    }

    suspicious_messages = sum(
        1 for _, result in analyses if result.phishing_signals
    )

    synced_accounts = sorted(set(request.accounts) | {email.account for email, _ in analyses})

    return InboxSnapshotResponse(
        synced_accounts=synced_accounts,
        category_totals=dict(totals),
        high_value=high_value,
        inbox_zero_plan=inbox_zero_plan,
        suspicious_messages=suspicious_messages,
    )