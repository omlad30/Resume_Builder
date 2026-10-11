from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, limiter
from app.models import User
from app.forms import SignupForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from app.services.email_service import send_reset_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('resumes.dashboard'))
    form = SignupForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        email = form.email.data.strip().lower()
        password = form.password.data

        if User.query.filter_by(email=email).first():
            flash('This email address is already registered. Please log in.', 'error')
            return redirect(url_for('auth.signup'))

        new_user = User(name=name, email=email, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash('Welcome to ProResume! Your account has been created.', 'success')
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('resumes.dashboard'))

    return render_template('signup.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("15 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('resumes.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('resumes.dashboard'))

        flash('Invalid email or password. Please try again.', 'error')

    return render_template('login.html', form=form)

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('resumes.dashboard'))
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()

        if user:
            token = user.get_reset_token(expires_sec=1800)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            send_reset_email(user.email, reset_url)

        flash('If an account matches that email, a password reset link has been sent.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('resumes.dashboard'))
    user = User.verify_reset_token(token, expires_sec=1800)
    if not user:
        flash('The password reset link is invalid or has expired.', 'error')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password_hash = generate_password_hash(form.password.data)
        db.session.commit()
        flash('Your password has been successfully updated! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('resumes.home'))
