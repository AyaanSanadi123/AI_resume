from enum import Enum
from pydantic import BaseModel, Field
from typing import List

class Category(str, Enum):
    TECHNICAL = "technical"
    PROJECTS = "projects"
    MISSING_SKILLS = "missing_skills"
    BEHAVIORAL = "behavioral"
    TRAJECTORY = "trajectory"
    EXPERIENCE = "experience"

class CategoryPriority(BaseModel):
    category: Category
    priority: float = Field(..., ge=0.0, le=1.0)
    rationale: str

class PriorityAnalysis(BaseModel):
    category_priorities: List[CategoryPriority]
