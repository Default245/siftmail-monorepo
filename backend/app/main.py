from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .schemas import (
    BatchClassificationRequest,
    BatchClassificationResponse,
    ClassificationRequest,
    ClassificationResponse,
    HealthResponse,
)
from .service import classify_message

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok", environment=settings.environment, app=settings.app_name)


@app.post("/api/sift/classify", response_model=ClassificationResponse)
def classify(payload: ClassificationRequest) -> ClassificationResponse:
    return classify_message(payload, settings)


@app.post("/api/sift/batch", response_model=BatchClassificationResponse)
def batch(payload: BatchClassificationRequest) -> BatchClassificationResponse:
    results = [classify_message(message, settings) for message in payload.messages]
    return BatchClassificationResponse(total=len(results), results=results)
