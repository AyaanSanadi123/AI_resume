from typing import Dict, Any
from adaptive_interview.models.resume_profile import ResumeProfile, Project
from adaptive_interview.adapters.ats_adapter import TemporaryATSProvider
from adaptive_interview.engine.role_understanding import RoleUnderstandingEngine
from adaptive_interview.engine.resume_intelligence import ResumeIntelligenceEngine
from adaptive_interview.engine.knowledge_discovery import KnowledgeDiscoveryEngine
from adaptive_interview.engine.question_planner import QuestionPlanner
from adaptive_interview.engine.prompt_builder import PromptBuilder
from adaptive_interview.engine.interview_generator import InterviewGenerator

def generate_interview_questions(resume_data: Dict[str, Any], job_description: str) -> Dict[str, Any]:
    """
    Main entry point for the Adaptive Interview Generation Module.
    Consumes Resume Parser output and Job Description, and orchestrates the interview generation pipeline.
    """
    
    # 1. Convert raw resume data to ResumeProfile model
    projects = []
    for p in resume_data.get("projects", []):
        projects.append(Project(title=p.get("title", ""), description=p.get("description", "")))
        
    profile = ResumeProfile(
        candidate_name=resume_data.get("candidate_name", "Candidate"),
        role=resume_data.get("role", "General"),
        experience_level=resume_data.get("experience_level", "Unknown"),
        skills_found=resume_data.get("skills_found", []),
        job_description=job_description,
        projects=projects
    )
    
    # 2. Temporary ATS Adapter
    ats_provider = TemporaryATSProvider()
    ats_analysis = ats_provider.generate_ats_analysis(profile, job_description)
    
    # 3. Role Understanding
    role_engine = RoleUnderstandingEngine()
    role_profile = role_engine.analyze(job_description)
    
    # 4. Resume Intelligence Engine
    resume_engine = ResumeIntelligenceEngine()
    interview_signals = resume_engine.analyze(profile, ats_analysis)
    
    # 5. Knowledge Discovery
    knowledge_engine = KnowledgeDiscoveryEngine()
    knowledge_graph = knowledge_engine.discover(profile, ats_analysis, role_profile)
    
    # 6. Deterministic Interview Planner
    planner = QuestionPlanner()
    blueprint = planner.plan(profile, ats_analysis, role_profile, interview_signals, knowledge_graph)
    
    # 7. Prompt Builder
    prompt = PromptBuilder.build(profile, role_profile, knowledge_graph, blueprint)
    
    # 8. Generation
    generator = InterviewGenerator()
    question_bank = generator.generate(prompt)
    
    return question_bank.model_dump()
