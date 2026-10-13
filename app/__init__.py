import os
from flask import Flask
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

from app.config import Config
from app.extensions import db, login_manager, csrf, limiter

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config_class)

    # Initialize upload folder
    upload_folder = os.path.join(app.root_path, '..', 'static', 'uploads')
    app.config['UPLOAD_FOLDER'] = os.path.abspath(upload_folder)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize Flask Extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.resumes import resumes_bp
    from app.routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(resumes_bp)
    app.register_blueprint(api_bp)

    # Register Jinja Filters for Structured Resume Layout
    from app.services.formatters import parse_education, parse_experience, parse_projects, parse_skills, clean_bullets
    app.jinja_env.filters['parse_education'] = parse_education
    app.jinja_env.filters['parse_experience'] = parse_experience
    app.jinja_env.filters['parse_projects'] = parse_projects
    app.jinja_env.filters['parse_skills'] = parse_skills
    app.jinja_env.filters['clean_bullets'] = clean_bullets

    return app
