from adaptive_interview.models.category_priority import Category
from adaptive_interview.models.difficulty_profile import DifficultyAssessment, DifficultyDistribution, Difficulty
from adaptive_interview.engine.blueprint_builder import BlueprintBuilder

def test_blueprint_builder():
    builder = BlueprintBuilder()
    
    category_allocations = {
        Category.TECHNICAL: 3,
        Category.PROJECTS: 2,
        Category.MISSING_SKILLS: 0,
        Category.BEHAVIORAL: 0,
        Category.TRAJECTORY: 0,
        Category.EXPERIENCE: 0
    }
    
    assessment = DifficultyAssessment(
        overall_level=Difficulty.MEDIUM,
        difficulty_profile=DifficultyDistribution(easy=0.2, medium=0.6, hard=0.2, expert=0.0),
        category_difficulty_preferences={
            "technical": DifficultyDistribution(easy=0.0, medium=0.3333, hard=0.6667, expert=0.0),
            "projects": DifficultyDistribution(easy=0.5, medium=0.5, hard=0.0, expert=0.0)
        },
        rationale=""
    )
    
    blueprint = builder.build(5, category_allocations, assessment)
    
    assert blueprint.total_questions == 5
    assert len(blueprint.question_slots) == 5
    
    technical_slots = [s for s in blueprint.question_slots if s.category == Category.TECHNICAL]
    assert len(technical_slots) == 3
    
    hard_tech = [s for s in technical_slots if s.difficulty == Difficulty.HARD]
    med_tech = [s for s in technical_slots if s.difficulty == Difficulty.MEDIUM]
    
    assert len(hard_tech) == 2
    assert len(med_tech) == 1
    
    project_slots = [s for s in blueprint.question_slots if s.category == Category.PROJECTS]
    assert len(project_slots) == 2
    
    easy_proj = [s for s in project_slots if s.difficulty == Difficulty.EASY]
    med_proj = [s for s in project_slots if s.difficulty == Difficulty.MEDIUM]
    
    assert len(easy_proj) == 1
    assert len(med_proj) == 1
