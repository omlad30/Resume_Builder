from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from flask_sqlalchemy import SQLAlchemy

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from groq import Groq
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from itsdangerous import URLSafeTimedSerializer
from forms import SignupForm, LoginForm, ForgotPasswordForm, ResetPasswordForm

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# --- SECURITY & RATE LIMITING SETUP ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a_very_secret_key_for_sessions')
csrf = CSRFProtect(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["500 per hour"],
    storage_uri="memory://"
)

# --- EMAIL CONFIGURATION (SMTP) ---
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 'yes']
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', MAIL_USERNAME or 'noreply@proresume.com')

def send_reset_email(user_email, reset_url):
    """Sends real email via SMTP if credentials are configured; logs link as fallback."""
    subject = "ProResume - Password Reset Request"
    body = f"""Hello,

You requested a password reset for your ProResume account.
Click the following link to reset your password (valid for 30 minutes):

{reset_url}

If you did not request this, please ignore this email.

Best regards,
The ProResume Team
"""
    if MAIL_USERNAME and MAIL_PASSWORD:
        try:
            msg = MIMEMultipart()
            msg['From'] = MAIL_DEFAULT_SENDER
            msg['To'] = user_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT, timeout=10)
            if MAIL_USE_TLS:
                server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            print(f"[EMAIL SENT] Password reset sent to {user_email}")
            return True
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send email via SMTP: {e}")
            print(f"[FALLBACK RESET LINK]: {reset_url}")
            return False
    else:
        # Development fallback: Log link to console for immediate testing
        print("\n" + "="*60)
        print(" [LOCAL DEV] PASSWORD RESET LINK GENERATED:")
        print(f" User: {user_email}")
        print(f" URL:  {reset_url}")
        print("="*60 + "\n")
        return True

# --- GROQ AI SETUP ---
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '').strip()
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# --- DATABASE CONFIGURATION ---
# Flexible DB: Uses DATABASE_URL from .env, or falls back to SQLite for zero-setup local dev
db_url = os.environ.get('DATABASE_URL') or os.environ.get('SQLALCHEMY_DATABASE_URI')
if not db_url:
    db_url = 'sqlite:///resume_builder.db'
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024  # 3 MB max limit
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
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

    def get_reset_token(self, expires_sec=1800):
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt='password-reset-salt')

    @staticmethod
    def verify_reset_token(token, expires_sec=1800):
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token, salt='password-reset-salt', max_age=expires_sec)
        except Exception:
            return None
        user_id = data.get('user_id')
        return User.query.get(user_id) if user_id else None

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
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
@limiter.limit("10 per minute")
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = SignupForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        email = form.email.data.strip().lower()
        password = form.password.data

        if User.query.filter_by(email=email).first():
            flash('This email address is already registered. Please log in.', 'error')
            return redirect(url_for('signup'))

        new_user = User(name=name, email=email, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash('Welcome to ProResume! Your account has been created.', 'success')
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('dashboard'))

    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("15 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))

        flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html', form=form)

@app.route('/forgot_password', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()

        # Follow production security practice: Always show the same confirmation message
        # to prevent user enumeration attacks
        if user:
            token = user.get_reset_token(expires_sec=1800)
            reset_url = url_for('reset_password', token=token, _external=True)
            send_reset_email(user.email, reset_url)

        flash('If an account matches that email, a password reset link has been sent.', 'success')
        return redirect(url_for('login'))

    return render_template('forgot_password.html', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    user = User.verify_reset_token(token, expires_sec=1800)
    if not user:
        flash('The password reset link is invalid or has expired.', 'error')
        return redirect(url_for('forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password_hash = generate_password_hash(form.password.data)
        db.session.commit()
        flash('Your password has been successfully updated! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', form=form)

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

@app.route('/edit_resume/<int:resume_id>', methods=['GET', 'POST'])
@login_required
def edit_resume(resume_id):
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        return "Unauthorized", 403
        
    if request.method == 'POST':
        resume.full_name = request.form['full_name']
        resume.email = request.form['email']
        resume.target_job = request.form['target_job']
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
                from werkzeug.utils import secure_filename
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                resume.profile_pic = filepath
                
        db.session.commit()
        return redirect(f'/resume/{resume.id}')
        
    return render_template('index.html', resume=resume)


@app.route('/preview_resume', methods=['POST'])
@csrf.exempt
def preview_resume():
    # Similar to home() but doesn't save to DB
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
    
    # Mock an object for Jinja
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


# --- AI API ROUTE ---
@app.route('/api/generate_resume', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per minute")
def generate_resume():
    if not groq_client:
        return jsonify({
            'error': 'GROQ_API_KEY is not configured. Please add GROQ_API_KEY to your .env file to use the AI writer.'
        }), 400

    data = request.json
    raw_text = data.get('raw_text', '') if data else ''
    
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
        # db.drop_all() # Commented out to persist saved users and resumes across server restarts
        db.create_all()
    app.run(debug=True)
