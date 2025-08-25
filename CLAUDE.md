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
- **🆕 Embedding-based recommendation system** - Google Gemini API integration with cosine similarity matching
- **🆕 Enhanced database schema** - Added embedding_vector columns to User and Work models
- **🆕 Hybrid recommendation architecture** - Embeddings for fast pre-filtering + LLM for final refinement

### 📋 IMMEDIATE PRIORITIES:

#### Phase 1: Integration of New Embedding System (NEXT)
1. **Update routes to use embedding recommendations** - Replace basic algorithm with embedding-based system
2. **Integrate hybrid recommendations** - Connect embedding + LLM scoring to existing UserWorkPool
3. **Test embedding system with real users** - Ensure similarity matching works across different preferences

#### Phase 2: User Experience Enhancement
4. **Skip/Regenerate functionality** - Allow users to skip individual recommendations and get new ones
5. **Mark as read functionality** - Update recommendation status when user clicks "Read Now"
6. **Reading progress tracking** - Better status management (unread/in_progress/completed)

#### Phase 3: Enhanced Intelligence & Content
7. **Learning from ratings** - Update confidence scores and embeddings based on user feedback
8. **Content expansion** - Seed database with more works (50+ per category) for better recommendations
9. **Advanced LLM refinement** - Use LLM to enhance recommendation reasoning and variety

#### Phase 4: Extended Features
10. **Reading history page** - View past recommendations and ratings
11. **Reading streaks & habits** - Track daily reading consistency
12. **Advanced analytics** - Reading patterns, favorite authors/themes analysis

## Architecture Overview

### Embedding-Based Recommendation System (NEW!)
- **Technology:** Google Gemini API (gemini-embedding-001) with 3072-dimensional vectors
- **Architecture:** Hybrid approach combining embedding similarity + LLM refinement
- **Process Flow:** 
  1. Generate embeddings for all works and user preferences
  2. Use cosine similarity to find top 50 candidates (fast, cheap)
  3. LLM scores top candidates for final ranking (accurate, expensive)
  4. Populate UserWorkPool with confidence scores
- **Benefits:** Cost-effective, scalable, and intelligently matches user preferences to content

### UserWorkPool System (ENHANCED)
- **Purpose:** Pre-generates and caches recommendations using embedding + LLM hybrid scoring
- **Logic:** Embedding similarity finds candidates → LLM refines → stores with confidence scores
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
- **Integrate embedding system** - Connect new recommendation engine to existing routes
- **Skip/regenerate functionality** - Allow users to get new individual recommendations
- **Reading progress tracking** - Mark works as read/in-progress

## Session Summary (Latest - Embedding System Implementation)

### Major Breakthrough - AI-Powered Recommendations:
1. **Built complete embedding recommendation system** - Google Gemini API integration with hybrid approach
2. **Enhanced database schema** - Added embedding_vector fields to User and Work models with Flask-Migrate
3. **Implemented intelligent matching** - Cosine similarity for fast pre-filtering + LLM refinement
4. **Created testing infrastructure** - Scripts to generate, test, and inspect embeddings
5. **Solved API integration challenges** - Fixed dimension mismatches and response parsing

### Technical Achievements:
- **Environment configuration** - Secure API key storage with .env and python-dotenv
- **Hybrid architecture** - Balance of speed (embeddings) and accuracy (LLM scoring)  
- **Cost optimization** - Free Gemini API tier with semantic similarity task configuration
- **Error handling** - Robust fallbacks and dimension validation
- **Testing tools** - Scripts for embedding generation and similarity testing

### Current State - Ready for Integration:
- **15 works with embeddings** - All literature pieces have 3072-dimensional vectors
- **User preference embeddings** - Natural language summaries converted to searchable vectors
- **Working similarity matching** - Cosine similarity successfully finds relevant content
- **Tested end-to-end** - Embedding generation → similarity calculation → recommendation ranking

### Next Session Goals:
- **Replace basic recommendation algorithm** - Switch routes to use embedding-based system
- **Integrate with existing UserWorkPool** - Use hybrid scores in current workflow
- **Expand content database** - Add more works for richer recommendations
- **Implement LLM refinement** - Use Gemini for final recommendation scoring