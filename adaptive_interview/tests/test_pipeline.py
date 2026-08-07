import sys
import os
import json

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from adaptive_interview.api.interview import generate_interview_questions

def test_pipeline():
    sample_ats_json = {
        "candidate_name": "Medora Gomes",
        "role": "AI/ML Intern",
        "ats_score": 74,
        "experience_level": "Student",
        "skills_found": [
            "Python",
            "TensorFlow",
            "SQL",
            "Git"
        ],
        "missing_skills": [
            "Docker",
            "PyTorch",
            "REST APIs"
        ],
        "weak_sections": [
            "Projects",
            "Achievements"
        ],
        "job_description": "We are looking for an AI/ML Intern to build models and deploy them.",
        "projects": [
            {
                "title": "PulmoX",
                "description": "AI Lung Cancer Detection"
            }
        ]
    }
    
    print("Running Adaptive Interview Pipeline Test...")
    try:
        result = generate_interview_questions(sample_ats_json)
        print("✅ Pipeline executed successfully!")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"❌ Pipeline failed: {str(e)}")

if __name__ == "__main__":
    test_pipeline()
