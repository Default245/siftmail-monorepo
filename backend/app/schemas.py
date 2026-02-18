from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class MessageMetadata(BaseModel):
    ip_address: Optional[str] = Field(None, description="Origin IP if available")
    mail_client: Optional[str] = Field(None, description="Submitting mail client or agent")


class ClassificationRequest(BaseModel):
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body text")
    sender: EmailStr
    recipient: EmailStr
    urls: List[HttpUrl] = Field(default_factory=list)
    attachments: List[str] = Field(default_factory=list, description="Attachment file names if known")
    metadata: Optional[MessageMetadata] = None


class ClassificationResponse(BaseModel):
    verdict: str = Field(..., description="spam | suspicious | clean")
    risk_score: float = Field(..., ge=0, le=1)
    reasons: List[str]
    flags: List[str]


class BatchClassificationRequest(BaseModel):
    messages: List[ClassificationRequest]


class BatchClassificationResponse(BaseModel):
    total: int
    results: List[ClassificationResponse]


class HealthResponse(BaseModel):
    status: str
    environment: str
    app: str
