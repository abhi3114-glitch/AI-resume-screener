from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
from resume_parser import parse_resume
from matcher import match_resume_to_job
import uuid
import json

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# simple in-memory store for demo
STORE = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    f = request.files.get('resume')
    if not f:
        return "No file", 400
    uid = str(uuid.uuid4())
    path = os.path.join(UPLOAD_FOLDER, uid + "_" + f.filename)
    f.save(path)
    parsed = parse_resume(path)
    # simplistic matching demo
    matched = match_resume_to_job(parsed, {
        "title": "Backend Engineer",
        "skills": ["python", "flask", "sql"]
    })
    STORE[uid] = {
        "parsed": parsed,
        "matched": matched
    }
    return jsonify({"result_id": uid})

@app.route('/results/<id>')
def results(id):
    data = STORE.get(id)
    if not data:
        # demo data
        data = {
            "name": "Demo Candidate",
            "initials": "DC",
            "headline": "Software Engineer",
            "match_score": 78,
            "top_skills": ["Python","Flask","SQL","Docker"],
            "reasons": ["Has Python", "Has Flask experience", "Relevant projects"],
            "cleaned_text": "Demo parsed resume text...",
            "skill_labels": ["Python","Flask","SQL","Docker","AWS","GIT"],
            "skill_values": [85,70,60,55,40,75],
            "candidate_id": "demo",
            "overlap_skills": ["Python","Flask"]
        }
    else:
        parsed = data['parsed']
        matched = data['matched']
        data = {
            "name": parsed.get("name","Candidate Name"),
            "initials": "".join([p[0] for p in parsed.get("name","C").split()])[:2],
            "headline": parsed.get("title",""),
            "match_score": matched.get("score", 0),
            "top_skills": parsed.get("skills", [])[:8],
            "reasons": matched.get("reasons", []),
            "cleaned_text": parsed.get("text",""),
            "skill_labels": parsed.get("skills",[])[:6],
            "skill_values": [80]*len(parsed.get("skills",[])[:6]),
            "candidate_id": id,
            "overlap_skills": list(set(parsed.get("skills",[])).intersection(set(["python","flask","sql"])))
        }
    return render_template('result.html', data=data)

@app.route('/report/<id>')
def report(id):
    # placeholder: return the rendered results as html file
    data = STORE.get(id)
    return redirect(url_for('results', id=id))

if __name__ == '__main__':
    app.run(debug=True)
