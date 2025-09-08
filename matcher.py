def match_resume_to_job(parsed, job):
    # naive matching
    skills = set(parsed.get('skills',[]))
    req = set([s.lower() for s in job.get('skills',[])])
    overlap = skills.intersection(req)
    score = int((len(overlap) / max(1, len(req))) * 100)
    reasons = [f"Has {s}" for s in overlap]
    return {"score": score, "reasons": reasons}
