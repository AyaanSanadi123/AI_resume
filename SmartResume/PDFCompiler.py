import json
import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from pathlib import Path
class PDFCompiler:
    def __init__(self, template_dir="."):
        print("🖨️ Booting up PDF Compiler Engine (Jinja2 + WeasyPrint)...")
        
        # Resolve the template directory securely relative to the script or current dir
        self.template_path = Path(template_dir).resolve()
        
        # Fallback check: if the folder doesn't exist, try looking in the current working directory
        if not self.template_path.exists():
            self.template_path = Path(".").resolve()
            
        if not self.template_path.exists():
            raise FileNotFoundError(f"❌ Error: The template directory could not be resolved.")
            
        self.env = Environment(loader=FileSystemLoader(str(self.template_path)))
        
        try:
            self.template = self.env.get_template("resume_template.html")
        except Exception as e:
            raise FileNotFoundError(f"❌ Error: Could not find 'resume_template.html' in {self.template_path}. {e}")

    def generate_pdf(self, enhanced_resume_data: dict, output_filepath: str = None) -> bytes:
        try:
            rendered_html = self.template.render(resume=enhanced_resume_data)
            
            # 1. Generate the PDF bytes in memory
            pdf_bytes = HTML(string=rendered_html).write_pdf()
            
            # 2. If a filepath is provided, write the bytes to disk manually
            if output_filepath:
                with open(output_filepath, "wb") as f:
                    f.write(pdf_bytes)
                    
            return pdf_bytes
        except Exception as e:
            print(f"🔥 DETAILED PDF EXCEPTION: {repr(e)}")
            import traceback
            traceback.print_exc()
            return None
