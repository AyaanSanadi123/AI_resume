import json
import re

def clean_and_save_database(input_filename="master_jobs_database.json", output_filename="cleaned master database.json"):
    # 1. Load the raw JSON file
    with open(input_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    def normalize_title(title: str) -> str:
        # Strip trailing company suffixes, locations, pipe/dash delimiters
        title = re.sub(r'\s*[|\-–—]\s*.*$', '', title)
        return title.strip().title()

    cleaned_records = []
    seen_descriptions = set()

    for item in data:
        skills = item.get('skills', [])
        
        # Rule 1: Pruning Skill-less Entries
        if not skills or len(skills) == 0:
            continue
            
        desc = item.get('description', '').strip()
        
        # Rule 2: Advanced Deduplication (exact description content)
        if desc in seen_descriptions:
            continue
        seen_descriptions.add(desc)
        
        # Rule 3: Title Normalization
        item['role_title'] = normalize_title(item.get('role_title', ''))
        
        cleaned_records.append(item)

    # Save to the new requested JSON file
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(cleaned_records, f, indent=2, ensure_ascii=False)

    print(f"✨ Successfully cleaned database!")
    print(f"📊 Original Count: {len(data)}")
    print(f"📊 Cleaned Count:  {len(cleaned_records)}")
    print(f"📁 Saved to '{output_filename}'")

if __name__ == "__main__":
    clean_and_save_database()