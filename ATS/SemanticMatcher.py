import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, Any

class SemanticMatcher:

    def __init__(self,db_path:str = "jobs_database.json"):
        # load the local database into memory 
        # load the embedding model
        self.model = SentenceTransformer('BAAI/bge-small-en-v1.5')

        with open(db_path, 'r', encoding='utf-8') as f:
            raw_db = json.load(f)

        self.job_db = {job['role_title'].lower(): job for job in raw_db}

        print(f"✅ Indexed {len(self.job_db)} unique roles. Engine Ready.")
            

    def _fetch_job_template(self,job_title:str)-> dict:
        # scans the json database and returns the target dictionary
        job = self.job_db.get(job_title.lower()) 
        if not job:
            raise ValueError(f"Job title '{job_title}' not found in the master database.")
        return job

    def _flatten_resume(self,resume_json:dict)->str:
        # this extracts the skills array, experience bullets,project bullets 
        # returns a single dense string 
        components = []
        
        # Add explicit skills
        skills = resume_json.get("skills", [])
        if skills:
            components.append("Skills: " + ", ".join(skills))
            
        # Extract Experience bullets (ignoring company names/dates)
        for exp in resume_json.get("experience", []):
            bullets = exp.get("bullets", [])
            components.extend(bullets)
            
        # Extract Project bullets
        for proj in resume_json.get("projects", []):
            bullets = proj.get("bullets", [])
            components.extend(bullets)
            
        return " ".join(components)

    def _flatten_job(self,job_json:dict) -> str:
        # extracts relevent info from the job dict 
        # role_title,category,skills array
        # returns a single dense string 
        title = job_json.get("role_title", "")
        category = job_json.get("category", "")
        skills = job_json.get("skills", [])
        
        components = [f"Role: {title}", f"Domain: {category}"]
        if skills:
            components.append("Required Skills: " + ", ".join(skills))
            
        return " ".join(components)
    
    def calculate_match(self,resume_json:dict,target_job_title:str) -> dict:
        # 1. call fetch_job_template
        # 2. Calls _flatten_resume() and _flatten_job()
        job_template = self._fetch_job_template(target_job_title)
        flat_resume = self._flatten_resume(resume_json)
        flat_job = self._flatten_job(job_template)

        vectors = self.model.encode([flat_resume,flat_job])
        resume_vector = vectors[0].reshape(1, -1)
        job_vector = vectors[1].reshape(1, -1)


        # 3. Compute Cosine Similarity
        similarity = cosine_similarity(resume_vector, job_vector)[0][0]
        match_score_percentage = round(float(similarity) * 100, 1)

        resume_skills_set = {s.lower() for s in resume_json.get("skills", [])}
        job_skills_set = {s.lower() for s in job_template.get("skills", [])}
        
        matched_skills = list(resume_skills_set.intersection(job_skills_set))
        missing_skills = list(job_skills_set.difference(resume_skills_set))
        
        return {
            "target_role": job_template.get("role_title"),
            "match_score": match_score_percentage,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "system_logs": {
                "flattened_resume_preview": flat_resume[:200] + "...",
                "flattened_job_preview": flat_job
            }
        }


    