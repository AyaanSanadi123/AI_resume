import os
import platform
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware


if platform.system() == "Windows":
    os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"
    os.environ["FLAGS_use_mkldnn"] = "0"
    try:
        os.add_dll_directory(r"D:\dependencies\msys2\ucrt64\bin")
    except Exception as e:
        print(f"⚠️ Warning: Could not add DLL directory: {e}")


from ATS.text_extraction import TextExtraction
from ATS.resume_parser import ResumeParser
from ATS.SemanticMatcher import SemanticMatcher
from ATS.LLMAdvisor import LLMAdvisor


from DSE.ResumeAuditor import ResumeAuditor

from SmartResume.ResumeRewriter import ResumeRewriter
from SmartResume.PDFCompiler import PDFCompiler


from mock_interview.router import interview_router

app = FastAPI(title="AI Resume Backend Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Update with your Next.js port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(interview_router)

print("🚀 Initializing AI Engines. Please wait...")

# setting up the ATS 
parser = ResumeParser()
matcher = SemanticMatcher(db_path="ATS/data/job_dataset.json")
advisor =  LLMAdvisor()

# setting up DSE engine 
auditor = ResumeAuditor()

# setting up smart resume 
rewriter = ResumeRewriter()
compiler = PDFCompiler(template_dir="SmartResume/")

print("✅ All Engines Online.")


# route-1 the ATS pipeline 
@app.get("/api/ats/roles")
async def get_available_roles():
    try:
        roles = [title.title() for title in matcher.job_db.keys()]
        return JSONResponse(content={"roles": sorted(roles)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ats/analyze")
async def analyze_ats_match(file: UploadFile = File(...),target_role: str = Form(...)):
    try:
        # setup the extractor 
        extractor = TextExtraction(file)
        raw_text,sections = await extractor.process()

        # parsing 
        parsed_resume_json = parser.parse(raw_text, sections)

        # do the vector math
        match_results = matcher.calculate_match(parsed_resume_json, target_role)

        # call the advisor 
        # fetch the job selected 
        job_template = matcher._fetch_job_template(target_role)
        advice_json = advisor.generate_advice(parsed_resume_json, job_template, match_results)

        return JSONResponse(content={
            "parsed_data": parsed_resume_json,
            "match_data": match_results,
            "advice": advice_json
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# DSE engine 
@app.post("/api/dse/audit")
async def audit_resume(file:UploadFile = File(...)):
    try:
        extractor = TextExtraction(file)
        raw_text,sections = await extractor.process()

        # parsing 
        parsed_resume_json = parser.parse(raw_text, sections)

        # for this we need the parsed and the sections

        score_card = auditor.audit_resume(parsed_resume_json, sections)
        if "error" in score_card:
            raise HTTPException(status_code=500, detail=score_card["error"])

        # Return both the parsed data and the scorecard for the frontend UI dashboard
        return JSONResponse(content={
            "parsed_resume": parsed_resume_json,
            "scorecard": score_card
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# setting up the smart resume 
@app.post("/api/dse/upgrade")
async def upgrade_and_compile_resume(payload: dict):
    try:
        parsed_resume = payload.get("parsed_resume")
        scorecard = payload.get("scorecard")

        if not parsed_resume or not scorecard:
            raise HTTPException(status_code=400, detail="Missing parsed_resume or scorecard in payload.")

        # 1. Rewrite based on the scorecard feedback
        enhanced_data = rewriter.rewrite_resume(parsed_resume, scorecard)

        if "error" in enhanced_data:
            raise HTTPException(status_code=500, detail=enhanced_data["error"])

        # 2. Compile to PDF bytes in memory
        pdf_bytes = compiler.generate_pdf(enhanced_resume_data=enhanced_data, output_filepath=None)

        if not pdf_bytes:
            raise HTTPException(status_code=500, detail="Failed to compile PDF.")

        # 3. Return the binary file directly to the browser
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{enhanced_data.get("name", "Optimized").replace(" ", "_")}_Resume.pdf"'
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))