from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
# We tell Flask how to log into your MySQL server
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/resume_builder_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database tool
db = SQLAlchemy(app)

# --- DATABASE TABLES (MODELS) ---
# This creates the 'user' table in MySQL automatically
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    target_job = db.Column(db.String(100)) # e.g., "Junior Python Developer"

# --- ROUTES ---
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    # This magic block creates the tables in MySQL before the server starts!
    with app.app_context():
        db.create_all()
        
    app.run(debug=True)
