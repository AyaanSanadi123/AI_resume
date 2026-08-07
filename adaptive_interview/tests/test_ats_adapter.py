print("========== TEST STARTED ==========")
from adaptive_interview.adapters.ats_adapter import TemporaryATSProvider
from adaptive_interview.models.resume_profile import ResumeProfile

# load ResumeProfile however your project expects
resume = ResumeProfile.model_validate_json(
    open("ATS/extraction_outputs/accountant_easy_parsed.json").read()
)

job_description = """
AI/ML Intern

Required:
Python
PyTorch
Docker
REST APIs
"""

ats = TemporaryATSProvider()

analysis = ats.generate_ats_analysis(
    resume,
    job_description
)

print("\n========== ATS Analysis ==========")
print(analysis.model_dump_json(indent=2))