import pytest
from adaptive_interview.models.category_priority import PriorityAnalysis, CategoryPriority, Category
from adaptive_interview.engine.allocation_engine import allocate_categories

def test_allocation_engine_basic():
    priorities = PriorityAnalysis(
        category_priorities=[
            CategoryPriority(category=Category.TECHNICAL, priority=1.0, rationale=""),
            CategoryPriority(category=Category.PROJECTS, priority=0.5, rationale=""),
            CategoryPriority(category=Category.MISSING_SKILLS, priority=0.0, rationale="")
        ]
    )
    
    constraints = {
        "minimum_questions_when_relevant": 1,
        "maximum_category_fraction": 0.60
    }
    
    allocations = allocate_categories(priorities, 10, constraints)
    
    assert allocations[Category.MISSING_SKILLS] == 0
    assert sum(allocations.values()) == 10
    
    assert allocations[Category.TECHNICAL] == 6
    assert allocations[Category.PROJECTS] == 4

def test_allocation_feasibility_error():
    priorities = PriorityAnalysis(
        category_priorities=[
            CategoryPriority(category=Category.TECHNICAL, priority=1.0, rationale="")
        ]
    )
    
    constraints = {
        "minimum_questions_when_relevant": 2,
        "maximum_category_fraction": 0.60
    }
    
    with pytest.raises(ValueError, match="allocation feasibility error"):
        allocate_categories(priorities, 1, constraints)
