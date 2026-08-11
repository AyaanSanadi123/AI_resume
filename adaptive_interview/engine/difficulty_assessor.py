import json
from pathlib import Path
from typing import Optional, Dict, Any

from ..models.difficulty_profile import DifficultyAssessment
from ..models.upstream_candidate import UpstreamCandidate
from ..models.knowledge_summary import KnowledgeSummary
from ..services.gemini_client import GeminiClient

class DifficultyAssessorEngine:
    def __init__(self, client: GeminiClient):
        self.client = client
        self.prompt_path = Path(__file__).parent.parent / "prompts" / "difficulty_assessor.txt"

    def _load_prompt(self) -> str:
        with open(self.prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def generate(
        self,
        candidate: UpstreamCandidate,
        target_role: str,
        job_description: Optional[str],
        matched_skills: list[str],
        missing_skills: list[str],
        llm_advisor: Dict[str, Any],
        knowledge_summary: KnowledgeSummary
    ) -> DifficultyAssessment:
        prompt_template = self._load_prompt()
        
        prompt = prompt_template.replace("{resume}", json.dumps(candidate.model_dump(), indent=2))
        prompt = prompt.replace("{target_role}", target_role)
        prompt = prompt.replace("{job_description}", job_description or "")
        prompt = prompt.replace("{matched_skills}", json.dumps(matched_skills, indent=2))
        prompt = prompt.replace("{missing_skills}", json.dumps(missing_skills, indent=2))
        prompt = prompt.replace("{llm_advisor}", json.dumps(llm_advisor, indent=2))
        prompt = prompt.replace("{knowledge_summary}", json.dumps(knowledge_summary.model_dump(), indent=2))
        
        return self.client.generate_structured(prompt, DifficultyAssessment)
