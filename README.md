# ✨ ProResume Builder

An AI-ready, highly professional Resume Builder web application built with **Python (Flask)**, **SQLAlchemy**, and **Tailwind CSS**. 

ProResume allows users to generate beautiful, ATS-optimized resumes in seconds. Users simply fill out a clean, responsive web form, optionally upload a profile picture, and choose from 5 premium design templates. The backend instantly generates a pixel-perfect HTML resume that can be downloaded as a high-quality PDF.

## 🚀 Features

- **5 Premium Templates:**
  - 📄 **Classic:** Traditional, ultra-clean, and highly ATS-friendly.
  - 💼 **Modern:** Sleek 2-column layout with bold accents.
  - ✨ **Minimalist:** Elegant typography focusing on whitespace and readability.
  - 🎨 **Creative:** Vibrant gradient headers and modern badges.
  - 📸 **Photo ATS:** A modern layout that seamlessly integrates a user profile photo.
- **Image Uploads:** Secure backend file handling for profile pictures (up to 3MB).
- **Responsive UI:** A stunning Glassmorphism landing page that looks perfect on both mobile and desktop.
- **Dynamic Content:** Automatically formats multi-line text (for Education and Experience) and generates skill badges.
- **AI-Ready:** UI foundation laid out for Google Gemini AI integration to auto-generate professional summaries.

## 🛠️ Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy
- **Database:** MySQL
- **Frontend:** HTML5, Tailwind CSS, FontAwesome, Google Fonts
- **File Handling:** Werkzeug

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
   ```

3. **Install dependencies:**
   Make sure you have Flask, SQLAlchemy, and MySQL-Connector installed.
   ```bash
   pip install Flask Flask-SQLAlchemy mysql-connector-python Werkzeug
   ```

4. **Set up the database:**
   Ensure MySQL is running on your machine with a database named `resume_builder_db` (or update the URI in `app.py`). 

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
