from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from .models import User, UserPreference, WorkRecommendation
from .recommendations import get_user_recommendations_for_date, populate_user_work_pool
from .preference_utils import update_user_preference_summary
from . import db
from datetime import date, datetime, timezone

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

@bp.route('/onboarding', methods=['GET', 'POST'])
@login_required
def onboarding():
    if current_user.onboarding_completed:
        return redirect(url_for('routes.daily_view'))
    
    if request.method == 'POST':
        try:
            # Clear existing preferences
            UserPreference.query.filter_by(user_id=current_user.id).delete()
            
            # Get form data
            data = request.get_json() if request.is_json else request.form
            
            # Parse and save user preferences
            _save_user_preferences(current_user.id, data)
            
            # Update user settings
            current_user.difficulty_preference = data.get('difficulty', 'intermediate')
            current_user.preferred_length = data.get('length', 'medium')
            
            # Convert adventurousness from 0-100 to 0-1
            adventurousness = float(data.get('adventurousness', 50)) / 100.0
            current_user.adventurousness_level = adventurousness
            
            # Mark onboarding as completed
            current_user.onboarding_completed = True
            
            db.session.commit()
            
            # Generate preference summary for LLM use
            update_user_preference_summary(current_user.id)
            
            # Generate initial work pool
            populate_user_work_pool(current_user.id)
            
            flash('Welcome! Your preferences have been saved.')
            
            if request.is_json:
                return {'success': True, 'redirect': url_for('routes.daily_view')}
            else:
                return redirect(url_for('routes.daily_view'))
                
        except Exception as e:
            db.session.rollback()
            flash(f'Error saving preferences: {str(e)}')
            if request.is_json:
                return {'success': False, 'error': str(e)}, 400
            
    return render_template('onboarding.html')

def _save_user_preferences(user_id, data):
    """
    Parse and save user preferences from onboarding form.
    
    TODO: Enhanced parsing for better preference extraction:
    - Use NLP to extract genres/themes from book titles
    - Identify author writing styles and periods
    - Map movie directors to literary equivalents
    - Extract keywords and themes from interests
    - Parse complex preference descriptions
    """
    
    # Save favorite books
    favorite_books = data.get('favoriteBooks', '').strip()
    if favorite_books:
        for book in favorite_books.split('\n'):
            book = book.strip()
            if book:
                # TODO: Parse book title to extract:
                # - Genre inference
                # - Author style matching
                # - Theme extraction
                # - Publication period preferences
                pref = UserPreference(
                    user_id=user_id,
                    preference_type='book',
                    preference_value=book,
                    weight=1.0
                )
                db.session.add(pref)
    
    # Save favorite authors
    favorite_authors = data.get('favoriteAuthors', '').strip()
    if favorite_authors:
        for author in favorite_authors.split('\n'):
            author = author.strip()
            if author:
                # TODO: Author analysis:
                # - Map to writing style characteristics
                # - Identify common themes in their work
                # - Find similar contemporary/classic authors
                # - Extract genre preferences from author catalog
                pref = UserPreference(
                    user_id=user_id,
                    preference_type='author',
                    preference_value=author,
                    weight=1.0
                )
                db.session.add(pref)
    
    # Save other interests (movies, directors, artists)
    other_interests = data.get('otherInterests', '').strip()
    if other_interests:
        for interest in other_interests.split('\n'):
            interest = interest.strip()
            if interest:
                # TODO: Cross-media preference mapping:
                # - Map film directors to literary equivalents (e.g., Wes Anderson -> quirky, detailed prose)
                # - Extract visual artist styles to literary themes
                # - Music preferences to rhythm/mood in writing
                # - Identify aesthetic preferences that cross mediums
                pref = UserPreference(
                    user_id=user_id,
                    preference_type='interest',
                    preference_value=interest,
                    weight=0.8
                )
                db.session.add(pref)
    
    # Save topics to avoid
    avoid_topics = data.get('avoidTopics', '').strip()
    if avoid_topics:
        for topic in avoid_topics.split('\n'):
            topic = topic.strip()
            if topic:
                # TODO: Topic avoidance parsing:
                # - Expand single topics to related themes
                # - Handle nuanced preferences (e.g., "some violence ok, but not graphic")
                # - Map broad categories to specific literary elements
                pref = UserPreference(
                    user_id=user_id,
                    preference_type='avoid',
                    preference_value=topic,
                    weight=-1.0
                )
                db.session.add(pref)

@bp.route('/daily')
@login_required
def daily_view():
    if not current_user.onboarding_completed:
        return redirect(url_for('routes.onboarding'))
    
    recommendations = get_user_recommendations_for_date(current_user.id)
    
    return render_template('daily.html', recommendations=recommendations, datetime=datetime)

