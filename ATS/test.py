import os
import json
import asyncio
import traceback
import platform

if platform.system() == "Windows":
    os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"
    os.environ["FLAGS_use_mkldnn"] = "0"

from text_extraction import TextExtraction
from resume_parser import ResumeParser  # Import Phase 2

# ------------------------------------------------------------------
# 2. Mock UploadFile for local testing without running FastAPI
# ------------------------------------------------------------------
class MockUploadFile:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.filename = os.path.basename(file_path)

    async def read(self) -> bytes:
        with open(self.file_path, "rb") as f:
            return f.read()

# ------------------------------------------------------------------
# 3. Main Batch Test Runner
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

    # Instantiate the parser once (Stateless Pipeline)
    parser = ResumeParser()

    passed_count = 0
    failed_count = 0

    for idx, filename in enumerate(sample_files, start=1):
        file_path = os.path.join(input_dir, filename)
        base_name = os.path.splitext(filename)[0]
        
        print(f"[{idx}/{len(sample_files)}] Processing: {filename}...")

        try:
            # Wrap local file in mock UploadFile
            mock_file = MockUploadFile(file_path)
            
            # PHASE 1: Text & Layout Extraction
            extractor = TextExtraction(mock_file)
            normalized_text, sections = await extractor.process()

            # PHASE 2: Semantic Parsing (Regex + State Machine)
            parsed_resume = parser.parse(normalized_text, sections)

            # Create individual output paths
            txt_output_path = os.path.join(output_dir, f"{base_name}_text.txt")
            json_output_path = os.path.join(output_dir, f"{base_name}_parsed.json")

            # 1. Save normalized full text stream (for manual review if needed)
            with open(txt_output_path, "w", encoding="utf-8") as f:
                f.write(normalized_text)

            # 2. Save the final Structured JSON from Phase 2
            with open(json_output_path, "w", encoding="utf-8") as f:
                json.dump(parsed_resume, f, indent=2, ensure_ascii=False)

            print(f"    ✅ Success -> Parsed output saved to '{output_dir}/{base_name}_parsed.json'")
            passed_count += 1

        except Exception as e:
            print(f"    ❌ Failed -> {str(e)}")
            traceback.print_exc()
            failed_count += 1

    print("\n" + "=" * 50)
    print(f"📊 TEST SUMMARY:")
    print(f"    Total Processed: {len(sample_files)}")
    print(f"    Passed:         {passed_count}")
    print(f"    Failed:         {failed_count}")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(run_batch_tests())