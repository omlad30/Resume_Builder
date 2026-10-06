from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:root@localhost/resume_builder_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- DATABASE MODEL ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    target_job = db.Column(db.String(100))
    template_choice = db.Column(db.String(50), default="classic")

# --- ROUTES ---
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        form_name = request.form['full_name']
        form_email = request.form['email']
        form_job = request.form['target_job']
        form_template = request.form.get('template_choice', 'classic')
        
        new_user = User(full_name=form_name, email=form_email, target_job=form_job, template_choice=form_template)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(f'/resume/{new_user.id}')
        
        except Exception as e:
            return "<h1 style='color: red;'>Error: That email is already registered!</h1>"

    return render_template('index.html')


@app.route('/resume/<int:user_id>')
def view_resume(user_id):
    user_data = User.query.get_or_404(user_id)
    
    if user_data.template_choice == 'modern':
        return render_template('resume_modern.html', user=user_data)
    else:
        return render_template('resume.html', user=user_data)


# --- START THE SERVER ---
if __name__ == '__main__':
    with app.app_context():
        db.drop_all() 
        db.create_all()
    app.run(debug=True)
