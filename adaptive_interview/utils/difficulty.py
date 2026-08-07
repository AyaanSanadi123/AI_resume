from adaptive_interview.models.ats_analysis import ATSAnalysis
from adaptive_interview.models.resume_profile import ResumeProfile
from adaptive_interview.models.role_profile import RoleProfile
from adaptive_interview.models.interview_signal import InterviewSignal

class DifficultyEngine:
    """Dynamically adapts interview difficulty based on a weighted scoring engine."""
    
    @staticmethod
    def calculate(profile: ResumeProfile, ats_analysis: ATSAnalysis, role: RoleProfile, signal: InterviewSignal) -> str:
        score = 0.0
        
        # 1. ATS Score Weight (0 to 100) -> max 30 points
        score += (ats_analysis.ats_score / 100.0) * 30
        
        # 2. Experience Years (heuristics from experience_level or signal) -> max 20 points
        exp_level = profile.experience_level.lower()
        if "senior" in exp_level or "lead" in exp_level or "staff" in exp_level or "principal" in exp_level:
            score += 20
        elif "mid" in exp_level or "intermediate" in exp_level:
            score += 12
        elif "junior" in exp_level or "entry" in exp_level:
            score += 5
        else:
            score += 5 # default
            
        # 3. Role Seniority -> max 10 points
        role_seniority = role.seniority.lower()
        if "senior" in role_seniority or "lead" in role_seniority or "staff" in role_seniority or "principal" in role_seniority:
            score += 10
        elif "mid" in role_seniority:
            score += 5
        else:
            score += 2
            
        # 4. Project Complexity & Diversity -> max 20 points
        complexity = signal.project_complexity.lower()
        if "high" in complexity or "advanced" in complexity or "complex" in complexity:
            score += 10
        elif "medium" in complexity or "moderate" in complexity:
            score += 5
        
        diversity = signal.project_diversity.lower()
        if "high" in diversity or "diverse" in diversity:
            score += 10
        elif "medium" in diversity or "moderate" in diversity:
            score += 5
            
        # 5. Technical Breadth -> max 10 points
        breadth = signal.technical_breadth.lower()
        if "broad" in breadth or "high" in breadth or "extensive" in breadth:
            score += 10
        elif "medium" in breadth or "moderate" in breadth:
            score += 5
            
        # 6. Education & Certifications -> max 10 points
        edu = signal.education_and_certification_coverage.lower()
        if "strong" in edu or "comprehensive" in edu or "high" in edu:
            score += 10
        elif "adequate" in edu or "moderate" in edu or "medium" in edu:
            score += 5
            
        # Total possible: 100 points
        if score >= 80:
            return "Expert"
        elif score >= 60:
            return "Hard"
        elif score >= 40:
            return "Medium"
        else:
            return "Easy"
