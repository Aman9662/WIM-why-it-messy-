"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel
from typing import Optional, Literal


class TextDetectRequest(BaseModel):
    text: str
    detection_type: Literal[
        "ai_content", "plagiarism", "fake_news",
        "fake_review", "fake_profile", "fake_job",
        "phishing", "code_plagiarism"
    ]


class UrlDetectRequest(BaseModel):
    url: str
    detection_type: Literal["fake_news", "fake_product", "phishing", "general"]


class DetectionResult(BaseModel):
    detection_type: str
    score: float
    verdict: str
    confidence: str
    breakdown: dict
    highlights: list[str]
    improvements: list[str]
    raw_analysis: str
