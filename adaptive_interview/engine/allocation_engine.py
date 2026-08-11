from typing import Dict, Any, List
import math
from ..models.category_priority import PriorityAnalysis, Category
from ..models.difficulty_profile import DifficultyAssessment, Difficulty

def allocate_categories(
    category_priorities: PriorityAnalysis,
    total_questions: int,
    constraints: Dict[str, Any]
) -> Dict[Category, int]:
    if total_questions <= 0:
        raise ValueError("total_questions must be a positive integer.")
    
    min_q = constraints.get("minimum_questions_when_relevant", 1)
    max_frac = constraints.get("maximum_category_fraction", 0.60)
    
    relevant_cats = [p for p in category_priorities.category_priorities if p.priority > 0]
    
    if total_questions < len(relevant_cats) * min_q:
        raise ValueError(
            f"allocation feasibility error: total_questions ({total_questions}) is smaller than "
            f"the number of relevant categories ({len(relevant_cats)}) multiplied by minimum_questions_when_relevant ({min_q})."
        )
    
    if not relevant_cats:
        return {cat: 0 for cat in Category}
    
    total_priority = sum(p.priority for p in relevant_cats)
    allocations = {c: 0 for c in Category}
    
    for p in relevant_cats:
        allocations[p.category] = min_q
    
    remaining_questions = total_questions - (len(relevant_cats) * min_q)
    targets = {p.category: (p.priority / total_priority) * remaining_questions for p in relevant_cats}
    
    while remaining_questions > 0:
        sorted_cats = sorted(targets.items(), key=lambda x: x[1], reverse=True)
        assigned = False
        for cat, target_val in sorted_cats:
            current_frac = (allocations[cat] + 1) / total_questions
            if current_frac <= max_frac:
                allocations[cat] += 1
                targets[cat] -= 1
                remaining_questions -= 1
                assigned = True
                break
        
        if not assigned:
            best_cat = sorted_cats[0][0]
            allocations[best_cat] += 1
            targets[best_cat] -= 1
            remaining_questions -= 1

    return allocations

