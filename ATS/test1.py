import json
import os
from SemanticMatcher import SemanticMatcher

def run_evaluation_tests():
    # 1. Load the parsed candidate resume
    resume_file = "resume1_parsed.json"
    if not os.path.exists(resume_file):
        print(f"❌ Error: '{resume_file}' not found.")
        return

    with open(resume_file, "r", encoding="utf-8") as f:
        ayaan_resume = json.load(f)

    # 2. Initialize the Matching Engine (Loads DB and Model)
    print("Initializing Semantic Matcher...\n")
    matcher = SemanticMatcher(db_path="jobs_database.json")

    # 3. Target roles from the database to test against
    test_roles = [
        "Sr Human Resource Generalist", 
        "Human Resources Manager"
    ]

    # 4. Execute the match loop
    for role in test_roles:
        print(f"Evaluating profile against: {role}...")
        
        result = matcher.calculate_match(ayaan_resume, role)
        
        if not result or "error" in result:
            print(f"❌ Role '{role}' not found in database.\n")
            print("-" * 50)
            continue
            
        print(f"✅ Match Score: {result['match_score']}%")
        print(f"   Matched Skills: {result['matched_skills']}")
        
        # Truncate missing skills for cleaner console output
        missing = result['missing_skills']
        display_missing = missing[:5]
        if len(missing) > 5:
            display_missing.append(f"... (+{len(missing) - 5} more)")
            
        print(f"   Missing Skills: {display_missing}")
        print("-" * 50)

if __name__ == "__main__":
    run_evaluation_tests()