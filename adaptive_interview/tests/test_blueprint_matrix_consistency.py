from adaptive_interview.models.category_priority import Category
from adaptive_interview.models.difficulty_profile import Difficulty
from adaptive_interview.engine.blueprint_builder import BlueprintBuilder


def test_blueprint_preserves_category_difficulty_matrix():
    """
    Verify that BlueprintBuilder converts an already-computed
    category × difficulty matrix into exactly the expected
    InterviewBlueprint slots.

    Matrix:

                         easy   medium   hard   expert
        technical          1       3       2       0
        projects           1       2       1       0

    Total questions = 10
    """

    category_allocations = {
        Category.TECHNICAL: 6,
        Category.PROJECTS: 4,
        Category.MISSING_SKILLS: 0,
        Category.BEHAVIORAL: 0,
        Category.TRAJECTORY: 0,
        Category.EXPERIENCE: 0,
    }

    difficulty_matrix = {
        Category.TECHNICAL: {
            Difficulty.EASY: 1,
            Difficulty.MEDIUM: 3,
            Difficulty.HARD: 2,
            Difficulty.EXPERT: 0,
        },

        Category.PROJECTS: {
            Difficulty.EASY: 1,
            Difficulty.MEDIUM: 2,
            Difficulty.HARD: 1,
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

    builder = BlueprintBuilder()

    blueprint = builder.build(
        total_questions=10,
        category_allocations=category_allocations,
        difficulty_matrix=difficulty_matrix,
    )

    # ---------------------------------------------------------
    # TOTAL QUESTIONS
    # ---------------------------------------------------------

    assert blueprint.total_questions == 10
    assert len(blueprint.question_slots) == 10

    # ---------------------------------------------------------
    # COUNT ACTUAL BLUEPRINT SLOTS
    # ---------------------------------------------------------

    actual_matrix = {
        category: {
            difficulty: 0
            for difficulty in Difficulty
        }
        for category in Category
    }

    for slot in blueprint.question_slots:
        actual_matrix[slot.category][slot.difficulty] += 1

    # ---------------------------------------------------------
    # MATRIX MUST MATCH EXACTLY
    # ---------------------------------------------------------

    for category in Category:
        for difficulty in Difficulty:

            expected = difficulty_matrix[category][difficulty]
            actual = actual_matrix[category][difficulty]

            assert actual == expected, (
                f"Mismatch for "
                f"{category.value}/{difficulty.value}: "
                f"expected {expected}, got {actual}"
            )

    # ---------------------------------------------------------
    # CATEGORY TOTALS
    # ---------------------------------------------------------

    for category in Category:

        expected_category_count = category_allocations[category]

        actual_category_count = sum(
            actual_matrix[category].values()
        )

        assert actual_category_count == expected_category_count

    # ---------------------------------------------------------
    # DIFFICULTY TOTALS
    # ---------------------------------------------------------

    assert sum(
        actual_matrix[category][Difficulty.EASY]
        for category in Category
    ) == 2

    assert sum(
        actual_matrix[category][Difficulty.MEDIUM]
        for category in Category
    ) == 5

    assert sum(
        actual_matrix[category][Difficulty.HARD]
        for category in Category
    ) == 3

    assert sum(
        actual_matrix[category][Difficulty.EXPERT]
        for category in Category
    ) == 0

    # ---------------------------------------------------------
    # QUESTION NUMBERS
    # ---------------------------------------------------------

    question_numbers = [
        slot.question_number
        for slot in blueprint.question_slots
    ]

    assert question_numbers == list(range(1, 11))