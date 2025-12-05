from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert "environment" in payload


def test_classify_returns_response():
    request_body = {
        "subject": "Reset your password and claim your reward",
        "body": "Click the urgent link below to wire transfer your winnings.",
        "sender": "alerts@example-phish.com",
        "recipient": "user@example.com",
        "urls": ["https://example-phish.com/reset"],
        "attachments": ["invoice.pdf"],
    }
    response = client.post("/api/sift/classify", json=request_body)
    assert response.status_code == 200
    payload = response.json()
    assert payload["verdict"] in {"spam", "suspicious", "clean"}
    assert 0 <= payload["risk_score"] <= 1
    assert payload["reasons"]


def test_batch_classification():
    request_body = {
        "messages": [
            {
                "subject": "Company update",
                "body": "Quarterly update with meeting link",
                "sender": "team@example.com",
                "recipient": "user@example.com",
                "urls": ["https://example.com/meeting"],
            },
            {
                "subject": "Urgent payment needed",
                "body": "wire transfer now to avoid penalty",
                "sender": "scam@dodgy-payments.io",
                "recipient": "user@example.com",
                "urls": ["https://dodgy-payments.io/pay"],
                "attachments": ["invoice.pdf", "statement.pdf", "details.pdf"],
            },
        ]
    }
    response = client.post("/api/sift/batch", json=request_body)
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    assert len(payload["results"]) == 2
