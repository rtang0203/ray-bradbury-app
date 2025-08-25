"""
Utility functions for processing and summarizing user preferences.
"""

from .models import User, UserPreference
from .embeddings_engine import EmbeddingRecommendationEngine
from . import db
import json

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

def save_user_preferences(user_id, data):
    """
    Parse and save user preferences from onboarding form, generate preference summary,
    and create embedding vector for recommendation matching.
    
    Args:
        user_id: The ID of the user
        data: Form data containing preferences
    
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
    
    # Generate preference summary for LLM integration
    update_user_preference_summary(user_id)
    
    # Generate and save user embedding vector
    user = User.query.get(user_id)
    if user and user.preference_summary:
        try:
            engine = EmbeddingRecommendationEngine()
            embedding = engine.generate_user_embedding(user)
            
            user.embedding_vector = json.dumps(embedding)
            db.session.commit()
            
        except Exception as e:
            print(f"Error generating user embedding: {e}")
            # Continue without embedding - will fall back to basic recommendations