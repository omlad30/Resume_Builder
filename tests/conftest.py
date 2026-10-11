import pytest
from app import create_app
from app.config import Config
from app.extensions import db
from app.models import User, Resume

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # Disable CSRF in tests for clean form submissions
    SERVER_NAME = 'localhost'

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client, app):
    with app.app_context():
        user = User(name="Test Candidate", email="candidate@test.com", password_hash="dummy")
        from werkzeug.security import generate_password_hash
        user.password_hash = generate_password_hash("password123")
        db.session.add(user)
        db.session.commit()
    
    # Log in
    client.post('/login', data={'email': 'candidate@test.com', 'password': 'password123'}, follow_redirects=True)
    return client
