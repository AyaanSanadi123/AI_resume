from typing import List
from pydantic import BaseModel, Field

class InterviewSignal(BaseModel):
    demonstrated_technical_strengths: List[str] = Field(default_factory=list)
    inferred_technical_competencies: List[str] = Field(default_factory=list)
    missing_technologies: List[str] = Field(default_factory=list)
    competency_gaps: List[str] = Field(default_factory=list)
    project_complexity: str
    project_diversity: str
    architecture_exposure: str
    deployment_exposure: str
    research_exposure: str
    software_engineering_maturity: str
    technical_breadth: str
    domain_expertise: str
    experience_maturity: str
    education_and_certification_coverage: str
    leadership_indicators: List[str] = Field(default_factory=list)
    ownership_indicators: List[str] = Field(default_factory=list)
    communication_opportunities: List[str] = Field(default_factory=list)
    areas_requiring_verification: List[str] = Field(default_factory=list)
