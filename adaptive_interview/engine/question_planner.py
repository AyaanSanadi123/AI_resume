from typing import Dict, Any, List
from adaptive_interview.models.resume_profile import ResumeProfile
from adaptive_interview.models.ats_analysis import ATSAnalysis
from adaptive_interview.models.role_profile import RoleProfile
from adaptive_interview.models.knowledge_graph import KnowledgeGraph
from adaptive_interview.models.interview_signal import InterviewSignal
from adaptive_interview.models.interview_blueprint import InterviewBlueprint
from adaptive_interview.utils.difficulty import DifficultyEngine

class QuestionPlanner:
    """Deterministically plans the interview structure and topic allocation."""
    
    @staticmethod
    def plan(
        profile: ResumeProfile, 
        ats_analysis: ATSAnalysis, 
        role: RoleProfile, 
        signal: InterviewSignal,
        graph: KnowledgeGraph
    ) -> InterviewBlueprint:
        
        difficulty = DifficultyEngine.calculate(profile, ats_analysis, role, signal)
        
        # Base interview settings
        duration_minutes = 60
        number_of_questions = 10
        
        category_distribution = {
            "Technical Deep Dive": 4,
            "System/Architecture": 2,
            "Behavioral/Leadership": 2,
            "Project Experience": 2
        }
        
        # Topic allocation based on Knowledge Graph
        topic_allocation = {}
        for topic in graph.interview_focus_areas:
            topic_allocation[topic] = 1 # give 1 question per focus area initially
            
        # Prerequisite ordering
        prerequisite_ordering = graph.concepts_requiring_prerequisite_verification
        
        # Follow-up opportunities
        follow_up_opportunities = graph.concepts_requiring_deeper_questioning
        
        # Difficulty progression (Easy -> Target -> Target -> ... -> Harder)
        difficulty_progression = ["Medium"] * number_of_questions
        if difficulty == "Easy":
            difficulty_progression = ["Easy"] * number_of_questions
        elif difficulty == "Medium":
            difficulty_progression[0] = "Easy" # Start easy
            difficulty_progression[-1] = "Hard" # End hard
        elif difficulty == "Hard":
            difficulty_progression = ["Medium", "Medium", "Hard", "Hard", "Hard", "Hard", "Hard", "Hard", "Expert", "Expert"]
        elif difficulty == "Expert":
            difficulty_progression = ["Hard", "Hard", "Expert", "Expert", "Expert", "Expert", "Expert", "Expert", "Expert", "Expert"]
            
        # Adjust based on length
        difficulty_progression = difficulty_progression[:number_of_questions]
        while len(difficulty_progression) < number_of_questions:
            difficulty_progression.append(difficulty)
            
        return InterviewBlueprint(
            interview_duration_minutes=duration_minutes,
            number_of_questions=number_of_questions,
            category_distribution=category_distribution,
            topic_allocation=topic_allocation,
            prerequisite_ordering=prerequisite_ordering,
            follow_up_opportunities=follow_up_opportunities,
            difficulty_progression=difficulty_progression,
            target_difficulty=difficulty
        )
