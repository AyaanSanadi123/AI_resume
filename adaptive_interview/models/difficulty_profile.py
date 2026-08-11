from enum import Enum
from pydantic import BaseModel, Field, model_validator
from typing import Dict
import math

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

class DifficultyDistribution(BaseModel):
    easy: float = Field(..., ge=0.0, le=1.0)
    medium: float = Field(..., ge=0.0, le=1.0)
    hard: float = Field(..., ge=0.0, le=1.0)
    expert: float = Field(..., ge=0.0, le=1.0)

class CategoryDifficultyPreferences(BaseModel):
    technical: DifficultyDistribution
    projects: DifficultyDistribution
    missing_skills: DifficultyDistribution
    behavioral: DifficultyDistribution
    trajectory: DifficultyDistribution
    experience: DifficultyDistribution

class DifficultyAssessment(BaseModel):
    overall_level: Difficulty
    difficulty_profile: DifficultyDistribution
    category_difficulty_preferences: CategoryDifficultyPreferences
    rationale: str

    @model_validator(mode='after')
    def validate_probabilities(self):
        TOLERANCE = 1e-4
        
        prof_sum = self.difficulty_profile.easy + self.difficulty_profile.medium + self.difficulty_profile.hard + self.difficulty_profile.expert
        if not math.isclose(prof_sum, 1.0, abs_tol=TOLERANCE):
            raise ValueError(f"difficulty_profile probabilities must sum to 1.0, got {prof_sum}")
        
        # Convert to dict to iterate over fields
        prefs_dict = self.category_difficulty_preferences.model_dump()
        for cat, dist in prefs_dict.items():
            cat_sum = dist['easy'] + dist['medium'] + dist['hard'] + dist['expert']
            if not math.isclose(cat_sum, 1.0, abs_tol=TOLERANCE):
                raise ValueError(f"category_difficulty_preferences for {cat} must sum to 1.0, got {cat_sum}")
                
        return self
