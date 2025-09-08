# AI Resume Screener

Simple Flask app that analyzes a resume against a job description and returns a fit score and missing skills.

## Run
1. python -m venv .venv
2. Activate the venv:
   - On macOS/Linux: `source .venv/bin/activate`
   - On Windows PowerShell: `.venv\\Scripts\\Activate.ps1`
3. pip install -r requirements.txt
4. (Optional) Download spaCy model for best results: `python -m spacy download en_core_web_sm`
5. python app.py
6. Open http://127.0.0.1:5000

Supported uploads: .pdf, .docx, .txt
