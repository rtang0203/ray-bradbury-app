# app.py - Main Flask application
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import os

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///literary_recommendations.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    onboarding_completed = db.Column(db.Boolean, default=False)
    adventurousness_level = db.Column(db.Float, default=0.5)  # 0-1 scale
    difficulty_preference = db.Column(db.String(20), default='intermediate')  # beginner/intermediate/advanced
    preferred_length = db.Column(db.String(20), default='medium')  # short/medium/long
    active = db.Column(db.Boolean, default=True)
    
    # Relationships
    preferences = db.relationship('UserPreference', backref='user', lazy=True)
    work_pools = db.relationship('UserWorkPool', backref='user', lazy=True)
    work_recommendations = db.relationship('WorkRecommendation', backref='user', lazy=True)
    daily_sets = db.relationship('DailyRecommendationSet', backref='user', lazy=True)

class UserPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    preference_type = db.Column(db.String(50), nullable=False)  # book/author/movie/director/artist/genre/topic
    preference_value = db.Column(db.String(200), nullable=False)
    weight = db.Column(db.Float, default=1.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)

class Work(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    work_type = db.Column(db.String(20), nullable=False)  # poem/short_story/essay
    content_url = db.Column(db.String(500))
    summary = db.Column(db.Text)
    estimated_reading_time = db.Column(db.Integer)  # minutes
    difficulty_level = db.Column(db.String(20))  # beginner/intermediate/advanced
    genres = db.Column(db.String(200))  # comma-separated
    themes = db.Column(db.String(200))  # comma-separated
    publication_year = db.Column(db.Integer)
    public_domain = db.Column(db.Boolean, default=True)
    word_count = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    active = db.Column(db.Boolean, default=True)
    
    # Relationships
    work_pools = db.relationship('UserWorkPool', backref='work', lazy=True)
    work_recommendations = db.relationship('WorkRecommendation', backref='work', lazy=True)

class UserWorkPool(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    work_id = db.Column(db.Integer, db.ForeignKey('work.id'), nullable=False)
    work_type = db.Column(db.String(20), nullable=False)  # poem/short_story/essay
    confidence_score = db.Column(db.Float, nullable=False)  # 0-1 scale
    added_reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='available')  # available/recommended/exhausted
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_recommended_at = db.Column(db.DateTime)
    times_recommended = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)

class WorkRecommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    work_id = db.Column(db.Integer, db.ForeignKey('work.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    reasoning = db.Column(db.Text)
    status = db.Column(db.String(20), default='unread')  # unread/in_progress/completed
    rating = db.Column(db.Integer)  # 1-5, nullable until completed
    feedback = db.Column(db.Text)
    recommended_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class DailyRecommendationSet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    poem_recommendation_id = db.Column(db.Integer, db.ForeignKey('work_recommendation.id'))
    story_recommendation_id = db.Column(db.Integer, db.ForeignKey('work_recommendation.id'))
    essay_recommendation_id = db.Column(db.Integer, db.ForeignKey('work_recommendation.id'))
    overall_rating = db.Column(db.Integer)  # 1-5
    overall_feedback = db.Column(db.Text)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships to the individual recommendations
    poem_rec = db.relationship('WorkRecommendation', foreign_keys=[poem_recommendation_id])
    story_rec = db.relationship('WorkRecommendation', foreign_keys=[story_recommendation_id])
    essay_rec = db.relationship('WorkRecommendation', foreign_keys=[essay_recommendation_id])

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        if not current_user.onboarding_completed:
            return redirect(url_for('onboarding'))
        return redirect(url_for('daily_view'))
    return render_template('welcome.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return render_template('register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('onboarding'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if not user.onboarding_completed:
                return redirect(url_for('onboarding'))
            return redirect(url_for('daily_view'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/onboarding')
@login_required
def onboarding():
    if current_user.onboarding_completed:
        return redirect(url_for('daily_view'))
    return render_template('onboarding.html')

@app.route('/daily')
@login_required
def daily_view():
    if not current_user.onboarding_completed:
        return redirect(url_for('onboarding'))
    
    # Get today's recommendations (we'll implement this logic later)
    today = date.today()
    daily_set = DailyRecommendationSet.query.filter_by(
        user_id=current_user.id,
        date=today
    ).first()
    
    return render_template('daily.html', daily_set=daily_set)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)