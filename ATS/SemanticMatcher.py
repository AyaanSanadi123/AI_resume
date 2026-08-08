import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, Any

class SemanticMatcher:

    def __init__(self, db_path: str = "data/job_dataset.json"):
        # Load embedding model
        self.model = SentenceTransformer('BAAI/bge-small-en-v1.5')

        with open(db_path, 'r', encoding='utf-8') as f:
            raw_db = json.load(f)

        # Safely index roles handling missing 'Title' or 'role_title' keys
        self.job_db = {}
        for job in raw_db:
            title = job.get('Title') or job.get('role_title')
            if title:
                self.job_db[title.lower()] = job

        print(f"✅ Indexed {len(self.job_db)} unique roles. Engine Ready.")

    def _fetch_job_template(self, title: str) -> dict:
        job = self.job_db.get(title.lower()) 
        if not job:
            raise ValueError(f"Job title '{title}' not found in the master database.")
        return job

    def _flatten_resume(self, resume_json: dict) -> str:
        components = []
        
        # Explicit skills
        skills = resume_json.get("skills", [])
        if skills:
            components.append("Skills: " + ", ".join(skills))
            
        # Experience bullets
        for exp in resume_json.get("experience", []):
            bullets = exp.get("bullets", [])
            components.extend(bullets)
            
        # Project bullets
        for proj in resume_json.get("projects", []):
            bullets = proj.get("bullets", [])
            components.extend(bullets)
            
        return " ".join(components)

    def _flatten_job(self, job_json: dict) -> str:
        # Supports new schema ('Title', 'Skills', 'Responsibilities', 'ExperienceLevel')
        # and old schema ('role_title', 'skills', 'description', 'category')
        title = job_json.get("Title") or job_json.get("role_title", "")
        level = job_json.get("ExperienceLevel") or job_json.get("category", "")
        skills = job_json.get("Skills") or job_json.get("skills", [])
        responsibilities = job_json.get("Responsibilities") or [job_json.get("description", "")]
        
        components = [f"Role: {title}"]
        if level:
            components.append(f"Level/Domain: {level}")
        if skills:
            components.append("Required Skills: " + ", ".join(skills))
        if responsibilities:
            components.extend(responsibilities)
            
        return " ".join(components)
    
    def calculate_match(self, resume_json: dict, target_job_title: str) -> dict:
        job_template = self._fetch_job_template(target_job_title)
        flat_resume = self._flatten_resume(resume_json)
        flat_job = self._flatten_job(job_template)

        vectors = self.model.encode([flat_resume, flat_job])
        resume_vector = vectors[0].reshape(1, -1)
        job_vector = vectors[1].reshape(1, -1)

        # Compute Cosine Similarity
        similarity = cosine_similarity(resume_vector, job_vector)[0][0]
        match_score_percentage = round(float(similarity) * 100, 1)

        # Skill intersection handling case insensitivity & alternate key names
        resume_skills_set = {s.lower() for s in resume_json.get("skills", [])}
        raw_job_skills = job_template.get("Skills") or job_template.get("skills", [])
        job_skills_set = {s.lower() for s in raw_job_skills}
        
        matched_skills = list(resume_skills_set.intersection(job_skills_set))
        missing_skills = list(job_skills_set.difference(resume_skills_set))
        
        target_title = job_template.get("Title") or job_template.get("role_title")
        
        return {
            "target_role": target_title,
            "match_score": match_score_percentage,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "system_logs": {
                "flattened_resume_preview": flat_resume[:200] + "...",
                "flattened_job_preview": flat_job
            }
        }