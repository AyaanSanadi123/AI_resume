from typing import List, Dict, Any
from pydantic import BaseModel, Field

class InterviewBlueprint(BaseModel):
    interview_duration_minutes: int
    number_of_questions: int
    category_distribution: Dict[str, int] = Field(default_factory=dict)
    topic_allocation: Dict[str, int] = Field(default_factory=dict)
    prerequisite_ordering: List[str] = Field(default_factory=list)
    follow_up_opportunities: List[str] = Field(default_factory=list)
    difficulty_progression: List[str] = Field(default_factory=list)
    target_difficulty: str
