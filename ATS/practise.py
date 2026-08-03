


import pymupdf
import pymupdf.layout  # Activates the GNN layout intelligence
import pymupdf4llm
import json

def extract_resume_ast_structure(pdf_path: str):
    # Open the document via PyMuPDF
    doc = pymupdf.open(pdf_path)
    
    # Extract rich layout-aware JSON 
    # This returns blocks, headers, footers, columns, and reading sequence identifiers
    layout_json = pymupdf4llm.to_json(doc)
    
    return layout_json

# Run it on a complex resume
data = extract_resume_ast_structure(r"C:\ayaans folder\AyaanSanadi-resume.pdf")

# Inspect a snippet of how structured the JSON is
print(json.dumps(data, indent=2)[:1000])