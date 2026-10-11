from flask import Blueprint, request, jsonify
from app.extensions import csrf, limiter
from app.services.ai_service import generate_resume_from_raw_text, analyze_ats_match

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/generate_resume', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per minute")
def generate_resume():
    """Extract and structure resume fields from unformatted text."""
    data = request.json or {}
    raw_text = data.get('raw_text', '').strip()

    if not raw_text:
        return jsonify({'error': 'No text provided. Please provide text to analyze.'}), 400

    result, error = generate_resume_from_raw_text(raw_text)
    if error:
        return jsonify({'error': error}), 400 if 'GROQ_API_KEY' in error else 500

    return jsonify(result)

@api_bp.route('/ats_score', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per minute")
def ats_score():
    """Analyze resume text against job description for ATS score, keywords, and recommendations."""
    data = request.json or {}
    resume_text = data.get('resume_text', '').strip()
    job_description = data.get('job_description', '').strip()

    if not resume_text:
        return jsonify({'error': 'Resume content is required for ATS audit.'}), 400

    if not job_description:
        return jsonify({'error': 'Target Job Description is required for ATS audit.'}), 400

    result, error = analyze_ats_match(resume_text, job_description)
    if error:
        return jsonify({'error': error}), 400 if 'GROQ_API_KEY' in error else 500

    return jsonify(result)
