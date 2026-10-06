from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/resume_builder_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024  # 3 MB max limit
db = SQLAlchemy(app)

# --- DATABASE MODEL ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    target_job = db.Column(db.String(100))
    template_choice = db.Column(db.String(50), default="classic")
    phone = db.Column(db.String(20))
    location = db.Column(db.String(100))
    linkedin = db.Column(db.String(100))
    github = db.Column(db.String(100))
    summary = db.Column(db.Text)
    education = db.Column(db.Text)
    experience = db.Column(db.Text)
    skills = db.Column(db.Text)
    soft_skills = db.Column(db.Text)
    profile_pic = db.Column(db.String(255)) # Path to uploaded image

# --- ROUTES ---
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        form_name = request.form['full_name']
        form_email = request.form['email']
        form_job = request.form['target_job']
        form_template = request.form.get('template_choice', 'classic')
        
        # New Fields
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
        
        # Handle file upload
        pic_path = None
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                pic_path = filepath
        
        new_user = User(
            full_name=form_name, email=form_email, target_job=form_job, template_choice=form_template,
            phone=form_phone, location=form_location, linkedin=form_linkedin, github=form_github,
            summary=form_summary, education=form_education, experience=form_experience, skills=form_skills,
            soft_skills=form_soft_skills, profile_pic=pic_path
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(f'/resume/{new_user.id}')
        
        except Exception as e:
            return f"<h1 style='color: red;'>Error: That email is already registered!</h1><p>{e}</p>"

    return render_template('index.html')


@app.route('/resume/<int:user_id>')
def view_resume(user_id):
    user_data = User.query.get_or_404(user_id)
    
    template_map = {
        'classic': 'resume_classic.html',
        'modern': 'resume_modern.html',
        'minimalist': 'resume_minimalist.html',
        'creative': 'resume_creative.html',
        'photo': 'resume_photo.html'
    }
    
    template_name = template_map.get(user_data.template_choice, 'resume_classic.html')
    return render_template(template_name, user=user_data)

# --- START THE SERVER ---
if __name__ == '__main__':
    with app.app_context():
        db.drop_all() 
        db.create_all()
    app.run(debug=True)
