from datetime import date, datetime, timezone
from sqlalchemy import and_, or_
from .models import (
    User, Work, UserWorkPool, WorkRecommendation, db
)
from .embeddings_engine import EmbeddingRecommendationEngine

def generate_daily_recommendation(user_id, work_type, target_date=None):
    """
    Generate a single daily recommendation for a specific work type.
    
    Args:
        user_id: The ID of the user
        work_type: The type of work ('poem', 'short_story', 'essay')
        target_date: The date to generate recommendation for (defaults to today)
    
    Returns:
        WorkRecommendation or None if generation fails
    """
    if target_date is None:
        target_date = date.today()
    
    # 1. Check if recommendation already exists for this date and type
    existing_rec = WorkRecommendation.query.filter_by(
        user_id=user_id,
        work_type=work_type,
        date=target_date
    ).first()
    
    if existing_rec:
        return existing_rec
    
    # 2. Get user's available work pool for this category
    candidates = _get_available_works(user_id, work_type)
    
    if not candidates:
        return None
    
    # 3. Select the best work
    selected_work = _select_best_work(candidates)
    
    if not selected_work:
        return None
    
    try:
        # 4. Create WorkRecommendation record
        recommendation = WorkRecommendation(
            user_id=user_id,
            work_id=selected_work.work_id,
            work_type=work_type,
            date=target_date,
            reasoning=f"Selected based on confidence score {selected_work.confidence_score:.2f}"
        )
        
        db.session.add(recommendation)
        
        # 5. Update UserWorkPool status to 'recommended'
        _mark_works_as_recommended([selected_work])
        
        db.session.commit()
        return recommendation
        
    except Exception as e:
        db.session.rollback()
        raise e

def get_daily_recommendations(user_id, target_date=None, regenerate=False):
    """
    Get or generate all three daily recommendations (poem, story, essay) for a user.
    
    Args:
        user_id: The ID of the user
        target_date: The date to get recommendations for (defaults to today)
        regenerate: If True, always generate new recommendations. If False, use existing ones if available.
    
    Returns:
        dict with keys 'poem', 'short_story', 'essay' containing WorkRecommendation objects
    """
    if target_date is None:
        target_date = date.today()
    
    recommendations = {}
    
    for work_type in ['poem', 'short_story', 'essay']:
        existing_rec = None
        
        if not regenerate:
            # Check for existing recommendation
            existing_rec = WorkRecommendation.query.filter_by(
                user_id=user_id,
                work_type=work_type,
                date=target_date
            ).first()
        
        if existing_rec:
            recommendations[work_type] = existing_rec
        else:
            # Generate new recommendation
            rec = generate_daily_recommendation(user_id, work_type, target_date)
            recommendations[work_type] = rec
    
    return recommendations

def _get_available_works(user_id, work_type):
    """Get available works from user's pool for a specific type."""
    return UserWorkPool.query.filter(
        and_(
            UserWorkPool.user_id == user_id,
            UserWorkPool.work_type == work_type,
            UserWorkPool.status == 'available',
            UserWorkPool.active == True
        )
    ).order_by(
        UserWorkPool.confidence_score.desc(),
        UserWorkPool.last_recommended_at.asc().nullsfirst()
    ).limit(10).all()  # Get top 10 candidates

def _select_best_work(candidates):
    """
    Select the best work from candidates, considering variety.
    For now, just picks the highest confidence score.
    Future: Consider author diversity, themes, etc.
    """
    if not candidates:
        return None
    
    # For basic implementation, just return highest confidence
    return candidates[0]

def _mark_works_as_recommended(work_pool_entries):
    """Mark work pool entries as recommended and update timestamps."""
    current_time = datetime.now(timezone.utc)
    
    for entry in work_pool_entries:
        entry.status = 'recommended'
        entry.last_recommended_at = current_time
        entry.times_recommended += 1

