import os
import json
from DSE.ResumeAuditor import ResumeAuditor
from .ResumeRewriter import ResumeRewriter
from .PDFCompiler import PDFCompiler

def run_master_pipeline():
    print("==================================================")
    print("🚀 INITIATING SMART RESUME AI PIPELINE 🚀")
    print("==================================================")

    # 1. File Setup
    parsed_json_file = "ATS/resume1_parsed.json"
    sections_json_file = "DSE/resume1_sections.json"
    output_pdf_file = "SmartResume/Final_AI_Optimized_Resume.pdf"
    
    if not os.path.exists(parsed_json_file) or not os.path.exists(sections_json_file):
        print("❌ Error: Missing input JSON data files.")
        return

    # Load data
    with open(parsed_json_file, "r", encoding="utf-8") as f:
        parsed_data = json.load(f)
    with open(sections_json_file, "r", encoding="utf-8") as f:
        sections_data = json.load(f)

    # ---------------------------------------------------------
    # PHASE 1: DIAGNOSTIC SCORING ENGINE (DSE)
    # ---------------------------------------------------------
    print("\n--- PHASE 1: THE AUDIT ---")
    auditor = ResumeAuditor()
    print("⏳ Running math checks and semantic evaluation...")
    scorecard = auditor.audit_resume(parsed_data, sections_data)
    
    if "error" in scorecard:
        print(f"❌ Auditor failed: {scorecard['error']}")
        return
        
    print(f"✅ Audit Complete! Verdict: {scorecard.get('executive_verdict', '')[:100]}...")

    # ---------------------------------------------------------
    # PHASE 2: AI REWRITER (Prompt Chained with Scorecard)
    # ---------------------------------------------------------
    print("\n--- PHASE 2: THE REWRITE ---")
    rewriter = ResumeRewriter()
    print("⏳ Rewriting bullets based on Auditor feedback...")
    enhanced_resume_data = rewriter.rewrite_resume(parsed_resume_json=parsed_data, scorecard_json=scorecard)
    
    if "error" in enhanced_resume_data:
        print(f"❌ Rewriter failed: {enhanced_resume_data['error']}")
        return
        
    print("✅ Rewrite Complete! Missing skills injected and targeted brackets added.")
    
    # Save the output to disk so you can inspect the JSON changes
    with open("DSE/enhanced_resume_chain_test.json", "w", encoding="utf-8") as f:
        json.dump(enhanced_resume_data, f, indent=2)

    # ---------------------------------------------------------
    # PHASE 3: COMPILATION
    # ---------------------------------------------------------
    print("\n--- PHASE 3: PDF GENERATION ---")
    compiler = PDFCompiler(template_dir="SmartResume") # Adjust to "SmartResume" if your template is there
    print(f"⏳ Merging into Jinja2 template and compiling PDF...")
    
    pdf_binary = compiler.generate_pdf(
        enhanced_resume_data=enhanced_resume_data, 
        output_filepath=output_pdf_file
    )
    
    if pdf_binary:
        print("\n🎉 SUCCESS! PIPELINE EXECUTED FLAWLESSLY.")
        print(f"📄 Your highly targeted, optimized PDF is saved to: '{output_pdf_file}'")
    else:
        print("❌ PDF compilation failed.")

if __name__ == "__main__":
    run_master_pipeline()