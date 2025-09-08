# matcher.py
from sentence_transformers import SentenceTransformer, util
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List
import re

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

class ResumeMatcher:
    def __init__(self, model_name=MODEL_NAME):
        self.model = SentenceTransformer(model_name)

    def embed_text(self, texts: List[str]):
        return self.model.encode(texts, convert_to_tensor=True)

    def compute_similarity_score(self, resume_text: str, jd_text: str) -> float:
        emb = self.embed_text([resume_text, jd_text])
        sim = util.cos_sim(emb[0], emb[1]).item()
        # normalize from [-1,1] to [0,1]
        score = (sim + 1) / 2
        return float(score)

    def skill_overlap(self, resume_skills: List[str], jd_skills: List[str]) -> float:
        # lowercase and compare sets
        rs = set([s.lower() for s in resume_skills])
        js = set([s.lower() for s in jd_skills])
        if not js:
            return 0.0
        overlap = rs.intersection(js)
        return len(overlap) / len(js)

    def extract_skills_from_text(self, text: str, top_k=20) -> List[str]:
        # naive extraction: look for common tech tokens (split on non-word and filter)
        tokens = re.findall(r"[A-Za-z\+\#\-\.]+", text)
        tokens = [t for t in tokens if len(t) > 1 and not t.isdigit()]
        # frequency sort
        freq = {}
        for t in tokens:
            key = t.lower()
            freq[key] = freq.get(key, 0) + 1
        sorted_skills = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        skills = [s for s, _ in sorted_skills[:top_k]]
        return skills

    def overall_score(self, resume_text: str, jd_text: str, resume_skills: List[str], jd_skills: List[str]) -> Dict:
        sim = self.compute_similarity_score(resume_text, jd_text)
        skill_overlap = self.skill_overlap(resume_skills, jd_skills)
        # weight them: 70% semantic similarity, 30% skill overlap (tune as needed)
        score = 0.7 * sim + 0.3 * skill_overlap
        return {"semantic_similarity": sim, "skill_overlap": skill_overlap, "overall_score": score}
