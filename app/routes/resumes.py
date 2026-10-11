import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db, csrf
from app.models import Resume

resumes_bp = Blueprint('resumes', __name__)

@resumes_bp.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        form_name = request.form.get('full_name', '')
        form_email = request.form.get('email', '')
        form_job = request.form.get('target_job', '')
        form_template = request.form.get('template_choice', 'classic')
        form_phone = request.form.get('phone', '')
        form_location = request.form.get('location', '')
        form_linkedin = request.form.get('linkedin', '')
        form_github = request.form.get('github', '')
        form_summary = request.form.get('summary', '')
        form_education = request.form.get('education', '')
        form_experience = request.form.get('experience', '')
        form_skills = request.form.get('skills', '')
        
        has_soft_skills = request.form.get('has_soft_skills')
        form_soft_skills = request.form.get('soft_skills', '') if has_soft_skills else ''

        pic_path = None
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                pic_path = os.path.join('static', 'uploads', filename).replace('\\', '/')

        new_resume = Resume(
            user_id=current_user.id if current_user.is_authenticated else None,
            full_name=form_name, email=form_email, target_job=form_job, template_choice=form_template,
            phone=form_phone, location=form_location, linkedin=form_linkedin, github=form_github,
            summary=form_summary, education=form_education, experience=form_experience, skills=form_skills,
            soft_skills=form_soft_skills, profile_pic=pic_path
        )

        try:
            db.session.add(new_resume)
            db.session.commit()
            return redirect(url_for('resumes.view_resume', resume_id=new_resume.id))
        except Exception as e:
            flash(f"Error saving resume: {e}", "error")

    return render_template('index.html')

@resumes_bp.route('/dashboard')
@login_required
def dashboard():
    user_resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.id.desc()).all()
    return render_template('dashboard.html', resumes=user_resumes)

@resumes_bp.route('/resume/<int:resume_id>')
def view_resume(resume_id):
    user_data = Resume.query.get_or_404(resume_id)

    # Claim anonymous resume if user is authenticated
    if user_data.user_id is None and current_user.is_authenticated:
        user_data.user_id = current_user.id
        db.session.commit()

    # Security check for registered resumes
    if user_data.user_id and current_user.is_authenticated and user_data.user_id != current_user.id:
        return "<h1 style='color: red;'>Access Denied! You do not own this resume.</h1>", 403

    template_map = {
        'classic': 'resume_classic.html',
        'modern': 'resume_modern.html',
        'minimalist': 'resume_minimalist.html',
        'creative': 'resume_creative.html',
        'photo': 'resume_photo.html'
    }
    template_name = template_map.get(user_data.template_choice, 'resume_classic.html')
    return render_template(template_name, user=user_data)

@resumes_bp.route('/edit_resume/<int:resume_id>', methods=['GET', 'POST'])
@login_required
def edit_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        return "Unauthorized", 403

    if request.method == 'POST':
        resume.full_name = request.form.get('full_name', '')
        resume.email = request.form.get('email', '')
        resume.target_job = request.form.get('target_job', '')
        resume.template_choice = request.form.get('template_choice', 'classic')
        resume.phone = request.form.get('phone', '')
        resume.location = request.form.get('location', '')
        resume.linkedin = request.form.get('linkedin', '')
        resume.github = request.form.get('github', '')
        resume.summary = request.form.get('summary', '')
        resume.education = request.form.get('education', '')
        resume.experience = request.form.get('experience', '')
        resume.skills = request.form.get('skills', '')
        
        has_soft_skills = request.form.get('has_soft_skills')
        resume.soft_skills = request.form.get('soft_skills', '') if has_soft_skills else ''

        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                resume.profile_pic = os.path.join('static', 'uploads', filename).replace('\\', '/')

        db.session.commit()
        flash("Resume updated successfully!", "success")
        return redirect(url_for('resumes.view_resume', resume_id=resume.id))

    return render_template('index.html', resume=resume)

@resumes_bp.route('/delete_resume/<int:resume_id>', methods=['POST'])
@login_required
def delete_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        return "Unauthorized", 403
    db.session.delete(resume)
    db.session.commit()
    flash("Resume deleted successfully.", "success")
    return redirect(url_for('resumes.dashboard'))

@resumes_bp.route('/preview_resume', methods=['POST'])
@csrf.exempt
def preview_resume():
    user_data = {
        'full_name': request.form.get('full_name', 'Your Name'),
        'email': request.form.get('email', 'you@example.com'),
        'target_job': request.form.get('target_job', 'Target Job'),
        'phone': request.form.get('phone', ''),
        'location': request.form.get('location', ''),
        'linkedin': request.form.get('linkedin', ''),
        'github': request.form.get('github', ''),
        'summary': request.form.get('summary', ''),
        'education': request.form.get('education', ''),
        'experience': request.form.get('experience', ''),
        'skills': request.form.get('skills', ''),
        'soft_skills': request.form.get('soft_skills', ''),
        'template_choice': request.form.get('template', 'classic')
    }

    class MockUser:
        def __init__(self, **entries):
            self.__dict__.update(entries)

    mock_user = MockUser(**user_data)
    template_map = {
        'classic': 'resume_classic.html',
        'modern': 'resume_modern.html',
        'minimalist': 'resume_minimalist.html',
        'creative': 'resume_creative.html',
        'photo': 'resume_photo.html'
    }
    template_name = template_map.get(user_data['template_choice'], 'resume_classic.html')
    return render_template(template_name, user=mock_user)
