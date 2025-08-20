# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A daily literary recommendation app inspired by Ray Bradbury's quote: "You must read one poem, one short story, and one essay every night for 1,000 nights." The app provides personalized daily recommendations across three categories, learns from user ratings, and builds reading habits through an intelligent recommendation system.

## Development Commands

```bash
# Run the Flask development server
python run.py

# Seed the database with curated literary content
python scripts/seed_content.py

# Install dependencies
pip install -r requirements.txt
```

## Current Implementation Status

### ✅ COMPLETED:
- Complete Flask app structure with all database models
- User authentication system (registration/login/logout)
- All SQLAlchemy models with proper relationships
- Template system with responsive design using Tailwind CSS
- Navigation and routing structure
- **Full onboarding system** - Backend processing and preference storage
- **Individual recommendation engine** - Simplified WorkRecommendation system (removed DailyRecommendationSet)
- **Daily view with real recommendations** - Shows actual works with working external links
- **Individual rating system** - Rate each poem/story/essay separately
- **Profile/preferences editing page** - Update preferences and view reading stats
- **Preference summary system** - Natural language summaries for LLM integration
- **UserWorkPool population** - Basic confidence scoring algorithm
- **Database seeded** - 15 initial works (5 poems, 5 stories, 5 essays) with working content URLs

### 📋 IMMEDIATE PRIORITIES:

#### Phase 1: User Experience Enhancement (NEXT)
1. **Skip/Regenerate functionality** - Allow users to skip individual recommendations and get new ones
2. **Mark as read functionality** - Update recommendation status when user clicks "Read Now"
3. **Reading progress tracking** - Better status management (unread/in_progress/completed)

#### Phase 2: LLM Integration & Intelligence
4. **LLM-powered recommendations** - Use preference summaries to generate smarter UserWorkPool
5. **Learning from ratings** - Update confidence scores based on user feedback
6. **Advanced recommendation variety** - Consider themes, writing styles, author diversity

#### Phase 3: Extended Features
7. **Reading history page** - View past recommendations and ratings
8. **Reading streaks & habits** - Track daily reading consistency
9. **Content expansion** - Add more works to the database

## Architecture Overview

### UserWorkPool System (KEY INNOVATION)
- **Purpose:** Pre-generates and caches recommendations to avoid daily LLM API calls
- **Logic:** LLM analyzes user preferences → generates ~50-100 works per category → stores with confidence scores
- **Daily Selection:** Pick highest confidence works not recently recommended
- **Learning:** Good ratings boost similar works, bad ratings lower confidence scores

### Core Data Model Flow (Simplified Architecture)

The recommendation system works through individual WorkRecommendation records:

1. **User** → **UserPreference**: Captures reading preferences during onboarding with natural language summaries
2. **Work** → **UserWorkPool**: Algorithm adds works to user's personalized pool with confidence scores
3. **UserWorkPool** → **WorkRecommendation**: Daily algorithm selects from pool to create individual recommendations
4. **Individual recommendations**: Each work type (poem/story/essay) is independent - no grouping required

### Key Model Relationships

- `WorkRecommendation` includes `work_type` field ('poem', 'short_story', 'essay') for independent tracking
- `UserWorkPool` tracks recommendation history via `times_recommended`, `last_recommended_at`, and `status` (available/recommended/exhausted)
- `User.preference_summary` stores LLM-friendly natural language version of all preferences
- All datetime fields use `datetime.now(timezone.utc)` for UTC timestamps

### Recommendation Algorithm Design

```python
def generate_daily_recommendation(user_id, work_type, date):
    # 1. Check if recommendation already exists for date and work_type
    # 2. Get user's available work pool for specific type (status='available') 
    # 3. Select highest confidence work not recently recommended
    # 4. Create individual WorkRecommendation record with work_type
    # 5. Update UserWorkPool status to 'recommended'
    
# Generate all three independently
recommendations = {
    'poem': generate_daily_recommendation(user_id, 'poem', date),
    'story': generate_daily_recommendation(user_id, 'short_story', date),
    'essay': generate_daily_recommendation(user_id, 'essay', date)
}
```

### Learning System
- **Good ratings (4-5 stars):** Add similar works, boost confidence of related items
- **Bad ratings (1-2 stars):** Remove similar works, lower confidence scores  
- **Preference changes:** Regenerate relevant pool sections
- **Pool refresh:** Generate new works every few weeks

## Technology Stack
- **Backend:** Flask + SQLAlchemy
- **Database:** SQLite (development) / PostgreSQL (production)  
- **Frontend:** Tailwind CSS via CDN, minimal JavaScript
- **Authentication:** Flask-Login
- **Planned AI Integration:** LLM API (OpenAI/Anthropic) for generating recommendation pools
- **Content Sources:** Public domain works (Project Gutenberg, Poetry Foundation)

## Code Style & Preferences

### Python/Flask Conventions:
- Use SQLAlchemy ORM for all database operations
- Flask-Login for authentication
- Blueprint structure for routes
- Environment-based configuration (config.py)
- Clear model relationships with proper foreign keys

### Frontend Approach:
- **Tailwind CSS** for styling (already implemented)
- **Minimal JavaScript** - progressive enhancement
- **Mobile-first responsive design**
- **Semantic HTML** with accessibility considerations

### Database Design:
- **Confidence scoring system** (0-1 float) for recommendation quality
- **Status tracking** for works (available/recommended/exhausted)
- **Comprehensive metadata** for works (difficulty, themes, reading time)

## Session Summary (Latest)

### Major Architectural Refactor Completed:
1. **Built complete recommendation system** - From basic confidence scoring to full user workflow
2. **Implemented full onboarding flow** - User preferences captured and stored with natural language summaries
3. **Created profile/preferences editing** - Users can update preferences and view reading statistics
4. **Added individual rating system** - Rate each work separately with 1-5 stars
5. **Simplified architecture** - Removed DailyRecommendationSet complexity, now using individual WorkRecommendations
6. **Database structure finalized** - All models working with proper relationships and data types

### Key Benefits Achieved:
- **Flexible individual control** - Skip, rate, or regenerate any work independently
- **LLM-ready preference system** - Natural language summaries for smarter recommendations
- **Clean, maintainable codebase** - Simpler queries, clearer data flow
- **Complete user experience** - From registration to daily recommendations with ratings

### Ready for Next Phase:
- **Skip/regenerate functionality** - Allow users to get new individual recommendations
- **Reading progress tracking** - Mark works as read/in-progress  
- **LLM integration** - Use preference summaries for smarter work pool generation