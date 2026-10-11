from app.models import Resume

def test_resume_creation_and_view(auth_client, app):
    """Test creating a resume and viewing it with a template."""
    res = auth_client.post('/', data={
        'full_name': 'Om Lad',
        'email': 'om@example.com',
        'target_job': 'Full Stack Developer',
        'template_choice': 'modern',
        'phone': '+91 99999 88888',
        'location': 'Mumbai, India',
        'linkedin': 'https://linkedin.com/in/omlad',
        'github': 'https://github.com/omlad',
        'summary': 'Experienced developer passionate about Python and React.',
        'education': 'B.Tech Computer Science\nXYZ University (2020-2024)',
        'experience': 'Software Engineer @ TechCorp (2024-Present)\n• Built scalable APIs',
        'skills': 'Python, Flask, JavaScript, SQL',
        'soft_skills': 'Communication, Leadership',
        'has_soft_skills': 'on'
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b'Om Lad' in res.data
    assert b'Full Stack Developer' in res.data

def test_preview_resume(client):
    """Test live preview without authentication and without saving to DB."""
    res = client.post('/preview_resume', data={
        'full_name': 'Live Preview User',
        'email': 'preview@example.com',
        'target_job': 'AI Engineer',
        'template': 'minimalist',
        'skills': 'Python, PyTorch, Groq'
    })
    assert res.status_code == 200
    assert b'Live Preview User' in res.data
    assert b'AI Engineer' in res.data

def test_delete_resume(auth_client, app):
    """Test deleting a user-owned resume."""
    with app.app_context():
        resume = Resume(
            user_id=1,
            full_name='Delete Candidate',
            email='del@example.com',
            target_job='Tester',
            template_choice='classic'
        )
        db_session = app.extensions['sqlalchemy'].session
        db_session.add(resume)
        db_session.commit()
        resume_id = resume.id

    res = auth_client.post(f'/delete_resume/{resume_id}', follow_redirects=True)
    assert res.status_code == 200
    with app.app_context():
        assert Resume.query.get(resume_id) is None

def test_ats_api_validation(client):
    """Test ATS score endpoint validation rules."""
    # Missing both fields
    res = client.post('/api/ats_score', json={})
    assert res.status_code == 400
    assert b'Resume content is required' in res.data

    # Missing job description
    res_no_jd = client.post('/api/ats_score', json={'resume_text': 'Python, SQL'})
    assert res_no_jd.status_code == 400
    assert b'Job Description is required' in res_no_jd.data

def test_ai_generate_validation(client):
    """Test AI resume generator validation."""
    res = client.post('/api/generate_resume', json={})
    assert res.status_code == 400
    assert b'No text provided' in res.data
