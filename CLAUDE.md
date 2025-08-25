# CLAUDE.md

## Notes

- **Think carefully and try to identify the root cause instead of adding unnecessary complexity. Keep changes concise when possible.**

## Project Overview

A daily literary recommendation app inspired by Ray Bradbury's quote: "You must read one poem, one short story, and one essay every night for 1,000 nights." The app provides personalized daily recommendations using an embedding-based recommendation system.

## Development Commands

```bash
python run.py                    # Run Flask development server
python scripts/seed_content.py  # Seed database with content
pip install -r requirements.txt # Install dependencies
```

## Current Status & Next Priorities

### ✅ Completed:
- Flask app with authentication, models, and templates
- **✅ Fully integrated embedding-based recommendation system** - Google Gemini API with 3072-dimensional vectors
- **✅ Complete preference pipeline** - Raw preferences → summary → embedding → recommendations
- **✅ Atomic preference saving** - `save_user_preferences()` handles complete workflow
- **✅ Template/route consistency** - Fixed `story` vs `short_story` key mapping
- **✅ Clean architecture** - Moved preference logic to `preference_utils.py`
- **✅ Embedding generation** - Only called during onboarding/profile updates (cost-efficient)
- **✅ Individual rating system** - Rate each poem/story/essay separately
- **✅ Database seeded** - 15 works with embedding vectors generated

### 🔍 Current Limitation:
- **Similar recommendations across users** due to small content pool (15 works) and content-preference mismatch
- Algorithm working correctly but needs more diverse content to differentiate properly

### 📋 Next Steps:
1. **Content expansion** - Add 50+ works per category with diverse themes (religious, philosophical, modern, etc.)
2. **Learning system** - Update confidence scores based on user ratings
3. **LLM integration** - call LLM model to refine confidence scores for top choices further 
4. **Algorithm refinement** - Adjust similarity thresholds and add content diversity scoring

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
    'short_story': generate_daily_recommendation(user_id, 'short_story', date),
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
- **Database:** SQLite (development) 
- **Frontend:** Tailwind CSS, minimal JavaScript
- **Authentication:** Flask-Login
- **AI:** Google Gemini API for embeddings and LLM scoring

## Code Conventions
- SQLAlchemy ORM for all database operations
- Flask-Login for authentication
- Confidence scoring system (0-1 float) for recommendation quality
- UTC timestamps for all datetime fields