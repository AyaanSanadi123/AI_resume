from adaptive_interview.models.category_priority import Category
from adaptive_interview.models.difficulty_profile import Difficulty
from adaptive_interview.engine.blueprint_builder import BlueprintBuilder


def test_blueprint_builder():

    builder = BlueprintBuilder()

    category_allocations = {
        Category.TECHNICAL: 3,
        Category.PROJECTS: 2,
        Category.MISSING_SKILLS: 0,
        Category.BEHAVIORAL: 0,
        Category.TRAJECTORY: 0,
        Category.EXPERIENCE: 0,
    }

    difficulty_matrix = {
        Category.TECHNICAL: {
            Difficulty.EASY: 0,
            Difficulty.MEDIUM: 1,
            Difficulty.HARD: 2,
            Difficulty.EXPERT: 0,
        },

        Category.PROJECTS: {
            Difficulty.EASY: 1,
            Difficulty.MEDIUM: 1,
            Difficulty.HARD: 0,
            Difficulty.EXPERT: 0,
        },

        Category.MISSING_SKILLS: {
            Difficulty.EASY: 0,
            Difficulty.MEDIUM: 0,
            Difficulty.HARD: 0,
            Difficulty.EXPERT: 0,
        },

        Category.BEHAVIORAL: {
            Difficulty.EASY: 0,
            Difficulty.MEDIUM: 0,
            Difficulty.HARD: 0,
            Difficulty.EXPERT: 0,
        },

        Category.TRAJECTORY: {
            Difficulty.EASY: 0,
            Difficulty.MEDIUM: 0,
            Difficulty.HARD: 0,
            Difficulty.EXPERT: 0,
        },

        Category.EXPERIENCE: {
            Difficulty.EASY: 0,
            Difficulty.MEDIUM: 0,
            Difficulty.HARD: 0,
            Difficulty.EXPERT: 0,
        },
    }

    blueprint = builder.build(
        total_questions=5,
        category_allocations=category_allocations,
        difficulty_matrix=difficulty_matrix,
    )

    assert blueprint.total_questions == 5
    assert len(blueprint.question_slots) == 5

    technical_slots = [
        s
        for s in blueprint.question_slots
        if s.category == Category.TECHNICAL
    ]

    assert len(technical_slots) == 3

    hard_tech = [
        s
        for s in technical_slots
        if s.difficulty == Difficulty.HARD
    ]

    med_tech = [
        s
        for s in technical_slots
        if s.difficulty == Difficulty.MEDIUM
    ]

    assert len(hard_tech) == 2
    assert len(med_tech) == 1

    project_slots = [
        s
        for s in blueprint.question_slots
        if s.category == Category.PROJECTS
    ]

    assert len(project_slots) == 2

    easy_proj = [
        s
        for s in project_slots
        if s.difficulty == Difficulty.EASY
    ]

    med_proj = [
        s
        for s in project_slots
        if s.difficulty == Difficulty.MEDIUM
    ]

    assert len(easy_proj) == 1
    assert len(med_proj) == 1