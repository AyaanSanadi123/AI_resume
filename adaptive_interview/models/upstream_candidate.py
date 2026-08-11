from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class UpstreamCandidate(BaseModel):
    name: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    education: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[Dict[str, Any]] = Field(default_factory=list)
    awards_and_honors: List[str] = Field(default_factory=list)
    contact_info: Optional[Dict[str, Any]] = None
