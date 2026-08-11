from typing import Dict, Any
from ..models.category_priority import PriorityAnalysis, Category

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
