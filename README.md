# ✨ ProResume Builder

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask%203.x-black.svg)](https://flask.palletsprojects.com/)
[![Groq AI](https://img.shields.io/badge/AI%20Engine-Groq%20Cloud-orange.svg)](https://groq.com/)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-38bdf8.svg)](https://tailwindcss.com/)
[![Tests](https://img.shields.io/badge/Tests-Pytest%20Passing-brightgreen.svg)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent, AI-powered full-stack resume builder and **ATS (Applicant Tracking System) Optimization Platform** built with **Python (Flask)**, **SQLAlchemy**, **Tailwind CSS**, and **Groq AI**.

ProResume empowers job seekers to transform unstructured rough notes, job histories, or messy resumes into clean, ATS-optimized, single-page resumes in seconds—with instant PDF exports, ATS keyword matching, and 5 hand-crafted professional templates.

---

## 🌟 Key Features

### ⚡ 1. AI Resume Extraction & Autofill
- **One-Click Parsing**: Paste rough summaries, raw LinkedIn text, or unformatted notes into the AI Assistant.
- **Groq AI Engine (`llama-3.3-70b-versatile` / `qwen/qwen3.8-27b`)**: Extracts and structures clean sections for contact details, summary, experience bullets, education, projects, technical skills, soft skills, and certifications.
- **Local Smart NLP Fallback**: Includes built-in regex and heuristic NLP fallback (`smart_extract_resume`) that functions seamlessly even without an API key or internet connection.

### 🎯 2. ATS Match Score & Job Description Matcher
- **Target Job Audit**: Paste any target job description alongside your resume text.
- **Match Percentage (0–100%)**: Evaluates role alignment, technical stack coverage, and soft skills match.
- **Keyword Gap Analysis**: Highlights keywords found and missing critical keywords to help your resume beat applicant tracking systems.
- **Actionable Feedback**: Delivers bulleted recommendations for tailoring your experience to the job posting.

### 🎨 3. 5 Tailored Resume Templates
- 📄 **Classic (Ivy League / ATS Standard)**: Traditional, compact single-page layout with serif typography (`Merriweather`), horizontal rules, and date alignments—tailored to score 100% on automated parsing.
- 💼 **Modern**: Contemporary 2-column sidebar layout with bold accents and categorized skill sections.
- ✨ **Minimalist**: Clean Scandinavian design focused on high-readability typography, white space, and subtle dividers.
- 🎨 **Creative**: Vibrant header gradient, badge pills, and modern tech styling for design and startup roles.
- 📸 **Photo ATS**: Incorporates a clean professional profile picture upload alongside an ATS-compliant structure.

### 📥 4. Client-Side & Print PDF Exports
- **1-Click PDF Download**: Powered by `html2pdf.js` with configured A4 margins and zero visual clipping.
- **Native Print-to-PDF**: Custom `@media print` CSS rules tailored for exact page breaks and clean browser PDF printing (`Ctrl + P`).
- **Live Preview & Floating Toolbar**: View, test, download, or edit resumes directly from the web interface.

### 🔒 5. Enterprise Security & Architecture
- **Application Factory Pattern**: Clean modular architecture separating `auth`, `resumes`, and `api` into Flask blueprints.
- **CSRF Protection**: Form integrity backed by `Flask-WTF` CSRF tokens.
- **Rate Limiting**: Protected against brute-force attacks and API abuse with `Flask-Limiter`.
- **Authentication & Password Recovery**: Secure password hashing (`Werkzeug`), session management (`Flask-Login`), and time-sensitive URL tokens (`itsdangerous`) with automatic fallback to terminal links for local testing.
- **Dual Database Support**: Zero-config **SQLite** default for instant setup, with seamless **MySQL** support via environment variables.
- **Automated Testing Suite**: Comprehensive unit and integration test suite using `pytest` covering authentication, password resets, and resume CRUD operations.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.10+, Flask 3.x, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Limiter |
| **AI / NLP** | Groq Cloud API, Custom Regex / Heuristic Parsers |
| **Frontend** | HTML5, Jinja2, Vanilla CSS & Tailwind CSS, FontAwesome, Google Fonts, `html2pdf.js` |
| **Database** | SQLite (Default / Zero-Config) or MySQL |
| **Security** | Werkzeug (`scrypt` / `pbkdf2`), CSRF Tokens, `itsdangerous` timed serializers |
| **Deployment** | Gunicorn, Procfile (Heroku / Render / Railway ready) |
| **Testing** | Pytest, AnyIO |

---

## 📁 Project Structure

```text
resume_builder/
├── app/
│   ├── __init__.py           # Application Factory (create_app)
│   ├── config.py             # Environment & database configuration
│   ├── extensions.py         # Initialized db, login_manager, csrf, limiter, mail
│   ├── forms/                # WTForms validation & CSRF models
│   ├── models/               # SQLAlchemy User and Resume models
│   ├── routes/
│   │   ├── api.py            # AI resume generator & ATS scoring endpoints
│   │   ├── auth.py           # Login, signup, password reset flow
│   │   └── resumes.py        # Dashboard, builder, preview, edit & delete
│   └── services/
│       ├── ai_service.py     # Groq API client & smart NLP extractor
│       ├── email_service.py  # Password reset mail delivery & console fallback
│       └── formatters.py     # Bullet cleaner, skill tagger & date parser
├── static/
│   ├── style.css             # Custom styles and print optimizations
│   └── uploads/              # User profile photo storage
├── templates/
│   ├── index.html            # Interactive builder form & ATS modal
│   ├── dashboard.html        # User resume management center
│   ├── resume_classic.html   # Ivy League ATS single-page template
│   ├── resume_modern.html    # 2-column sidebar template
│   ├── resume_minimalist.html# High-readability minimalist layout
│   ├── resume_creative.html  # Modern gradient tech template
│   ├── resume_photo.html     # Profile photo template
│   └── ...                   # Auth & password reset templates
├── tests/
│   ├── conftest.py           # Pytest fixtures & test application setup
│   ├── test_auth.py          # Auth & password reset test cases
│   └── test_resumes.py       # Resume creation, view, and deletion tests
├── .env.example              # Environment variable template
├── app.py                    # Local development runner
├── wsgi.py                   # Production WSGI entry point
├── Procfile                  # Cloud deployment configuration (Gunicorn)
└── requirements.txt          # Python dependencies
```

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.10+** installed on your system.
- *(Optional)* A free Groq API key from [Groq Console](https://console.groq.com) for AI parsing & ATS scoring.

### 2. Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/omlad30/Resume_Builder.git
   cd Resume_Builder
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # On Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\activate

   # On macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### 3. Environment Setup

Copy `.env.example` to create your local `.env`:
```bash
cp .env.example .env
```

Open `.env` and configure your settings:
```env
SECRET_KEY=your_random_secret_key_here

# Database URL: defaults to SQLite (zero setup)
DATABASE_URL=sqlite:///resume_builder.db

# Groq API Key (Optional for AI auto-extraction & ATS audits)
GROQ_API_KEY=gsk_your_groq_api_key_here

# (Optional) SMTP settings for password reset emails
# If left blank, password reset links print directly to your terminal!
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=
```

### 4. Running the Development Server

Start the application:
```bash
python app.py
```

Open your browser and visit:
```text
http://127.0.0.1:5000/
```

---

## 🧪 Running Automated Tests

Run the full test suite with `pytest`:
```bash
python -m pytest
```

All 12 tests will validate:
- User signup, duplicate email checks, and login authentication.
- Password reset token generation, expiration, and password update flow.
- Resume form submission, data persistence, and profile photo uploads.
- Dashboard authorization and resume deletion safety.

---

## ☁️ Deployment

The project includes a ready-to-use `Procfile` and `wsgi.py` for cloud platforms like **Render**, **Railway**, or **Heroku**:

```text
web: gunicorn wsgi:app
```

Set your environment variables (`SECRET_KEY`, `DATABASE_URL`, `GROQ_API_KEY`) in your cloud provider's dashboard, and the application will automatically initialize the database schema on launch.

---

## 🤝 Contributing

Contributions, feedback, and pull requests are warmly welcomed!
1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

Distributed under the **MIT License**. See `LICENSE` for more information.
