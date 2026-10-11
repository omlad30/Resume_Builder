import json
from groq import Groq
from flask import current_app

def get_groq_client():
    api_key = current_app.config.get('GROQ_API_KEY', '').strip()
    return Groq(api_key=api_key) if api_key else None

def generate_resume_from_raw_text(raw_text):
    """Uses Groq Qwen model to structure unformatted text into ATS resume sections."""
    client = get_groq_client()
    if not client:
        return None, "GROQ_API_KEY is not configured. Please set it in your .env file."

    prompt = f"""
    You are an expert ATS resume writer. The user has provided messy text (an old resume, a LinkedIn profile, or a job description).
    Extract and organize the information into a highly professional format.
    
    Return EXACTLY a JSON object with the following keys, and nothing else:
    {{
        "summary": "A powerful 3-sentence professional summary.",
        "experience": "Format as: Job Title @ Company (Years)\\n• Bullet point 1\\n• Bullet point 2",
        "education": "Format as: Degree\\nUniversity (Years)",
        "skills": "Comma separated list of technical skills",
        "soft_skills": "Comma separated list of soft skills"
    }}
    
    User Text:
    {raw_text}
    """

    try:
        completion = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        response_json = completion.choices[0].message.content
        return json.loads(response_json), None
    except Exception as e:
        return None, str(e)

def analyze_ats_match(resume_text, job_description):
    """Compares resume text with target Job Description (JD) and returns ATS score, matched keywords, missing keywords, and recommendations."""
    client = get_groq_client()
    if not client:
        return None, "GROQ_API_KEY is not configured. Please set it in your .env file."

    prompt = f"""
    You are an enterprise Applicant Tracking System (ATS) auditor and senior technical recruiter.
    Analyze the following Candidate Resume against the target Job Description (JD).
    
    Calculate an accurate ATS Match Score (0 to 100) based on:
    1. Keyword match (skills, tools, frameworks)
    2. Role relevance and seniority alignment
    3. Quantifiable achievements and experience impact
    
    Return EXACTLY a JSON object with these exact keys:
    {{
        "score": 85,
        "summary": "Brief 2-sentence summary of candidate fit for this specific job.",
        "matched_keywords": ["list", "of", "matching", "skills", "found", "in", "both"],
        "missing_keywords": ["critical", "keywords", "from", "JD", "missing", "in", "resume"],
        "recommendations": [
            "Actionable suggestion 1 to improve ATS score",
            "Actionable suggestion 2 to improve ATS score",
            "Actionable suggestion 3 to improve ATS score"
        ]
    }}
    
    Candidate Resume Data:
    {resume_text}
    
    Target Job Description:
    {job_description}
    """

    try:
        completion = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        response_json = completion.choices[0].message.content
        return json.loads(response_json), None
    except Exception as e:
        return None, str(e)
