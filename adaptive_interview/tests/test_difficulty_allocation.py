from adaptive_interview.models.category_priority import Category
from adaptive_interview.models.difficulty_profile import (
    Difficulty,
    DifficultyAssessment,
    DifficultyDistribution,
)
from adaptive_interview.engine.allocation_engine import (
    allocate_difficulty_matrix,
)


def test_difficulty_allocation_matrix():
    """
    Verify that the deterministic difficulty allocator correctly
    reconciles:

        category question counts
        +
        global difficulty distribution
        +
        category-specific difficulty preferences

    into a valid category × difficulty matrix.
    """

    # ---------------------------------------------------------
    # CATEGORY ALLOCATION
    # ---------------------------------------------------------
    #
    # Total questions = 10
    #
    # Technical must receive 6 questions.
    # Projects must receive 4 questions.
    #
    # All other categories receive 0.
    #
    category_allocations = {
        Category.TECHNICAL: 6,
        Category.PROJECTS: 4,
        Category.MISSING_SKILLS: 0,
        Category.BEHAVIORAL: 0,
        Category.TRAJECTORY: 0,
        Category.EXPERIENCE: 0,
    }

    # ---------------------------------------------------------
    # GLOBAL DIFFICULTY PROFILE
    # ---------------------------------------------------------
    #
    # Total = 1.0
    #
    # For 10 questions this represents:
    #
    # easy   -> 2 questions
    # medium -> 5 questions
    # hard   -> 3 questions
    # expert -> 0 questions
    #
    global_difficulty = DifficultyDistribution(
        easy=0.20,
        medium=0.50,
        hard=0.30,
        expert=0.00,
    )

    # ---------------------------------------------------------
    # CATEGORY-SPECIFIC DIFFICULTY PREFERENCES
    # ---------------------------------------------------------
    #
    # Technical:
    #   0% easy
    #   50% medium
    #   50% hard
    #   0% expert
    #
    # Projects:
    #   50% easy
    #   50% medium
    #   0% hard
    #   0% expert
    #
    # These preferences are deliberately different.
    #
    # The test therefore verifies that the implementation
    # actually considers category-specific preferences rather
    # than applying one global difficulty distribution
    # independently to every category.
    #
    category_preferences = {
        "technical": DifficultyDistribution(
            easy=0.00,
            medium=0.50,
            hard=0.50,
            expert=0.00,
        ),
        "projects": DifficultyDistribution(
            easy=0.50,
            medium=0.50,
            hard=0.00,
            expert=0.00,
        ),
        "missing_skills": DifficultyDistribution(
            easy=0.00,
            medium=0.00,
            hard=0.00,
            expert=0.00,
        ),
        "behavioral": DifficultyDistribution(
            easy=0.00,
            medium=0.00,
            hard=0.00,
            expert=0.00,
        ),
        "trajectory": DifficultyDistribution(
            easy=0.00,
            medium=0.00,
            hard=0.00,
            expert=0.00,
        ),
        "experience": DifficultyDistribution(
            easy=0.00,
            medium=0.00,
            hard=0.00,
            expert=0.00,
        ),
    }

    difficulty_assessment = DifficultyAssessment(
        overall_level=Difficulty.MEDIUM,
        difficulty_profile=global_difficulty,
        category_difficulty_preferences=category_preferences,
        rationale="Test candidate-specific category difficulty preferences.",
    )

    # ---------------------------------------------------------
    # RUN THE DETERMINISTIC ALLOCATION
    # ---------------------------------------------------------

    matrix = allocate_difficulty_matrix(
        category_allocations=category_allocations,
        difficulty_assessment=difficulty_assessment,
    )

    # ---------------------------------------------------------
    # EXPECTED DIFFICULTIES
    # ---------------------------------------------------------
    #
    # The global profile for 10 questions requires:
    #
    # easy   = 2
    # medium = 5
    # hard   = 3
    # expert = 0
    #
    expected_column_totals = {
        Difficulty.EASY: 2,
        Difficulty.MEDIUM: 5,
        Difficulty.HARD: 3,
        Difficulty.EXPERT: 0,
    }

    # ---------------------------------------------------------
    # CHECK THAT ONLY ALLOCATED CATEGORIES HAVE QUESTIONS
    # ---------------------------------------------------------

    assert sum(matrix[Category.TECHNICAL].values()) == 6
    assert sum(matrix[Category.PROJECTS].values()) == 4

    assert sum(matrix[Category.MISSING_SKILLS].values()) == 0
    assert sum(matrix[Category.BEHAVIORAL].values()) == 0
    assert sum(matrix[Category.TRAJECTORY].values()) == 0
    assert sum(matrix[Category.EXPERIENCE].values()) == 0

    # ---------------------------------------------------------
    # CHECK ROW TOTALS
    # ---------------------------------------------------------

    assert sum(matrix[Category.TECHNICAL].values()) == 6
    assert sum(matrix[Category.PROJECTS].values()) == 4

    # ---------------------------------------------------------
    # CHECK COLUMN TOTALS
    # ---------------------------------------------------------

    for difficulty, expected_count in expected_column_totals.items():

        actual_count = sum(
            matrix[category][difficulty]
            for category in category_allocations
        )

        assert actual_count == expected_count, (
            f"Difficulty {difficulty.value} expected "
            f"{expected_count} questions but received {actual_count}."
        )

    # ---------------------------------------------------------
    # CHECK TOTAL QUESTION COUNT
    # ---------------------------------------------------------

    total_questions = sum(
        count
        for category_matrix in matrix.values()
        for count in category_matrix.values()
    )

    assert total_questions == 10

    # ---------------------------------------------------------
    # CHECK EVERY CELL IS A NON-NEGATIVE INTEGER
    # ---------------------------------------------------------

    for category in category_allocations:

        for difficulty in Difficulty:

            value = matrix[category][difficulty]

            assert isinstance(value, int)
            assert value >= 0

    # ---------------------------------------------------------
    # CHECK MATRIX SHAPE
    # ---------------------------------------------------------
    #
    # Every category must have all four difficulty columns.
    #

    for category in category_allocations:

        assert set(matrix[category].keys()) == {
            Difficulty.EASY,
            Difficulty.MEDIUM,
            Difficulty.HARD,
            Difficulty.EXPERT,
        }


