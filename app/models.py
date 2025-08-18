from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime, timezone

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
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
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
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
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
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
    added_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
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
    recommended_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

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
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    # Relationships to the individual recommendations
    poem_rec = db.relationship('WorkRecommendation', foreign_keys=[poem_recommendation_id])
    story_rec = db.relationship('WorkRecommendation', foreign_keys=[story_recommendation_id])
    essay_rec = db.relationship('WorkRecommendation', foreign_keys=[essay_recommendation_id])

# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
