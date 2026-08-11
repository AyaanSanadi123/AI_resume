import json
import os
from pathlib import Path
import sys

# Add root directory to path to allow import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from adaptive_interview.api.interview import generate_adaptive_interview

def test_pipeline_execution():
    fixtures_dir = Path(__file__).parent / "fixtures"
    
    with open(fixtures_dir / "sample_resume.json", "r") as f:
        candidate_data = json.load(f)
        
    with open(fixtures_dir / "sample_role.json", "r") as f:
        role_data = json.load(f)
        
    with open(fixtures_dir / "sample_semantic_match.json", "r") as f:
        semantic_data = json.load(f)
        
    with open(fixtures_dir / "sample_llm_advisor.json", "r") as f:
        llm_advisor = json.load(f)
        
    if not os.getenv("GEMINI_API_KEY"):
        print("Skipping full pipeline execution: GEMINI_API_KEY not found.")
        return
        
    print("Running full pipeline with 20 questions...")
    q_bank = generate_adaptive_interview(
        candidate_data=candidate_data,
        target_role=role_data.get("target_role"),
        total_questions=20,
        job_description=role_data.get("job_description"),
        matched_skills=semantic_data.get("matched_skills"),
        missing_skills=semantic_data.get("missing_skills"),
        llm_advisor=llm_advisor
    )
    
    assert "questions" in q_bank
    assert len(q_bank["questions"]) == 20
    
    output_dir = Path(__file__).parent.parent / "test_outputs"
    output_dir.mkdir(exist_ok=True)
    with open(output_dir / "full_pipeline_output.json", "w") as f:
        json.dump(q_bank, f, indent=2)
        
    print(f"Pipeline executed successfully. output written to {output_dir / 'full_pipeline_output.json'}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    test_pipeline_execution()
