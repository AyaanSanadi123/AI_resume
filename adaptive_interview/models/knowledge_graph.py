from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class ConceptNode(BaseModel):
    name: str
    prerequisite_concepts: List[str] = Field(default_factory=list)
    dependent_concepts: List[str] = Field(default_factory=list)
    related_technologies: List[str] = Field(default_factory=list)
    expected_interview_depth: str
    expected_competency_level: str
    logical_follow_up_topics: List[str] = Field(default_factory=list)

class KnowledgeGraph(BaseModel):
    engineering_domain: str
    specialization: str
    technologies_demonstrated: List[str] = Field(default_factory=list)
    technologies_required: List[str] = Field(default_factory=list)
    missing_technologies: List[str] = Field(default_factory=list)
    inferred_concepts: List[str] = Field(default_factory=list)
    prerequisite_concepts: List[str] = Field(default_factory=list)
    related_concepts: List[str] = Field(default_factory=list)
    dependent_concepts: List[str] = Field(default_factory=list)
    advanced_concepts: List[str] = Field(default_factory=list)
    project_domains: List[str] = Field(default_factory=list)
    architecture_patterns: List[str] = Field(default_factory=list)
    deployment_concepts: List[str] = Field(default_factory=list)
    interview_focus_areas: List[str] = Field(default_factory=list)
    concepts_requiring_prerequisite_verification: List[str] = Field(default_factory=list)
    concepts_requiring_deeper_questioning: List[str] = Field(default_factory=list)
    concept_nodes: Dict[str, ConceptNode] = Field(default_factory=dict)
