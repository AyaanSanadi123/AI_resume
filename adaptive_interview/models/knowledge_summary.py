from pydantic import BaseModel
from typing import List

class TechnologyRelationship(BaseModel):
    technology: str
    concept: str
    prerequisites: List[str]
    related_technologies: List[str]

class KnowledgeSummary(BaseModel):
    role_domain: str
    primary_technical_areas: List[str]
    candidate_demonstrated_technologies: List[str]
    role_required_technologies: List[str]
    candidate_missing_technologies: List[str]
    core_concepts: List[str]
    technology_relationships: List[TechnologyRelationship]
    important_interview_knowledge: List[str]
    candidate_specific_knowledge_focus: List[str]
