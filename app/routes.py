from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from .models import User, DailyRecommendationSet
from . import db
from datetime import date

bp = Blueprint('routes', __name__, template_folder='templates')

@bp.route('/')
def index():
    if current_user.is_authenticated:
        if not current_user.onboarding_completed:
            return redirect(url_for('routes.onboarding'))
        return redirect(url_for('routes.daily_view'))
    return render_template('welcome.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('routes.register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('routes.register'))
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('routes.onboarding'))
    
    return render_template('register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']
        
        user = User.query.filter(
            or_(User.username == identifier, User.email == identifier)
        ).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if not user.onboarding_completed:
                return redirect(url_for('routes.onboarding'))
            return redirect(url_for('routes.daily_view'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.index'))

@bp.route('/onboarding')
@login_required
def onboarding():
    if current_user.onboarding_completed:
        return redirect(url_for('routes.daily_view'))
    return render_template('onboarding.html')

@bp.route('/daily')
@login_required
def daily_view():
    if not current_user.onboarding_completed:
        return redirect(url_for('routes.onboarding'))
    
    today = date.today()
    daily_set = DailyRecommendationSet.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()
    
    return render_template('daily.html', daily_set=daily_set)
