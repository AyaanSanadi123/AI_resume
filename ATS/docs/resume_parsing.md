# Phase 2: Semantic Spatial Parsing & LLM Engine (`resume_parser.py`)

The parsing module translates raw text streams and spatial layout coordinates into structured data structures.

## Deterministic Entity Extraction
- Uses rigid regular expressions to extract high-precision contact information:
  - Emails
  - Phone numbers
  - GitHub / LinkedIn links
- Performs extraction independently before LLM processing.

## Spatial Coordinate Sorting (`_sort_spatially`)
- Groups text blocks into vertical **Y-buckets** (15px intervals).
- Sorts blocks left-to-right using their `x0` coordinates.
- Preserves natural reading order across multi-column layouts.

## Strict Pydantic Data Contracts

Robust data models capture edge cases across multiple resume sections.

- **ExperienceModel** – Formal employment and corporate internships.
- **ProjectModel** – Independent, academic, or personal software builds.
- **EducationModel** – Degrees, institutions, and timelines.
- **CertificationModel** – Professional licenses and credentials.
- **ResumeSchema** – Master container managing summary, skills, awards, and nested objects.

## Gemini Semantic Integration
- Uses **gemini-3.5-flash**.
- Temperature set to **0.0**.
- Enforces strict JSON response schemas.
- Minimizes hallucinations while guaranteeing output format compliance.