def populate_user_work_pool(user_id):
    """
    Populate a user's work pool using the embedding-based recommendation engine.
    """
    user = User.query.get(user_id)
    if not user:
        return False
    
    if not user.embedding_vector:
        # Fallback to basic algorithm if no embedding vector for user exists
        return _populate_user_work_pool_basic(user_id)
    
    try:
        # Clear existing pool
        UserWorkPool.query.filter_by(user_id=user_id).delete()
        
        # Use embedding engine for intelligent recommendations
        engine = EmbeddingRecommendationEngine()
        engine.populate_user_work_pool(user_id)
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in embedding-based pool population: {e}")
        # Fallback to basic algorithm on error
        try:
            return _populate_user_work_pool_basic(user_id)
        except Exception as fallback_error:
            print(f"Fallback algorithm also failed: {fallback_error}")
            raise e

def _populate_user_work_pool_basic(user_id):
    """
    Basic fallback implementation for populating user's work pool.
    Used when embedding engine is unavailable or user lacks preference summary.
    """
    user = User.query.get(user_id)
    if not user:
        return False
    
    # Get all available works
    poems = Work.query.filter_by(work_type='poem', active=True).all()
    stories = Work.query.filter_by(work_type='short_story', active=True).all()
    essays = Work.query.filter_by(work_type='essay', active=True).all()
    
    # Add works with basic confidence scoring
    for work in poems:
        confidence = _calculate_basic_confidence(user, work)
        if confidence > 0.3:  # Only add if confidence is above threshold
            pool_entry = UserWorkPool(
                user_id=user_id,
                work_id=work.id,
                work_type='poem',
                confidence_score=confidence,
                added_reason="Basic algorithm match"
            )
            db.session.add(pool_entry)
    
    for work in stories:
        confidence = _calculate_basic_confidence(user, work)
        if confidence > 0.3:
            pool_entry = UserWorkPool(
                user_id=user_id,
                work_id=work.id,
                work_type='short_story',
                confidence_score=confidence,
                added_reason="Basic algorithm match"
            )
            db.session.add(pool_entry)
    
    for work in essays:
        confidence = _calculate_basic_confidence(user, work)
        if confidence > 0.3:
            pool_entry = UserWorkPool(
                user_id=user_id,
                work_id=work.id,
                work_type='essay',
                confidence_score=confidence,
                added_reason="Basic algorithm match"
            )
            db.session.add(pool_entry)
    
    db.session.commit()
    return True

def _calculate_basic_confidence(user, work):
    """
    Calculate basic confidence score for a work based on user preferences.
    Returns a score between 0 and 1.
    """
    base_score = 0.5  # Start with neutral confidence
    
    # Adjust based on difficulty preference
    if user.difficulty_preference == work.difficulty_level:
        base_score += 0.2
    elif user.difficulty_preference == 'beginner' and work.difficulty_level == 'intermediate':
        base_score += 0.1
    elif user.difficulty_preference == 'advanced' and work.difficulty_level == 'intermediate':
        base_score += 0.1
    elif user.difficulty_preference == 'intermediate':
        base_score += 0.05  # Intermediate users can handle any level
    
    # Adjust based on reading time preference
    reading_time = work.estimated_reading_time or 10  # Default to 10 minutes
    
    if user.preferred_length == 'short' and reading_time <= 5:
        base_score += 0.15
    elif user.preferred_length == 'medium' and 5 < reading_time <= 15:
        base_score += 0.15
    elif user.preferred_length == 'long' and reading_time > 15:
        base_score += 0.15
    
    # Adjust based on adventurousness (how willing to try new things)
    if user.adventurousness_level > 0.7:
        # Adventurous users might like more challenging or unusual works
        if work.difficulty_level == 'advanced':
            base_score += 0.1
    elif user.adventurousness_level < 0.3:
        # Conservative users prefer well-known, accessible works
        if work.difficulty_level == 'beginner':
            base_score += 0.1
    
    # Ensure score stays within bounds
    return max(0.0, min(1.0, base_score))

