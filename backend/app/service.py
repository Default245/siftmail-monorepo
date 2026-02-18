import re
from typing import List

from .config import Settings
from .schemas import ClassificationRequest, ClassificationResponse


def _score_keywords(text: str, keywords: List[str]) -> tuple[float, List[str]]:
    lowered = text.lower()
    hits = [kw for kw in keywords if kw.lower() in lowered]
    score = min(1.0, len(hits) * 0.15)
    return score, hits


def _score_domains(sender: str, urls: List[str], phishing_domains: List[str]) -> tuple[float, List[str]]:
    domains_found: List[str] = []
    pattern = re.compile(r"https?://([^/]+)/?")
    for url in urls:
        match = pattern.match(url)
        if match:
            domains_found.append(match.group(1).lower())
    domains_found.append(sender.split("@")[-1].lower())

    flagged = [domain for domain in domains_found if domain in {d.lower() for d in phishing_domains}]
    return (0.25 if flagged else 0.0), flagged


def classify_message(message: ClassificationRequest, settings: Settings) -> ClassificationResponse:
    text = f"{message.subject}\n{message.body}"
    score = 0.05  # base score for unknown senders
    reasons: List[str] = []
    flags: List[str] = []

    keyword_score, keyword_hits = _score_keywords(text, settings.spam_keywords)
    if keyword_hits:
        score += keyword_score
        reasons.append(f"Matched spam keywords: {', '.join(keyword_hits)}")
        flags.append("spam-keywords")

    domain_score, suspicious_domains = _score_domains(message.sender, [str(u) for u in message.urls], settings.phishing_domains)
    if suspicious_domains:
        score += domain_score
        reasons.append(f"Suspicious domain(s): {', '.join(suspicious_domains)}")
        flags.append("suspicious-domain")

    if len(message.attachments) > 2:
        score += 0.1
        reasons.append("Message contained multiple attachments")
        flags.append("many-attachments")

    if message.metadata and message.metadata.ip_address:
        if message.metadata.ip_address.startswith("10.") or message.metadata.ip_address.startswith("192.168"):
            reasons.append("Message originated from a private network")
            flags.append("private-ip")

    score = min(score, 1.0)
    verdict = "clean"
    threshold = settings.classification_threshold
    if score >= 0.8:
        verdict = "spam"
    elif score >= threshold:
        verdict = "suspicious"

    if not reasons:
        reasons.append("No obvious risk factors detected; message treated as clean")

    return ClassificationResponse(verdict=verdict, risk_score=round(score, 3), reasons=reasons, flags=flags)
