from typing import List, Optional
from pydantic import BaseModel, Field

class ATSAnalysis(BaseModel):
    ats_score: float
    semantic_similarity: float
    keyword_similarity: float
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    matched_keywords: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)
    missing_competencies: List[str] = Field(default_factory=list)
    candidate_strengths: List[str] = Field(default_factory=list)
    candidate_weaknesses: List[str] = Field(default_factory=list)
    reasoning: str