@bp.route('/daily-test')
@login_required
def daily_view_test():
    """Temporary route to test daily template without onboarding requirement"""
    recommendations = get_user_recommendations_for_date(current_user.id)
    
    return render_template('daily.html', recommendations=recommendations, datetime=datetime)

@bp.route('/generate-pool')
@login_required
def generate_pool():
    """Route to populate user's work pool with recommendations"""
    try:
        success = populate_user_work_pool(current_user.id)
        if success:
            flash('Work pool generated successfully!')
        else:
            flash('Failed to generate work pool')
    except Exception as e:
        flash(f'Error generating work pool: {str(e)}')
    
    return redirect(url_for('routes.daily_view'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            # Get form data
            data = request.get_json() if request.is_json else request.form
            
            # Clear existing preferences
            UserPreference.query.filter_by(user_id=current_user.id).delete()
            
            # Save updated preferences
            _save_user_preferences(current_user.id, data)
            
            # Update user settings
            current_user.difficulty_preference = data.get('difficulty', current_user.difficulty_preference)
            current_user.preferred_length = data.get('length', current_user.preferred_length)
            
            # Convert adventurousness from 0-100 to 0-1
            adventurousness = float(data.get('adventurousness', current_user.adventurousness_level * 100)) / 100.0
            current_user.adventurousness_level = adventurousness
            
            db.session.commit()
            
            # Regenerate preference summary
            update_user_preference_summary(current_user.id)
            
            # TODO: Optionally regenerate work pool based on new preferences
            # populate_user_work_pool(current_user.id)
            
            flash('Preferences updated successfully!')
            
            if request.is_json:
                return {'success': True}
            else:
                return redirect(url_for('routes.profile'))
                
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating preferences: {str(e)}')
            if request.is_json:
                return {'success': False, 'error': str(e)}, 400
    
    # GET request - show profile page
    # Get current preferences by type
    preferences = UserPreference.query.filter_by(user_id=current_user.id, active=True).all()
    
    book_preferences = [p for p in preferences if p.preference_type == 'book']
    author_preferences = [p for p in preferences if p.preference_type == 'author']
    interest_preferences = [p for p in preferences if p.preference_type == 'interest']
    avoid_preferences = [p for p in preferences if p.preference_type == 'avoid']
    
    # Get reading statistics
    total_recommendations = WorkRecommendation.query.filter_by(user_id=current_user.id).count()
    completed_recommendations = WorkRecommendation.query.filter_by(
        user_id=current_user.id, 
        status='completed'
    ).count()
    
    # Calculate average rating
    rated_recommendations = WorkRecommendation.query.filter(
        WorkRecommendation.user_id == current_user.id,
        WorkRecommendation.rating.isnot(None)
    ).all()
    
    average_rating = None
    if rated_recommendations:
        total_rating = sum(r.rating for r in rated_recommendations)
        average_rating = total_rating / len(rated_recommendations)
    
    # Calculate days active (days since first recommendation)
    first_recommendation = WorkRecommendation.query.filter_by(
        user_id=current_user.id
    ).order_by(WorkRecommendation.recommended_at.asc()).first()
    
    days_active = 0
    if first_recommendation:
        # Ensure both datetimes are timezone-aware for comparison
        now = datetime.now(timezone.utc)
        recommended_at = first_recommendation.recommended_at
        if recommended_at.tzinfo is None:
            # If recommended_at is naive, assume it's UTC
            recommended_at = recommended_at.replace(tzinfo=timezone.utc)
        days_active = (now - recommended_at).days + 1
    
    return render_template('profile.html',
                         book_preferences=book_preferences,
                         author_preferences=author_preferences, 
                         interest_preferences=interest_preferences,
                         avoid_preferences=avoid_preferences,
                         total_recommendations=total_recommendations,
                         completed_recommendations=completed_recommendations,
                         average_rating=average_rating,
                         days_active=days_active)

@bp.route('/rate-recommendation', methods=['POST'])
@login_required
def rate_recommendation():
    """Rate an individual work recommendation"""
    try:
        data = request.get_json()
        rec_id = data.get('recommendation_id')
        rating = int(data.get('rating'))
        
        if not rec_id or not (1 <= rating <= 5):
            return {'success': False, 'error': 'Invalid recommendation ID or rating'}, 400
        
        # Find the recommendation
        recommendation = WorkRecommendation.query.filter_by(
            id=rec_id,
            user_id=current_user.id
        ).first()
        
        if not recommendation:
            return {'success': False, 'error': 'Recommendation not found'}, 404
        
        # Update the rating
        recommendation.rating = rating
        recommendation.updated_at = datetime.now(timezone.utc)
        
        # Mark as completed if not already
        if recommendation.status == 'unread':
            recommendation.status = 'completed'
            recommendation.completed_at = datetime.now(timezone.utc)
        
        db.session.commit()
        
        return {'success': True, 'rating': rating}
        
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'error': str(e)}, 500
