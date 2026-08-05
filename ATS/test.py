import os
import json
import asyncio
import traceback
from text_extraction import TextExtraction  # Import your class

# ------------------------------------------------------------------
# 1. Mock UploadFile for local testing without running FastAPI
# ------------------------------------------------------------------
class MockUploadFile:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.filename = os.path.basename(file_path)

    async def read(self) -> bytes:
        with open(self.file_path, "rb") as f:
            return f.read()

# ------------------------------------------------------------------
# 2. Main Batch Test Runner
# ------------------------------------------------------------------
async def run_batch_tests(input_dir: str = "./test_resumes", output_dir: str = "./extraction_outputs"):
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(input_dir):
        print(f"❌ Input directory '{input_dir}' does not exist. Create it and add sample files.")
        return

    # Gather all supported files
    supported_exts = (".pdf", ".docx")
    sample_files = [
        f for f in os.listdir(input_dir) 
        if f.lower().endswith(supported_exts)
    ]

    if not sample_files:
        print(f"⚠️ No PDF or DOCX files found in '{input_dir}'.")
        return

    print(f"🚀 Found {len(sample_files)} sample files. Starting extraction test...\n")

    passed_count = 0
    failed_count = 0

    for idx, filename in enumerate(sample_files, start=1):
        file_path = os.path.join(input_dir, filename)
        base_name = os.path.splitext(filename)[0]
        
        print(f"[{idx}/{len(sample_files)}] Processing: {filename}...")

        try:
            # Wrap local file in mock UploadFile
            mock_file = MockUploadFile(file_path)
            
            # Execute your extraction pipeline
            extractor = TextExtraction(mock_file)
            normalized_text, sections = await extractor.process()

            # Create individual sub-folder or output files per resume
            txt_output_path = os.path.join(output_dir, f"{base_name}_text.txt")
            json_output_path = os.path.join(output_dir, f"{base_name}_sections.json")

            # 1. Save normalized full text stream
            with open(txt_output_path, "w", encoding="utf-8") as f:
                f.write(normalized_text)

            # 2. Save structured layout sections as formatted JSON
            with open(json_output_path, "w", encoding="utf-8") as f:
                json.dump(sections, f, indent=2, ensure_ascii=False)

            print(f"   ✅ Success -> Output saved to '{output_dir}/'")
            passed_count += 1

        except Exception as e:
            print(f"   ❌ Failed -> {str(e)}")
            # Log traceback for debugging severe extraction crashes
            traceback.print_exc()
            failed_count += 1

    print("\n" + "=" * 50)
    print(f"📊 TEST SUMMARY:")
    print(f"   Total Processed: {len(sample_files)}")
    print(f"   Passed:         {passed_count}")
    print(f"   Failed:         {failed_count}")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(run_batch_tests())

"""import pymupdf

pdf_path = "test_resumes/resume1.pdf"
doc = pymupdf.open(pdf_path)
page = doc[0]

# Test 1: Standard PyMuPDF text extraction
raw_text = page.get_text("text")
print(f"--- DIAGNOSTIC RESULTS ---")
print(f"1. Raw Text Character Count: {len(raw_text.strip())}")

# Test 2: Check for embedded raster images
images = page.get_images()
print(f"2. Embedded Images Count:    {len(images)}")

# Test 3: Check for vector drawing paths (Outlined Text)
drawings = page.get_drawings()
print(f"3. Vector Drawings Count:   {len(drawings)}")"""