from wsgi import app

# Backwards compatibility: Allows running 'python app.py' directly as before
if __name__ == '__main__':
    from app.extensions import db
    with app.app_context():
        db.create_all()
    app.run(debug=True)
