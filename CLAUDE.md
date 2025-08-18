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
- Basic onboarding flow template (needs backend integration)

### 📋 IMMEDIATE PRIORITIES:

#### Phase 1: Core Content & Recommendations (NEXT)
1. **Seed Content Database** - Populate `Work` table with initial poems, stories, essays
2. **Basic Recommendation Engine** - Simple recommendation logic before LLM integration
3. **Complete Daily View** - Display actual recommendations instead of placeholders

#### Phase 2: User Experience
4. **Complete Onboarding Backend** - Process and store user preferences
5. **Rating & Feedback System** - Star ratings with feedback collection
6. **History & Profile Pages** - Reading history and preference management

#### Phase 3: Intelligence & Personalization
7. **LLM Integration** - Generate personalized UserWorkPool via API
8. **Learning Algorithm** - Update recommendations based on user ratings

## Architecture Overview

### UserWorkPool System (KEY INNOVATION)
- **Purpose:** Pre-generates and caches recommendations to avoid daily LLM API calls
- **Logic:** LLM analyzes user preferences → generates ~50-100 works per category → stores with confidence scores
- **Daily Selection:** Pick highest confidence works not recently recommended
- **Learning:** Good ratings boost similar works, bad ratings lower confidence scores

### Core Data Model Flow

The recommendation system works through several interconnected models:

1. **User** → **UserPreference**: Captures reading preferences during onboarding
2. **Work** → **UserWorkPool**: Algorithm adds works to user's personalized pool with confidence scores
3. **UserWorkPool** → **WorkRecommendation**: Daily algorithm selects from pool to create recommendations
4. **WorkRecommendation** → **DailyRecommendationSet**: Groups poem/story/essay into daily sets

### Key Model Relationships

- `DailyRecommendationSet` has foreign keys to three separate `WorkRecommendation` records (poem_recommendation_id, story_recommendation_id, essay_recommendation_id)
- `UserWorkPool` tracks recommendation history via `times_recommended`, `last_recommended_at`, and `status` (available/recommended/exhausted)
- All datetime fields use `datetime.now(timezone.utc)` for UTC timestamps

### Recommendation Algorithm Design

```python
def generate_daily_recommendations(user_id, date):
    # 1. Check if recommendations already exist for date
    # 2. Get user's available work pool (status='available') 
    # 3. Select highest confidence works not recently recommended
    # 4. Ensure variety (different authors, themes, time periods)
    # 5. Create WorkRecommendation records
    # 6. Create DailyRecommendationSet linking the three
    # 7. Update UserWorkPool status to 'recommended'
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

## Current Challenges
- **Daily view shows placeholders** - Need actual recommendation data
- **Onboarding form submission** - Frontend complete, backend needed
- **Content database empty** - Need seeding script for initial works
- **No recommendation engine** - Core logic needs implementation