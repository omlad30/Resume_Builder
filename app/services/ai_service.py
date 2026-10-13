import os
import re
import json
from flask import current_app

def get_groq_client():
    api_key = current_app.config.get('GROQ_API_KEY', '').strip()
    if not api_key:
        return None
    try:
        from groq import Groq
        return Groq(api_key=api_key)
    except Exception:
        return None

def smart_extract_resume(raw_text):
    """
    Intelligent local NLP & regex extractor for unstructured resume text.
    Extracts all fields without requiring external API calls.
    """
    text = raw_text.replace('\r\n', '\n').replace('\r', '\n')
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return {
            "full_name": "", "target_job": "", "email": "", "phone": "",
            "location": "", "linkedin": "", "github": "", "summary": "",
            "education": "", "experience": "", "projects": "", "certifications": "",
            "skills": "", "soft_skills": ""
        }

    # 1. Contact and Header Extraction
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    email = email_match.group(0) if email_match else ""

    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}|\+91[\s-]?[6-9]\d{9}|[6-9]\d{9}', text)
    phone = phone_match.group(0).strip() if phone_match else ""

    linkedin_match = re.search(r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/([a-zA-Z0-9\-_%]+)', text, re.I)
    linkedin = f"linkedin.com/in/{linkedin_match.group(1)}" if linkedin_match else ""

    github_match = re.search(r'(?:https?:\/\/)?(?:www\.)?github\.com\/([a-zA-Z0-9\-_%]+)', text, re.I)
    github = f"github.com/{github_match.group(1)}" if github_match else ""

    portfolio_match = re.search(r'([a-zA-Z0-9\-_]+\.github\.io)', text, re.I)
    portfolio = portfolio_match.group(1) if portfolio_match else ""
    if portfolio and not github:
        github = portfolio

    # Location heuristic (e.g. City, State or City, State PIN)
    loc_match = re.search(r'([A-Z][a-zA-Z\s]+,\s*[A-Z][a-zA-Z\s]+(?:\s*\d{6})?)', text)
    location = ""
    if loc_match:
        cand = loc_match.group(1).strip()
        # Avoid matching degrees or company names
        if not re.search(r'bachelor|master|engineering|university|college|technologies|stack', cand, re.I):
            location = cand

    # Candidate Name & Target Job from header lines (lines before any section header)
    section_keywords = [
        'professional summary', 'summary', 'profile', 'about me', 'objective',
        'education', 'technical skills', 'skills', 'projects', 'key projects',
        'internships', 'experience', 'work experience', 'employment',
        'certifications', 'certifications and achievements', 'achievements',
        'soft skills', 'interests', 'extracurricular'
    ]

    header_lines = []
    for line in lines[:8]:
        line_lower = line.lower().strip()
        # strip markdown or underlines
        clean_lower = re.sub(r'^[#*_\-\s]+|[#*_\-\s]+$', '', line_lower)
        if any(clean_lower == kw or clean_lower.startswith(f"{kw}:") for kw in section_keywords):
            break
        header_lines.append(line)

    full_name = ""
    target_job = ""

    for h_line in header_lines:
        # Check if line contains contact info
        if '@' in h_line or 'http' in h_line or 'linkedin' in h_line or 'github' in h_line or re.search(r'\d{5,}', h_line):
            continue
        cleaned = re.sub(r'[|•*#]', '', h_line).strip()
        if not full_name and len(cleaned.split()) <= 4 and re.match(r'^[A-Za-z\s\.\']+$', cleaned):
            full_name = cleaned
        elif full_name and not target_job and len(cleaned.split()) <= 5:
            # Common job titles
            target_job = cleaned

    if not full_name and lines:
        first = lines[0].split('|')[0].strip()
        full_name = re.sub(r'[#*]', '', first).strip()

    # 2. Section Parsing
    # Identify line indices where sections start
    section_markers = []
    section_patterns = [
        ('summary', r'^(?:#+\s*)?(?:professional\s+summary|summary|profile|about\s+me|career\s+objective)'),
        ('education', r'^(?:#+\s*)?(?:education|academic\s+background|qualifications)'),
        ('skills', r'^(?:#+\s*)?(?:technical\s+skills|skills|technologies|core\s+competencies)'),
        ('projects', r'^(?:#+\s*)?(?:projects|key\s+projects|academic\s+projects)'),
        ('experience', r'^(?:#+\s*)?(?:internships|experience|work\s+experience|employment\s+history)'),
        ('certifications', r'^(?:#+\s*)?(?:certifications\s+and\s+achievements|certifications|achievements|courses|honors)'),
        ('soft_skills', r'^(?:#+\s*)?(?:soft\s+skills|interpersonal\s+skills)')
    ]

    for idx, line in enumerate(lines):
        clean_line = re.sub(r'^[#*_\-\s]+|[#*_\-\s]+$', '', line).lower()
        for sec_name, pattern in section_patterns:
            if re.match(pattern, clean_line):
                section_markers.append((idx, sec_name))
                break

    # Group text into sections
    sections = {
        'summary': [],
        'education': [],
        'skills': [],
        'projects': [],
        'experience': [],
        'certifications': [],
        'soft_skills': []
    }

    for i, (start_idx, sec_name) in enumerate(section_markers):
        end_idx = section_markers[i + 1][0] if i + 1 < len(section_markers) else len(lines)
        # Content lines exclude the header itself
        sec_lines = lines[start_idx + 1:end_idx]
        sections[sec_name].extend(sec_lines)

    # Clean and format bullets in sections
    def clean_section_text(sec_list):
        cleaned = []
        for l in sec_list:
            # Normalize bullet points
            normalized = re.sub(r'^[\s\x95\u2022\*\-]+\s*', '• ', l)
            cleaned.append(normalized)
        return '\n'.join(cleaned).strip()

    summary_text = clean_section_text(sections['summary'])
    education_text = clean_section_text(sections['education'])
    skills_text = clean_section_text(sections['skills'])
    projects_text = clean_section_text(sections['projects'])
    experience_text = clean_section_text(sections['experience'])
    certifications_text = clean_section_text(sections['certifications'])
    soft_skills_text = clean_section_text(sections['soft_skills'])

    # If soft skills are embedded in skills section
    if not soft_skills_text and 'soft skills:' in skills_text.lower():
        parts = re.split(r'soft\s+skills:\s*', skills_text, flags=re.I)
        if len(parts) > 1:
            skills_text = parts[0].strip()
            soft_skills_text = parts[1].strip()

    # Format soft skills as clean pipe or comma list
    if soft_skills_text:
        soft_skills_text = re.sub(r'[•*\n]+', ' | ', soft_skills_text).strip(' |')

    return {
        "full_name": full_name,
        "target_job": target_job,
        "email": email,
        "phone": phone,
        "location": location,
        "linkedin": linkedin,
        "github": github,
        "summary": summary_text,
        "education": education_text,
        "experience": experience_text,
        "projects": projects_text,
        "certifications": certifications_text,
        "skills": skills_text,
        "soft_skills": soft_skills_text
    }

def generate_resume_from_raw_text(raw_text):
    """
    Extracts and organizes unformatted text into ATS resume sections.
    First tries Groq LLM if configured; seamlessly falls back to smart local extraction.
    """
    if not raw_text or not raw_text.strip():
        return None, "No text provided. Please provide text to analyze."

    client = get_groq_client()
    if client:
        prompt = f"""
        You are an elite ATS resume architect. Extract all candidate information from the text below into clean, professional resume sections.
        Return ONLY a JSON object with EXACTLY the following keys:
        {{
            "full_name": "Full name of the candidate",
            "target_job": "Target job title or primary role",
            "email": "Email address",
            "phone": "Phone number with country code if available",
            "location": "City, State, Postal code",
            "linkedin": "LinkedIn profile URL or handle",
            "github": "GitHub / Portfolio link",
            "summary": "Compelling 2-4 sentence professional summary",
            "education": "Format with degree and dates on first line, institute and CGPA on next line",
            "experience": "Format work experience/internships with title, company, dates, and bullet points",
            "projects": "Format projects with Title, Tech Stack, and indented bullet points (• )",
            "certifications": "List of certifications and hackathon achievements (one per line with • )",
            "skills": "Categorized technical skills (e.g. Programming Languages: ..., Web Technologies: ...)",
            "soft_skills": "Comma or pipe separated list of key soft skills"
        }}

        Raw Resume Text:
        {raw_text}
        """

        # Try Groq supported models
        models_to_try = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
        for model_name in models_to_try:
            try:
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                response_json = completion.choices[0].message.content
                data = json.loads(response_json)
                # Merge with local regex for contact fields if model left them blank
                local_fallback = smart_extract_resume(raw_text)
                for field in ['full_name', 'email', 'phone', 'linkedin', 'github', 'location']:
                    if not data.get(field) and local_fallback.get(field):
                        data[field] = local_fallback[field]
                return data, None
            except Exception as e:
                # If model or API error, try next or fall through to smart extractor
                continue

    # Fallback to local intelligent parser
    local_data = smart_extract_resume(raw_text)
    return local_data, None

def analyze_ats_match(resume_text, job_description):
    """
    Compares resume text with target Job Description (JD) and returns ATS score,
    matched keywords, missing keywords, and recommendations.
    Uses Groq LLM if configured; otherwise performs robust local keyword analysis.
    """
    if not resume_text:
        return None, "Resume content is required for ATS audit."
    if not job_description:
        return None, "Target Job Description is required for ATS audit."

    client = get_groq_client()
    if client:
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

        models_to_try = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]
        for model_name in models_to_try:
            try:
                completion = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                response_json = completion.choices[0].message.content
                return json.loads(response_json), None
            except Exception:
                continue

    # Local Fallback ATS Keyword Audit Engine
    stop_words = {
        'the', 'and', 'for', 'with', 'that', 'this', 'from', 'have', 'are', 'was',
        'will', 'you', 'your', 'about', 'our', 'all', 'any', 'can', 'not', 'job',
        'requirements', 'skills', 'responsibilities', 'experience', 'years', 'working',
        'work', 'candidate', 'must', 'should', 'good', 'strong', 'ability', 'looking'
    }

    # Extract alphanumeric words/tokens from JD
    jd_tokens = set(re.findall(r'[a-zA-Z0-9\+#\.]+', job_description.lower()))
    resume_tokens = set(re.findall(r'[a-zA-Z0-9\+#\.]+', resume_text.lower()))

    # Known high-value technical keywords
    tech_pool = {
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
        'react', 'react.js', 'node', 'node.js', 'express', 'express.js', 'angular', 'vue',
        'django', 'flask', 'fastapi', 'spring', 'springboot', 'html', 'css', 'tailwind',
        'sql', 'mysql', 'postgresql', 'mongodb', 'firebase', 'redis', 'elasticsearch',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'git', 'github', 'ci/cd',
        'rest', 'api', 'graphql', 'microservices', 'dsa', 'algorithms', 'agile', 'scrum',
        'machine learning', 'deep learning', 'nlp', 'ai', 'gemini', 'llm', 'tensorflow', 'pytorch'
    }

    jd_tech = {w for w in tech_pool if re.search(r'\b' + re.escape(w) + r'\b', job_description.lower())}
    resume_tech = {w for w in tech_pool if re.search(r'\b' + re.escape(w) + r'\b', resume_text.lower())}

    if not jd_tech:
        # Fallback to general tokens if JD has no predefined tech
        jd_tech = {w for w in jd_tokens if len(w) > 3 and w not in stop_words}

    matched = sorted(list(jd_tech.intersection(resume_tech)))
    missing = sorted(list(jd_tech - resume_tech))

    match_ratio = (len(matched) / max(len(jd_tech), 1))
    score = min(95, max(45, int(match_ratio * 100)))

    # Actionable recommendations
    recommendations = []
    if missing:
        top_missing = ", ".join(missing[:4])
        recommendations.append(f"Add key JD requirements to Technical Skills & Experience: {top_missing}.")
    recommendations.append("Ensure every project bullet point starts with a strong action verb (e.g., Architected, Built, Optimized).")
    recommendations.append("Quantify your project results with measurable metrics (e.g., latency, percentage improvement, scale).")

    summary = f"Resume matches {len(matched)} key requirements from the target role with a match score of {score}%."

    return {
        "score": score,
        "summary": summary,
        "matched_keywords": matched[:12],
        "missing_keywords": missing[:12],
        "recommendations": recommendations
    }, None
