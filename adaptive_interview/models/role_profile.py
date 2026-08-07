from typing import List, Dict
from pydantic import BaseModel, Field

class RoleProfile(BaseModel):
    industry: str
    domain: str
    specialization: str
    seniority: str
    experience_required: str
    primary_responsibilities: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    required_competencies: List[str] = Field(default_factory=list)
    behavioral_competencies: List[str] = Field(default_factory=list)
    priority_weights: Dict[str, float] = Field(default_factory=dict)
    related_concepts: List[str] = Field(default_factory=list)
