import json
import os
from SemanticMatcher import SemanticMatcher
from LLMAdvisor import LLMAdvisor

def run_evaluation_tests():
    # 0. Check if API key is present
    if not os.environ.get("GEMINI_API_KEY"):
        print("❌ Error: GEMINI_API_KEY environment variable is not set in this terminal.")
        print("👉 Run: export GEMINI_API_KEY='your_actual_api_key' first.")
        return

    # 1. Load the parsed candidate resume
    resume_file = "resume1_parsed.json"
    if not os.path.exists(resume_file):
        print(f"❌ Error: '{resume_file}' not found.")
        return

    with open(resume_file, "r", encoding="utf-8") as f:
        ayaan_resume = json.load(f)

    # 2. Initialize Engines
    print("🚀 Initializing Semantic Matcher...")
    matcher = SemanticMatcher(db_path="data/job_dataset.json")
    
    print("🤖 Initializing LLM Advisor...")
    advisor = LLMAdvisor()

    # 3. Target roles to test
    test_roles = [
        "AI Engineer - Fresher"
    ]

    # 4. Execute the match and advisory loop
    for role in test_roles:
        print(f"\n==================================================")
        print(f"🔍 Evaluating profile against: {role}...")
        print(f"==================================================")
        
        try:
            # Step A: Local Vector Math
            result = matcher.calculate_match(ayaan_resume, role)
            
            # Step B: Fetch the Raw Job Template Dictionary
            job_template = matcher._fetch_job_template(role)
            
        except ValueError as e:
            print(f"❌ {e}\n" + "-" * 50)
            continue
            
        print(f"✅ Vector Match Score: {result['match_score']}%")
        print(f"   Matched Skills: {result['matched_skills']}")
        print(f"   Missing Skills: {result['missing_skills'][:5]}")
        
        # Step C: Call the LLM Advisor explicitly and print progress
        print("\n⏳ Sending payload to Gemini 3.5 Flash... (Please wait a second)")
        
        advice = advisor.generate_advice(
            resume_json=ayaan_resume,
            job_json=job_template,
            match_results=result
        )
        
        print("\n--------------------------------------------------")
        print("💡 LLM RESPONSE RECEIVED:")
        print("--------------------------------------------------")
        print(json.dumps(advice, indent=2))
        print("--------------------------------------------------\n")

if __name__ == "__main__":
    run_evaluation_tests()