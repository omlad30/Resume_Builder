from flask import Flask, render_template, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy

import os
import json
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from groq import Groq

app = Flask(__name__)

# --- GROQ AI SETUP ---
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
groq_client = Groq(api_key=GROQ_API_KEY)

# --- DATABASE CONFIGURATION ---
app.config['SECRET_KEY'] = 'a_very_secret_key_for_sessions'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/resume_builder_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024  # 3 MB max limit
db = SQLAlchemy(app)

# --- LOGIN SETUP ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- DATABASE MODELS ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    resumes = db.relationship('Resume', backref='owner', lazy=True)

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
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
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(email=email).first():
            return "<h1 style='color: red;'>Error: Email already registered!</h1><a href='/signup'>Go back</a>"
            
        new_user = User(name=name, email=email, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect('/dashboard')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect('/dashboard')
        return "<h1 style='color: red;'>Error: Invalid email or password!</h1><a href='/login'>Go back</a>"
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/dashboard')
@login_required
def dashboard():
    user_resumes = Resume.query.filter_by(user_id=current_user.id).order_by(Resume.id.desc()).all()
    return render_template('dashboard.html', resumes=user_resumes)

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
            return redirect(f'/resume/{new_resume.id}')
        
        except Exception as e:
            return f"<h1 style='color: red;'>Error Saving Resume!</h1><p>{e}</p>"

    return render_template('index.html')


@app.route('/resume/<int:resume_id>')
@login_required
def view_resume(resume_id):
    user_data = Resume.query.get_or_404(resume_id)
    
    # Claim anonymous resume
    if user_data.user_id is None:
        user_data.user_id = current_user.id
        db.session.commit()
        
    # Security check
    if user_data.user_id != current_user.id:
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

@app.route('/delete_resume/<int:resume_id>', methods=['POST'])
@login_required
def delete_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        return "Unauthorized", 403
    db.session.delete(resume)
    db.session.commit()
    return redirect(url_for('dashboard'))

# --- AI API ROUTE ---
@app.route('/api/generate_resume', methods=['POST'])
def generate_resume():
    data = request.json
    raw_text = data.get('raw_text', '')
    
    if not raw_text:
        return jsonify({'error': 'No text provided'}), 400
        
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
        completion = groq_client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        response_json = completion.choices[0].message.content
        return jsonify(json.loads(response_json))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- START THE SERVER ---
if __name__ == '__main__':
    with app.app_context():
        db.drop_all() 
        db.create_all()
    app.run(debug=True)
