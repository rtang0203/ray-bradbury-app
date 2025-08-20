"""
Utility functions for processing and summarizing user preferences.
"""

from .models import User, UserPreference

def generate_preference_summary(user_id):
    """
    Generate a natural language summary of user preferences for LLM consumption.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        str: A natural language summary of all user preferences
    """
    user = User.query.get(user_id)
    if not user:
        return ""
    
    preferences = UserPreference.query.filter_by(
        user_id=user_id, 
        active=True
    ).all()
    
    # Group preferences by type
    books = [p.preference_value for p in preferences if p.preference_type == 'book']
    authors = [p.preference_value for p in preferences if p.preference_type == 'author']
    interests = [p.preference_value for p in preferences if p.preference_type == 'interest']
    avoid = [p.preference_value for p in preferences if p.preference_type == 'avoid']
    
    # Build natural language summary
    summary_parts = []
    
    # Basic reading preferences
    difficulty_map = {
        'beginner': 'accessible and easy-to-read',
        'intermediate': 'moderately challenging',
        'advanced': 'complex and intellectually demanding'
    }
    
    length_map = {
        'short': 'brief reads (5-10 minutes)',
        'medium': 'medium-length pieces (10-20 minutes)', 
        'long': 'longer works (20+ minutes)'
    }
    
    adventurousness_desc = ""
    if user.adventurousness_level < 0.3:
        adventurousness_desc = "prefers familiar genres and well-known works"
    elif user.adventurousness_level > 0.7:
        adventurousness_desc = "loves exploring new genres and experimental literature"
    else:
        adventurousness_desc = "enjoys a mix of familiar and new literary experiences"
    
    summary_parts.append(f"Prefers {difficulty_map.get(user.difficulty_preference, 'intermediate')} literature and {length_map.get(user.preferred_length, 'medium-length pieces')}. {adventurousness_desc.capitalize()}.")
    
    # Favorite books
    if books:
        if len(books) == 1:
            summary_parts.append(f"Favorite book: {books[0]}.")
        else:
            book_list = ", ".join(books[:-1]) + f", and {books[-1]}" if len(books) > 1 else books[0]
            summary_parts.append(f"Favorite books include: {book_list}.")
    
    # Favorite authors
    if authors:
        if len(authors) == 1:
            summary_parts.append(f"Enjoys works by {authors[0]}.")
        else:
            author_list = ", ".join(authors[:-1]) + f", and {authors[-1]}" if len(authors) > 1 else authors[0]
            summary_parts.append(f"Enjoys works by {author_list}.")
    
    # Other interests (cross-media influences)
    if interests:
        if len(interests) == 1:
            summary_parts.append(f"Also interested in: {interests[0]}.")
        else:
            interest_list = ", ".join(interests[:-1]) + f", and {interests[-1]}" if len(interests) > 1 else interests[0]
            summary_parts.append(f"Other interests include: {interest_list}.")
    
    # Topics to avoid
    if avoid:
        if len(avoid) == 1:
            summary_parts.append(f"Prefers to avoid: {avoid[0]}.")
        else:
            avoid_list = ", ".join(avoid[:-1]) + f", and {avoid[-1]}" if len(avoid) > 1 else avoid[0]
            summary_parts.append(f"Prefers to avoid topics like: {avoid_list}.")
    
    return " ".join(summary_parts)

def update_user_preference_summary(user_id):
    """
    Generate and save preference summary for a user.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        from . import db
        
        user = User.query.get(user_id)
        if not user:
            return False
        
        summary = generate_preference_summary(user_id)
        user.preference_summary = summary
        db.session.commit()
        
        return True
        
    except Exception as e:
        from . import db
        db.session.rollback()
        return False

def get_user_preference_summary(user_id):
    """
    Get the preference summary for a user, generating it if it doesn't exist.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        str: The preference summary
    """
    user = User.query.get(user_id)
    if not user:
        return ""
    
    # Return existing summary if available
    if user.preference_summary:
        return user.preference_summary
    
    # Generate new summary if none exists
    summary = generate_preference_summary(user_id)
    
    # Try to save it (optional - don't fail if this doesn't work)
    try:
        from . import db
        user.preference_summary = summary
        db.session.commit()
    except:
        pass
    
    return summary