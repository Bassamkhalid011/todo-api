from typing import Literal
from pydantic import BaseModel, Field


class TriageInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)
    source: Literal["email", "slack", "form"]


class TriageOutput(BaseModel):
    category: Literal["bug", "feature", "question", "other"]
    priority: Literal["low", "medium", "high"]
    summary: str = Field(..., min_length=1, max_length=300)
    confidence: float = Field(..., ge=0.0, le=1.0)
