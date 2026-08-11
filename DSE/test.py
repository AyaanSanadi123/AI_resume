import os
import json
from ResumeAuditor import ResumeAuditor

def run_auditor_test():
    # File paths based on your provided data
    parsed_json_file = "../ATS/resume1_parsed.json"
    sections_json_file = "resume1_sections.json"
    
    # 1. Verify files exist
    if not os.path.exists(parsed_json_file):
        print(f"❌ Error: Could not find '{parsed_json_file}'.")
        return
    if not os.path.exists(sections_json_file):
        print(f"❌ Error: Could not find '{sections_json_file}'.")
        return
        
    # 2. Load the data
    print(f"📂 Loading parsed resume from '{parsed_json_file}'...")
    with open(parsed_json_file, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)
        
    print(f"📂 Loading spatial extraction data from '{sections_json_file}'...")
    with open(sections_json_file, "r", encoding="utf-8") as f:
        sections_data = json.load(f)
        
    # 3. Initialize the Auditor
    print("\n🚀 Initializing Resume Auditor...")
    auditor = ResumeAuditor()
    
    # 4. Run the Audit
    print("⏳ Analyzing structure and querying Gemini for semantic audit... (This takes a few seconds)")
    scorecard = auditor.audit_resume(parsed_data, sections_data)
    
    # 5. Handle output
    if "error" in scorecard:
        print(f"\n❌ {scorecard['error']}")
    else:
        output_filename = "resume_scorecard_output.json"
        print(f"\n✅ Audit Complete! Saving full scorecard to '{output_filename}'...")
        
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(scorecard, f, indent=2)
            
        print("\n💡 Glimpse of the Executive Verdict:")
        print(f"   \"{scorecard.get('executive_verdict', 'No verdict found.')}\"")
        
        print("\n💡 Action Plan Breakdown:")
        action_plan = scorecard.get("action_plan", {})
        print(f"   - Needs Reformatting: {'🔴 YES' if action_plan.get('needs_reformatting') else '✅ NO'}")
        print(f"   - Needs Metric Injection: {'🔴 YES' if action_plan.get('needs_metric_injection') else '✅ NO'}")
        print(f"   - Needs Vocabulary Upgrade: {'🔴 YES' if action_plan.get('needs_vocabulary_upgrade') else '✅ NO'}")

if __name__ == "__main__":
    run_auditor_test()