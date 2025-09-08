# resume_parser.py
import os
import docx2txt
from pdfminer.high_level import extract_text
import re
import spacy
from typing import Dict, List
import nltk

# make sure NLTK data available for tokenization if needed
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

# Load spaCy model globally (load in main to avoid repeated loads)
nlp = None

COMMON_SKILLS = [
    # add/extend this list as needed
    "python","java","c++","c","sql","mongodb","postgresql","mysql","tensorflow",
    "keras","pytorch","scikit-learn","docker","kubernetes","aws","azure","gcp",
    "flask","django","react","node","javascript","html","css","git","linux",
    "opencv","nlp","computer vision","pandas","numpy","matplotlib","seaborn"
]

def ensure_nlp():
    global nlp
    if nlp is None:
        nlp = spacy.load("en_core_web_sm")

def extract_text_from_file(path: str) -> str:
    """Extract plain text from PDF or DOCX (or .txt)."""
    ext = os.path.splitext(path)[1].lower()
    text = ""
    if ext == ".pdf":
        text = extract_text(path)
    elif ext in [".docx", ".doc"]:
        text = docx2txt.process(path)
    elif ext == ".txt":
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    else:
        raise ValueError("Unsupported file type: " + ext)
    return text

def extract_emails(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9.\-+_]+@[a-zA-Z0-9.\-+_]+\.[a-zA-Z]+", text)

def extract_phones(text: str) -> List[str]:
    return re.findall(r"\+?\d[\d\-\s]{7,}\d", text)

def extract_experience_years(text: str) -> float:
    # simple heuristic: look for patterns like "X years" or "X-year"
    nums = re.findall(r"(\d+)\+?\s+(?:years|yrs|year|yr)\b", text, flags=re.I)
    if nums:
        nums = list(map(int, nums))
        return max(nums)
    # fallback: look for "experience" nearby numbers
    m = re.search(r"(\d+)\s+years of experience", text, flags=re.I)
    if m:
        return int(m.group(1))
    return 0.0

def extract_skills(text: str) -> List[str]:
    """Find skills by keyword matching and small spaCy NER heuristics."""
    ensure_nlp()
    text_low = text.lower()
    found = set()
    # keyword match
    for skill in COMMON_SKILLS:
        if re.search(r"\b" + re.escape(skill.lower()) + r"\b", text_low):
            found.add(skill)
    # noun chunk / entity heuristics (grab proper nouns that look like tech names)
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ("ORG", "PRODUCT", "WORK_OF_ART", "NORP"):
            token = ent.text.strip()
            if len(token) < 30:
                found.add(token)
    # also include capitalized words that might be technologies
    for token in doc:
        if token.text[0].isupper() and len(token.text) <= 20:
            if token.text.lower() not in ("Experience", "Education", "Skills"):
                found.add(token.text)
    # filter obviously non-tech words (this is coarse)
    final = [s for s in found if len(s) > 1]
    return sorted(set([s.lower() for s in final]))

def parse_resume(path: str) -> Dict:
    """
    Returns parsed info dict:
    {
      "text": "...",
      "emails": [...],
      "phones": [...],
      "skills": [...],
      "years_experience": X
    }
    """
    text = extract_text_from_file(path)
    emails = extract_emails(text)
    phones = extract_phones(text)
    skills = extract_skills(text)
    years = extract_experience_years(text)
    return {"text": text, "emails": emails, "phones": phones, "skills": skills, "years_experience": years}
