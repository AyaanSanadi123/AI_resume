from pydantic import BaseModel
from typing import List
from .category_priority import Category
from .difficulty_profile import Difficulty

class InterviewSlot(BaseModel):
    question_number: int
    category: Category
    difficulty: Difficulty
    allowed_context: List[str]
    follow_up_allowed: bool