def allocate_difficulty_matrix(
    category_allocations: Dict[Category, int],
    difficulty_assessment: DifficultyAssessment
) -> Dict[Category, Dict[Difficulty, int]]:
    
    total_questions = sum(category_allocations.values())
    
    # 1. Validate global difficulty
    global_dist = difficulty_assessment.difficulty_profile
    global_sum = global_dist.easy + global_dist.medium + global_dist.hard + global_dist.expert
    if not math.isclose(global_sum, 1.0, abs_tol=1e-5):
        raise ValueError(f"Global difficulty profile must sum to 1.0, got {global_sum}")
        
    for val in [global_dist.easy, global_dist.medium, global_dist.hard, global_dist.expert]:
        if val < 0:
            raise ValueError("Global difficulty probabilities cannot be negative.")
            
    # 2. Calculate global integer column totals using largest remainder
    global_ideal = {
        Difficulty.EASY: total_questions * global_dist.easy,
        Difficulty.MEDIUM: total_questions * global_dist.medium,
        Difficulty.HARD: total_questions * global_dist.hard,
        Difficulty.EXPERT: total_questions * global_dist.expert,
    }
    
    global_targets = {
        Difficulty.EASY: int(global_ideal[Difficulty.EASY]),
        Difficulty.MEDIUM: int(global_ideal[Difficulty.MEDIUM]),
        Difficulty.HARD: int(global_ideal[Difficulty.HARD]),
        Difficulty.EXPERT: int(global_ideal[Difficulty.EXPERT]),
    }
    
    global_rem = total_questions - sum(global_targets.values())
    
    # Distribute the remainder
    remainders = {
        d: global_ideal[d] - global_targets[d] for d in Difficulty
    }
    # Sort by remainder (descending), break ties by enum order
    sorted_remainders = sorted(
        remainders.items(), 
        key=lambda x: (x[1], -list(Difficulty).index(x[0])), 
        reverse=True
    )
    
    for i in range(global_rem):
        global_targets[sorted_remainders[i][0]] += 1
        
    # 3. Calculate category ideals and validate preferences
    # Ensure all categories have a zeroed matrix by default
    matrix = {cat: {d: 0 for d in Difficulty} for cat in Category}
    
    ideal_cells = {}
    prefs_dict = difficulty_assessment.category_difficulty_preferences.model_dump()
    
    for cat, count in category_allocations.items():
        if count == 0:
            continue
            
        if cat.value not in prefs_dict:
            raise ValueError(f"Category {cat.value} has allocated questions but no difficulty preference.")
            
        pref = prefs_dict[cat.value]
        
        pref_sum = pref['easy'] + pref['medium'] + pref['hard'] + pref['expert']
        if not math.isclose(pref_sum, 1.0, abs_tol=1e-5):
            raise ValueError(f"Preference for {cat.value} must sum to 1.0, got {pref_sum}")
            
        for k, v in pref.items():
            if v < 0:
                raise ValueError(f"Preference for {cat.value} has negative value: {v}")
                
        ideal_cells[(cat, Difficulty.EASY)] = count * pref['easy']
        ideal_cells[(cat, Difficulty.MEDIUM)] = count * pref['medium']
        ideal_cells[(cat, Difficulty.HARD)] = count * pref['hard']
        ideal_cells[(cat, Difficulty.EXPERT)] = count * pref['expert']
        
    # 4. Track remaining targets
    row_remaining = {cat: count for cat, count in category_allocations.items() if count > 0}
    col_remaining = dict(global_targets)
    
    # Check feasibility
    if sum(row_remaining.values()) != sum(col_remaining.values()):
        raise ValueError("Sum of category allocations does not match sum of global difficulty targets.")
        
    # 5. Greedy allocation minimizing deficit
    # Deficit = ideal_cell - current_cell
    
    total_to_allocate = sum(row_remaining.values())
    for _ in range(total_to_allocate):
        best_cell = None
        best_score = float('-inf')
        
        # We iterate in deterministic order (Category then Difficulty)
        for cat in Category:
            if cat not in row_remaining or row_remaining[cat] == 0:
                continue
            for diff in Difficulty:
                if col_remaining[diff] == 0:
                    continue
                    
                deficit = ideal_cells[(cat, diff)] - matrix[cat][diff]
                
                # We want to maximize the positive deficit
                if deficit > best_score:
                    best_score = deficit
                    best_cell = (cat, diff)
                    
        if not best_cell:
            raise ValueError("Unable to allocate a valid cell meeting constraints.")
            
        alloc_cat, alloc_diff = best_cell
        matrix[alloc_cat][alloc_diff] += 1
        row_remaining[alloc_cat] -= 1
        col_remaining[alloc_diff] -= 1
        
    # 6. Final verification
    if sum(sum(d.values()) for d in matrix.values()) != total_questions:
        raise ValueError("Final matrix total does not match total_questions")
        
    for cat in Category:
        if sum(matrix[cat].values()) != category_allocations.get(cat, 0):
            raise ValueError(f"Row total for {cat} mismatch")
        for diff in Difficulty:
            val = matrix[cat][diff]
            if not isinstance(val, int) or val < 0:
                raise ValueError(f"Invalid cell value {val} at {cat}, {diff}")
                
    for diff in Difficulty:
        col_sum = sum(matrix[cat][diff] for cat in Category)
        if col_sum != global_targets[diff]:
            raise ValueError(f"Column total for {diff} mismatch")
            
    # Check shape
    for cat in category_allocations:
        if cat not in matrix or set(matrix[cat].keys()) != {Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD, Difficulty.EXPERT}:
            raise ValueError(f"Matrix shape invalid for category {cat}")
            
    return matrix
