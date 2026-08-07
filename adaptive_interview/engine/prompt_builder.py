from typing import Dict, Any
from adaptive_interview.models.resume_profile import ResumeProfile
from adaptive_interview.models.role_profile import RoleProfile
from adaptive_interview.models.knowledge_graph import KnowledgeGraph
from adaptive_interview.models.interview_blueprint import InterviewBlueprint
from adaptive_interview.prompts.instructions import TECHNICAL_INSTRUCTIONS, BEHAVIORAL_INSTRUCTIONS

class PromptBuilder:
    """Constructs structured prompts for the LLM based on the deterministic blueprint."""
    
    @staticmethod
    def build(
        profile: ResumeProfile, 
        role: RoleProfile, 
        graph: KnowledgeGraph, 
        blueprint: InterviewBlueprint
    ) -> str:
        prompt = f"""You are an expert technical interviewer acting as an intelligent ATS Interview System.
Your task is to generate a personalized interview question bank for a candidate based on the provided interview blueprint.

--- CANDIDATE PROFILE ---
Role: {profile.role}
Experience Level: {profile.experience_level}
Projects: {[p.title for p in profile.projects]}

--- TARGET ROLE ---
Seniority: {role.seniority}
Domain: {role.domain}

--- KNOWLEDGE GRAPH FOCUS ---
Topics to Cover: {', '.join(graph.interview_focus_areas)}
Prerequisites to Verify: {', '.join(graph.concepts_requiring_prerequisite_verification)}
Areas for Deeper Questioning: {', '.join(graph.concepts_requiring_deeper_questioning)}

--- INTERVIEW BLUEPRINT (STRICT COMPLIANCE REQUIRED) ---
Target Difficulty: {blueprint.target_difficulty}
Total Questions: {blueprint.number_of_questions}
Category Distribution: {blueprint.category_distribution}
Topic Allocation: {blueprint.topic_allocation}
Difficulty Progression: {blueprint.difficulty_progression}

--- INSTRUCTIONS ---
{TECHNICAL_INSTRUCTIONS}

{BEHAVIORAL_INSTRUCTIONS}

Generate exactly {blueprint.number_of_questions} questions matching the difficulty progression sequence and category distribution.
Return JSON only matching the QuestionBank schema.
"""
        return prompt
