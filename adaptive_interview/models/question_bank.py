from pydantic import BaseModel, model_validator
from typing import List, Optional
from .category_priority import Category
from .difficulty_profile import Difficulty

class InterviewQuestion(BaseModel):
    id: int
    category: Category
    difficulty: Difficulty
    topic: str
    intent: str
    question: str
    follow_up: Optional[str] = None

class QuestionBank(BaseModel):
    questions: List[InterviewQuestion]

    @model_validator(mode='after')
    def validate_questions(self):
        ids = [q.id for q in self.questions]
        expected_ids = list(range(1, len(self.questions) + 1))
        
        if len(ids) != len(set(ids)):
            raise ValueError("Question IDs must be unique")
            
        if sorted(ids) != expected_ids:
            raise ValueError("Question IDs must be sequential starting from 1")
            
        return self
