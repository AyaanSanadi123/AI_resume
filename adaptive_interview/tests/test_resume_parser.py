from ATS.resume_parser import ResumeParser
import json

# OCR JSON produced by text_extraction.py
with open(
    "ATS/extraction_outputs/accountant_easy_parsed.json",
    "r",
    encoding="utf-8"
) as f:

    sections = json.load(f)

raw_text = "\n".join(
    block["text"]
    for block in sections
)

parser = ResumeParser()

profile = parser.parse(
    raw_text,
    sections
)

print(json.dumps(profile, indent=2))