from app.models import User

def test_signup(client, app):
    """Test user registration."""
    res = client.post('/signup', data={
        'name': 'Rahul Sharma',
        'email': 'rahul@test.com',
        'password': 'strongpassword123'
    }, follow_redirects=True)
    assert res.status_code == 200
    with app.app_context():
        user = User.query.filter_by(email='rahul@test.com').first()
        assert user is not None
        assert user.name == 'Rahul Sharma'

def test_signup_duplicate_email(client):
    """Test user registration prevents duplicate email."""
    # Register first user
    client.post('/signup', data={'name': 'User 1', 'email': 'dup@test.com', 'password': 'pass12345'})
    # Logout before second signup
    client.get('/logout')
    
    # Register duplicate email
    res = client.post('/signup', data={'name': 'User 2', 'email': 'dup@test.com', 'password': 'pass12345'}, follow_redirects=True)
    assert b'already registered' in res.data

def test_login_logout(client):
    """Test login with valid credentials and logout."""
    client.post('/signup', data={'name': 'Login User', 'email': 'login@test.com', 'password': 'loginpass123'})
    client.get('/logout')
    
    # Valid login
    res = client.post('/login', data={'email': 'login@test.com', 'password': 'loginpass123'}, follow_redirects=True)
    assert res.status_code == 200
    assert b'Welcome, Login User!' in res.data or b'Dashboard' in res.data

    # Logout
    res_logout = client.get('/logout', follow_redirects=True)
    assert res_logout.status_code == 200

def test_login_invalid_password(client):
    """Test login with wrong password."""
    client.post('/signup', data={'name': 'Valid User', 'email': 'valid@test.com', 'password': 'correctpass'})
    client.get('/logout')
    
    res = client.post('/login', data={'email': 'valid@test.com', 'password': 'wrongpass'}, follow_redirects=True)
    assert b'Invalid email or password' in res.data

def test_password_reset_token_flow(client, app):
    """Test generating reset token and updating password."""
    client.post('/signup', data={'name': 'Reset User', 'email': 'reset@test.com', 'password': 'oldpassword123'})
    client.get('/logout')
    
    # Forgot password request
    res_forgot = client.post('/forgot_password', data={'email': 'reset@test.com'}, follow_redirects=True)
    assert res_forgot.status_code == 200
    assert b'password reset link has been sent' in res_forgot.data

    with app.app_context():
        user = User.query.filter_by(email='reset@test.com').first()
        token = user.get_reset_token()
    
    # Reset password with valid token
    res_reset = client.post(f'/reset_password/{token}', data={
        'password': 'newpassword123',
        'confirm_password': 'newpassword123'
    }, follow_redirects=True)
    assert res_reset.status_code == 200
    assert b'successfully updated' in res_reset.data
