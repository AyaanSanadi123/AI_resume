from pydantic import BaseModel, model_validator
from typing import List, Dict
from .interview_slot import InterviewSlot
from .category_priority import Category
from .difficulty_profile import Difficulty

class InterviewBlueprint(BaseModel):
    total_questions: int
    category_allocations: Dict[Category, int]
    difficulty_allocations: Dict[Difficulty, int]
    question_slots: List[InterviewSlot]
    generation_notes: str

    @model_validator(mode='after')
    def validate_blueprint(self):
        if len(self.question_slots) != self.total_questions:
            raise ValueError(f"question_slots length ({len(self.question_slots)}) must match total_questions ({self.total_questions})")
            
        q_nums = [slot.question_number for slot in self.question_slots]
        if len(q_nums) != len(set(q_nums)):
            raise ValueError("question_number values must be unique")
            
        expected_nums = list(range(1, self.total_questions + 1))
        if sorted(q_nums) != expected_nums:
            raise ValueError("question_number values must be sequential starting from 1")
            
        # Validate counts
        actual_cat_counts = {cat: 0 for cat in Category}
        actual_diff_counts = {diff: 0 for diff in Difficulty}
        
        for slot in self.question_slots:
            actual_cat_counts[slot.category] += 1
            actual_diff_counts[slot.difficulty] += 1
            
        # Convert CategoryAllocations to dict
        cat_allocs = self.category_allocations.model_dump() if hasattr(self.category_allocations, 'model_dump') else self.category_allocations
        diff_allocs = self.difficulty_allocations.model_dump() if hasattr(self.difficulty_allocations, 'model_dump') else self.difficulty_allocations

        for cat_str, count in cat_allocs.items():
            cat = Category(cat_str) if isinstance(cat_str, str) else cat_str
            if actual_cat_counts.get(cat, 0) != count:
                raise ValueError(f"category count for {cat} mismatch: expected {count}, got {actual_cat_counts.get(cat, 0)}")
                
        for diff_str, count in diff_allocs.items():
            diff = Difficulty(diff_str) if isinstance(diff_str, str) else diff_str
            if actual_diff_counts.get(diff, 0) != count:
                raise ValueError(f"difficulty count for {diff} mismatch: expected {count}, got {actual_diff_counts.get(diff, 0)}")
                
        return self
