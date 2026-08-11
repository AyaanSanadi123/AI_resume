import json
from pathlib import Path
from typing import Optional, Dict, Any, List

from .models.upstream_candidate import UpstreamCandidate
from .services.gemini_client import GeminiClient

from .engine.knowledge_discovery import KnowledgeDiscoveryEngine
from .engine.priority_analyzer import PriorityAnalyzerEngine
from .engine.difficulty_assessor import DifficultyAssessorEngine
# from .engine.allocation_engine import allocate_categories
from .engine.allocation_engine import (
    allocate_categories,
    allocate_difficulty_matrix,
)
from .engine.blueprint_builder import BlueprintBuilder
from .engine.question_generator import QuestionGeneratorEngine
from .models.question_bank import QuestionBank

class AdaptiveInterviewPipeline:
    def __init__(self, constraints_path: Optional[str] = None):
        self.client = GeminiClient()
        self.knowledge_discovery = KnowledgeDiscoveryEngine(self.client)
        self.priority_analyzer = PriorityAnalyzerEngine(self.client)
        self.difficulty_assessor = DifficultyAssessorEngine(self.client)
        self.blueprint_builder = BlueprintBuilder()
        self.question_generator = QuestionGeneratorEngine(self.client)
        
        if not constraints_path:
            constraints_path = Path(__file__).parent / "config" / "interview_constraints.json"
        
        with open(constraints_path, "r", encoding="utf-8") as f:
            self.constraints = json.load(f).get("allocation_constraints", {})
            
    def run(
        self,
        candidate_data: Dict[str, Any],
        target_role: str,
        total_questions: int,
        job_description: Optional[str] = None,
        matched_skills: List[str] = None,
        missing_skills: List[str] = None,
        llm_advisor: Dict[str, Any] = None
    ) -> QuestionBank:
        
        matched_skills = matched_skills or []
        missing_skills = missing_skills or []
        llm_advisor = llm_advisor or {}
        
        candidate = UpstreamCandidate.model_validate(candidate_data)
        
        knowledge_summary = self.knowledge_discovery.generate(
            candidate=candidate,
            target_role=target_role,
            job_description=job_description,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            llm_advisor=llm_advisor
        )
        
        priority_analysis = self.priority_analyzer.generate(
            candidate=candidate,
            target_role=target_role,
            job_description=job_description,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            llm_advisor=llm_advisor,
            knowledge_summary=knowledge_summary
        )
        
        difficulty_assessment = self.difficulty_assessor.generate(
            candidate=candidate,
            target_role=target_role,
            job_description=job_description,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            llm_advisor=llm_advisor,
            knowledge_summary=knowledge_summary
        )
        
        category_allocations = allocate_categories(
            category_priorities=priority_analysis,
            total_questions=total_questions,
            constraints=self.constraints
        )
        
        # interview_blueprint = self.blueprint_builder.build(
        #     total_questions=total_questions,
        #     category_allocations=category_allocations,
        #     difficulty_assessment=difficulty_assessment
        # )
        difficulty_matrix = allocate_difficulty_matrix(
            category_allocations=category_allocations,
            difficulty_assessment=difficulty_assessment,
        )

        interview_blueprint = self.blueprint_builder.build(
            total_questions=total_questions,
            category_allocations=category_allocations,
            difficulty_matrix=difficulty_matrix,
        )
        
        question_bank = self.question_generator.generate(
            candidate=candidate,
            target_role=target_role,
            job_description=job_description,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            llm_advisor=llm_advisor,
            knowledge_summary=knowledge_summary,
            interview_blueprint=interview_blueprint
        )
        
        return question_bank
