import os
import re
# PDF/DOCX readers
try:
    import pdfplumber
except Exception:
    pdfplumber = None
try:
    from pdfminer.high_level import extract_text as pdfminer_extract_text
except Exception:
    pdfminer_extract_text = None
try:
    import docx
except Exception:
    docx = None
def _extract_text_pdf(path):
    # prefer pdfplumber if available
    if pdfplumber:
        try:
            text = []
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
            return "\\n".join(text)
        except Exception:
            pass
    # fallback to pdfminer
    if pdfminer_extract_text:
        try:
            return pdfminer_extract_text(path)
        except Exception:
            pass
    # last resort
    return ""
def _extract_text_docx(path):
    if docx:
        try:
            d = docx.Document(path)
            paras = [p.text for p in d.paragraphs if p.text]
            return "\\n".join(paras)
        except Exception:
            pass
    return ""
def _extract_text_fallback(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
            return fh.read()
    except Exception:
        return ""
def extract_text(path):
    path = str(path)
    ext = os.path.splitext(path)[1].lower()
    if ext == '.pdf':
        t = _extract_text_pdf(path)
        if t:
            return t
        return _extract_text_fallback(path)
    elif ext in ('.docx', '.doc'):
        t = _extract_text_docx(path)
        if t:
            return t
        # .doc (old format) often fails; fallback to plain read
        return _extract_text_fallback(path)
    else:
        return _extract_text_fallback(path)
def parse_resume(path):
    text = extract_text(path) or ''
    # naive cleaning
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    name = lines[0] if lines else "Candidate"
    skills = []
    # find a line likely containing skills
    for l in lines:
        low = l.lower()
        if 'skill' in low or 'technical skills' in low or 'skills:' in low:
            # split common separators
            parts = re.split(r'[,:;•\\-\\|\\/]', l)
            parts = [p.strip() for p in parts if p.strip() and len(p.strip()) < 60]
            # remove heading words like 'skills' from list
            skills = [re.sub(r'(?i)skills?\\b', '', p).strip() for p in parts if p.strip()]
            break
    # fallback: extract likely skill tokens from the whole text (simple heuristic)
    if not skills:
        # look for tech words (very small builtin list — you can expand)
        tech_words = ['python','java','c++','c#','javascript','node','react','angular','flask','django','sql','postgres','mysql','mongodb','aws','docker','kubernetes','git']
        found = set()
        txt_lower = text.lower()
        for w in tech_words:
            if w in txt_lower:
                found.add(w)
        skills = sorted(found)
    return {
        "name": name,
        "text": text,
        "skills": [s.lower() for s in skills]
    }
