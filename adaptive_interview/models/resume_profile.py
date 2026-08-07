from typing import List, Optional
from pydantic import BaseModel, Field

class Project(BaseModel):
    title: str
    description: str

class ResumeProfile(BaseModel):
    candidate_name: str
    role: str
    experience_level: str
    skills_found: List[str] = Field(default_factory=list)
    job_description: str = ""
    projects: List[Project] = Field(default_factory=list)
