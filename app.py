# app.py
import os
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, jsonify
from resume_parser import parse_resume
from matcher import ResumeMatcher
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "uploads"
ALLOWED_EXT = {".pdf", ".docx", ".doc", ".txt"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

matcher = ResumeMatcher()

def allowed_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXT

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # file upload
        file = request.files.get("resume")
        jd_text = request.form.get("jd_text", "")
        jd_skills_text = request.form.get("jd_skills", "")
        jd_skills = [s.strip().lower() for s in jd_skills_text.split(",") if s.strip()]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)
            parsed = parse_resume(path)
            # if parser didn't find skills, try matcher extractor
            resume_skills = parsed.get("skills") or matcher.extract_skills_from_text(parsed["text"])
            # compute match
            scores = matcher.overall_score(parsed["text"], jd_text, resume_skills, jd_skills)
            # suggestions: missing skills
            missing = [s for s in jd_skills if s.lower() not in [r.lower() for r in resume_skills]]
            response = {
                "emails": parsed.get("emails", []),
                "phones": parsed.get("phones", []),
                "years_experience": parsed.get("years_experience", 0),
                "resume_skills": resume_skills,
                "jd_skills": jd_skills,
                "scores": scores,
                "missing_skills": missing
            }
            return render_template("result.html", result=response)
        else:
            return "Invalid or missing file (allowed: pdf, docx, txt)", 400
    return render_template("index.html")

# simple static for uploaded files (optional)
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
