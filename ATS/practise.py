


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


def parse_resume_json(json_data):
    if isinstance(json_data,str):
        data = json.loads(json_data)
    else:
        data = json_data

    cleaned_sections = []
    full_text_stream = []

    for page in data.get("pages",[]):
        page_num = page["page_number"]
        print(f"\n--- PROCESSING PAGE {page_num} ---")

        for box in page.get("boxes",[]):
            box_class = box.get("boxclass")

            # filter out the headers and footers... 
            if box_class in ["page-header", "page-footer"]:
                continue

            # extract the text from the nested lines 
            box_text = ""

            for line in box.get("textlines",[]):
                line_text = "".join([span.get("text", "") for span in line.get("spans", [])])
                box_text += line_text + " "

            box_text = box_text.strip()

            if not box_text:
                continue

             
            cleaned_sections.append({
                "class": box_class,
                "x0": box.get("x0"),
                "y0": box.get("y0"),
                "text": box_text
            })
            full_text_stream.append(box_text)
    return "\n".join(full_text_stream), cleaned_sections