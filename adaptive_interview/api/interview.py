from typing import Optional, Dict, Any, List
from ..interview_pipeline import AdaptiveInterviewPipeline

def generate_adaptive_interview(
    candidate_data: Dict[str, Any],
    target_role: str,
    total_questions: int,
    job_description: Optional[str] = None,
    matched_skills: List[str] = None,
    missing_skills: List[str] = None,
    llm_advisor: Dict[str, Any] = None
) -> Dict[str, Any]:
    pipeline = AdaptiveInterviewPipeline()
    q_bank = pipeline.run(
        candidate_data=candidate_data,
        target_role=target_role,
        total_questions=total_questions,
        job_description=job_description,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        llm_advisor=llm_advisor
    )
    return q_bank.model_dump()
