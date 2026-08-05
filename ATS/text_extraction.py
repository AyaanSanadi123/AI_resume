import os
import json
import tempfile
import pymupdf
import pymupdf4llm
import docx  
import numpy as np
import io 
from fastapi import HTTPException, UploadFile
from paddleocr import PaddleOCR
from PIL import Image

# ------------------------------------------------------------------
# Singleton / Lazy Loader for PaddleOCR
# ------------------------------------------------------------------
_PADDLE_OCR_ENGINE = None

def get_paddle_ocr():
    global _PADDLE_OCR_ENGINE
    if _PADDLE_OCR_ENGINE is None:
        # Instantiate safely inside the lazy loader function
        _PADDLE_OCR_ENGINE = PaddleOCR(use_angle_cls=True, lang="en")
    return _PADDLE_OCR_ENGINE

class TextExtraction:
    ALLOWED_EXTENSIONS = [".pdf", ".docx"]
    
    def __init__(self, file: UploadFile):
        self.file = file 
        self.filename = file.filename 
        self.ext = self._validate_file()

    def _validate_file(self) -> str:
        # Validate the file extension 
        ext = os.path.splitext(self.filename)[1].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail="Invalid file format. Only PDF and DOCX allowed."
            )
        return ext

    def _extract_pdf(self, file_path: str) -> tuple[str, list[dict]]:
        cleaned_sections = []
        full_text_stream = []

        with pymupdf.open(file_path) as doc:
            # Step 1: Quick Diagnostic Check across all pages
            total_raw_text = "".join([page.get_text("text") for page in doc]).strip()
            raw_char_count = len(total_raw_text)

            # -------------------------------------------------------------
            # BRANCH A: Native Text PDF (raw_char_count > 50)
            # -------------------------------------------------------------
            if raw_char_count > 50:
                # Tier 1: Try GNN-powered layout extraction
                try:
                    json_data = pymupdf4llm.to_json(doc)
                    data = json.loads(json_data) if isinstance(json_data, str) else json_data

                    for page in data.get("pages", []):
                        for box in page.get("boxes", []):
                            box_class = box.get("boxclass", "")
                            if box_class in ["page-header", "page-footer"]:
                                continue

                            box_lines = []
                            for line in box.get("textlines", []):
                                # FIX: Join spans with explicit spaces to prevent "sticky text"
                                spans_text = [
                                    span.get("text", "").strip() 
                                    for span in line.get("spans", []) 
                                    if span.get("text", "").strip()
                                ]
                                if spans_text:
                                    box_lines.append(" ".join(spans_text))

                            box_text = " ".join(box_lines).strip()
                            if box_text:
                                cleaned_sections.append({
                                    "class": box_class,
                                    "x0": box.get("x0"),
                                    "y0": box.get("y0"),
                                    "text": box_text,
                                })
                                full_text_stream.append(box_text)
                except Exception:
                    pass  # Fall through to Tier 2 if layout engine fails

                # Tier 2: Fallback to standard PyMuPDF blocks if Tier 1 produced nothing
                if not full_text_stream:
                    for page in doc:
                        blocks = page.get_text("blocks")
                        for b in blocks:
                            if b[6] == 0:  # Text block type
                                text = b[4].strip()
                                if text:
                                    cleaned_sections.append({
                                        "class": "block",
                                        "x0": b[0],
                                        "y0": b[1],
                                        "text": text,
                                    })
                                    full_text_stream.append(text)

            # -------------------------------------------------------------
            # BRANCH B: Scanned / Flattened PDF -> Tier 3 (PaddleOCR)
            # -------------------------------------------------------------
            if not full_text_stream:
                print(f"⚠️ Triggering Tier 3 (PaddleOCR Engine) for {self.filename}...")
                ocr_engine = get_paddle_ocr()

                for page in doc:
                    # 1. Render PDF page to high-res image (300 DPI) in RAM
                    pix = page.get_pixmap(dpi=300)
                    img_pil = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")
                    img_np = np.array(img_pil)

                    # 2. Execute PaddleOCR inference
                    results = ocr_engine.ocr(img_np)

                    if not results or not results[0]:
                        continue
                    
                    res = results[0]
                    page_lines = []

                    # --- FORMAT 1: PaddleX 3.7+ (Dictionary-like object) ---
                    if isinstance(res, dict) or hasattr(res, 'keys'):
                        # The new backend stores lists inside these keys
                        texts = res.get('rec_texts', []) or res.get('rec_text', [])
                        boxes = res.get('dt_polys', []) or res.get('boxes', [])
                        scores = res.get('rec_scores', []) or res.get('scores', [])
                        
                        for i in range(len(texts)):
                            cleaned_text = str(texts[i]).strip()
                            if cleaned_text:
                                # Safely get coordinates and confidence
                                box = boxes[i] if i < len(boxes) else [[0.0, 0.0]]
                                conf = scores[i] if i < len(scores) else 1.0
                                
                                x0, y0 = box[0][0], box[0][1]
                                
                                cleaned_sections.append({
                                    "class": "ocr_text",
                                    "x0": float(x0),
                                    "y0": float(y0),
                                    "confidence": round(float(conf), 4),
                                    "text": cleaned_text,
                                })
                                page_lines.append(cleaned_text)

                    # --- FORMAT 2: Legacy PaddleOCR (List of Lists) ---
                    elif isinstance(res, list):
                        for line in res:
                            try:
                                box_coords = line[0]
                                text_info = line[1]
                                
                                cleaned_text = str(text_info[0]).strip()
                                confidence = float(text_info[1]) if len(text_info) > 1 else 1.0
                                
                                if cleaned_text:
                                    x0, y0 = box_coords[0][0], box_coords[0][1]
                                    cleaned_sections.append({
                                        "class": "ocr_text",
                                        "x0": float(x0),
                                        "y0": float(y0),
                                        "confidence": round(float(confidence), 4),
                                        "text": cleaned_text,
                                    })
                                    page_lines.append(cleaned_text)
                            except Exception as e:
                                print(f"   ⚠️ Warning: Skipped OCR line due to parsing error: {e}")

                    if page_lines:
                        full_text_stream.append("\n".join(page_lines))
        
        # ---> FIX: Properly indented to execute for BOTH Branch A and Branch B <---
        return "\n".join(full_text_stream), cleaned_sections

    def _extract_docx(self, file_path: str) -> tuple[str, list[dict]]:
        doc = docx.Document(file_path)
        full_text = []
        cleaned_sections = []

        for i, paragraph in enumerate(doc.paragraphs):
            text = paragraph.text.strip()
            if text:
                full_text.append(text)
                cleaned_sections.append({
                    "class": "text", 
                    "x0": 0,       # Fake coordinates since DOCX is linear
                    "y0": i * 10,  
                    "text": text
                })
                
        return "\n".join(full_text), cleaned_sections

    def _normalize_text(self, raw_text: str) -> str:
        return " ".join(raw_text.split())

    async def process(self) -> tuple[str, list[dict]]:
        """Master pipeline: stages file, extracts, normalizes, and cleans up."""
        temp_path = None

        try:
            # 1. Secure TempFile Staging
            with tempfile.NamedTemporaryFile(delete=False, suffix=self.ext) as temp_file:
                temp_file.write(await self.file.read())
                temp_path = temp_file.name

            # 2. Extract based on format
            if self.ext == ".pdf":
                raw_text, sections = self._extract_pdf(temp_path)
            elif self.ext == ".docx":
                raw_text, sections = self._extract_docx(temp_path)
            else:
                raise HTTPException(status_code=400, detail="Unsupported format.")

            # 3. Normalize text streams
            normalized_full_text = self._normalize_text(raw_text)
            
            for section in sections:
                section["text"] = self._normalize_text(section["text"])

            # 4. Return Clean Data
            return normalized_full_text, sections

        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=500, 
                detail=f"Text extraction pipeline failed: {str(e)}"
            )

        finally:
            # 5. Guaranteed cleanup
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)