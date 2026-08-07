from typing import List, Optional
from pydantic import BaseModel, Field

class InterviewQuestion(BaseModel):
    id: int
    category: str
    difficulty: str
    skill: Optional[str] = None
    question: str
    expected_answer: List[str]
    keywords: List[str]
    evaluation_rubric: List[str]
    follow_up_questions: List[str] = Field(default_factory=list)
    time_limit: int
    confidence_weight: float

class QuestionBank(BaseModel):
    questions: List[InterviewQuestion]
