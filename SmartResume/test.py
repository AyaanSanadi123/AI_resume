import os
import json
from ResumeRewriter import ResumeRewriter
from PDFCompiler import PDFCompiler

def run_full_pipeline_test():
    # 1. Configuration & File Paths
    input_resume_file = "../ATS/resume1_parsed.json"  
    output_pdf_file = "Final_Optimized_Resume.pdf"
    
    if not os.path.exists(input_resume_file):
        print(f"❌ Error: Could not find input file '{input_resume_file}'.")
        return

    # 2. Load Raw Parsed Resume JSON
    print(f"📂 Loading raw resume data from '{input_resume_file}'...")
    with open(input_resume_file, "r", encoding="utf-8") as f:
        raw_resume_data = json.load(f)

    # 3. Step 2 Execution: LLM Auto-Rewriter
    print("\n--------------------------------------------------")
    print("🚀 PHASE 1: Running LLM Auto-Rewriter...")
    print("--------------------------------------------------")
    
    rewriter = ResumeRewriter()
    enhanced_resume_data = rewriter.rewrite_resume(raw_resume_data)
    
    if "error" in enhanced_resume_data:
        print(f"❌ Rewriter failed: {enhanced_resume_data['error']}")
        return
    
    print("✅ Resume content successfully enhanced by Gemini!")
    
    # Optional: Save intermediate enhanced json for inspection
    with open("enhanced_resume_test_output.json", "w", encoding="utf-8") as f:
        json.dump(enhanced_resume_data, f, indent=2)

    # 4. Step 3 & 4 Execution: Jinja2 + WeasyPrint Compiler
    print("\n--------------------------------------------------")
    print("🚀 PHASE 2: Compiling to ATS-Optimized PDF...")
    print("--------------------------------------------------")
    
    # Ensure template directory matches your class initialization ("SmartResume")
    compiler = PDFCompiler(template_dir="SmartResume")
    
    print(f"⏳ Merging enhanced JSON into Jinja2 template and rendering PDF...")
    pdf_binary = compiler.generate_pdf(
        enhanced_resume_data=enhanced_resume_data, 
        output_filepath=output_pdf_file
    )
    
    if pdf_binary:
        print(f"\n🎉 SUCCESS! Pipeline complete.")
        print(f"📄 Your optimized PDF is safely compiled and saved to: '{output_pdf_file}'")
    else:
        print("❌ PDF compilation failed.")

if __name__ == "__main__":
    run_full_pipeline_test()