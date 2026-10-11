# ✨ ProResume Builder

An AI-powered, highly professional Resume Builder web application built with **Python (Flask)**, **SQLAlchemy**, and **Tailwind CSS**. 

ProResume allows users to generate beautiful, ATS-optimized resumes in seconds. Users can fill out a clean web form, optionally upload a profile picture, or use the **AI Assistant** (powered by Groq) to convert raw unstructured text into polished resume sections. Choose from 5 premium templates and export pixel-perfect PDFs instantly.

## 🚀 Features

- **5 Premium Templates:**
  - 📄 **Classic:** Traditional, ultra-clean, and highly ATS-friendly.
  - 💼 **Modern:** Sleek 2-column layout with bold accents.
  - ✨ **Minimalist:** Elegant typography focusing on whitespace and readability.
  - 🎨 **Creative:** Vibrant gradient headers and modern badges.
  - 📸 **Photo ATS:** A modern layout that seamlessly integrates a user profile photo.
- **⚡ AI Resume Generator:** Powered by **Groq (`qwen/qwen3.8-27b`)** to parse rough summaries or job histories into ATS-optimized bullet points, summaries, and skills.
- **📥 Direct PDF Export:** Integrated `html2pdf.js` for 1-click client-side PDF downloads, alongside browser print support.
- **🔒 Authentication & Dashboard:** User registration, login, and private dashboard to manage, edit, and re-download saved resumes.
- **📁 Image Uploads:** Secure backend file handling for profile pictures (up to 3MB).
- **💾 Flexible Database:** Defaults to zero-setup **SQLite** out of the box, with full support for **MySQL** via `.env`.

## 🛠️ Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login
- **AI Engine:** Groq API (`qwen/qwen3.8-27b`)
- **Database:** SQLite (default) or MySQL
- **Frontend:** HTML5, Tailwind CSS, FontAwesome, Google Fonts, `html2pdf.js`
- **Environment Management:** `python-dotenv`

## 💻 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/resume_builder.git
   cd resume_builder
   ```

2. **Activate your virtual environment:**
   ```bash
   # On Windows
   .\venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to add your keys:
   ```env
   # Leave blank to use SQLite, or set your MySQL URI
   DATABASE_URL=sqlite:///resume_builder.db

   # (Optional) Get a free Groq API key from https://console.groq.com
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **View the app:**
   Open your browser and navigate to `http://127.0.0.1:5000/`.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!

## 📝 License
This project is open-source and available under the [MIT License](LICENSE).

