import os
import platform
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware


if platform.system() == "Windows":
    os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"
    os.environ["FLAGS_use_mkldnn"] = "0"



from ATS.text_extraction import TextExtraction
from ATS.resume_parser import ResumeParser
from ATS.SemanticMatcher import SemanticMatcher
from ATS.LLMAdvisor import LLMAdvisor


app = FastAPI(title="AI Resume Backend Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Update with your Next.js port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("🚀 Initializing AI Engines. Please wait...")

# setting up the ATS 
parser = ResumeParser()
matcher = SemanticMatcher()
advisor =  LLMAdvisor()

print("✅ All Engines Online.")


# route-1 the ATS pipeline 
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