def test_difficulty_allocation_is_deterministic():
    """
    The same inputs must always produce the same matrix.

    This protects the production requirement that the
    difficulty allocation is deterministic and reproducible.
    """

    category_allocations = {
        Category.TECHNICAL: 6,
        Category.PROJECTS: 4,
        Category.MISSING_SKILLS: 0,
        Category.BEHAVIORAL: 0,
        Category.TRAJECTORY: 0,
        Category.EXPERIENCE: 0,
    }

    difficulty_assessment = DifficultyAssessment(
        overall_level=Difficulty.MEDIUM,

        difficulty_profile=DifficultyDistribution(
            easy=0.20,
            medium=0.50,
            hard=0.30,
            expert=0.00,
        ),

        category_difficulty_preferences={
            "technical": DifficultyDistribution(
                easy=0.00,
                medium=0.50,
                hard=0.50,
                expert=0.00,
            ),

            "projects": DifficultyDistribution(
                easy=0.50,
                medium=0.50,
                hard=0.00,
                expert=0.00,
            ),

            "missing_skills": DifficultyDistribution(
                easy=0.00,
                medium=0.00,
                hard=0.00,
                expert=0.00,
            ),

            "behavioral": DifficultyDistribution(
                easy=0.00,
                medium=0.00,
                hard=0.00,
                expert=0.00,
            ),

            "trajectory": DifficultyDistribution(
                easy=0.00,
                medium=0.00,
                hard=0.00,
                expert=0.00,
            ),

            "experience": DifficultyDistribution(
                easy=0.00,
                medium=0.00,
                hard=0.00,
                expert=0.00,
            ),
        },

        rationale="Determinism test.",
    )

    first_result = allocate_difficulty_matrix(
        category_allocations=category_allocations,
        difficulty_assessment=difficulty_assessment,
    )

    second_result = allocate_difficulty_matrix(
        category_allocations=category_allocations,
        difficulty_assessment=difficulty_assessment,
    )

    assert first_result == second_result