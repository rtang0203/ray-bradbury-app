# CLAUDE.md

## Project Overview

A daily literary recommendation app inspired by Ray Bradbury's quote: "You must read one poem, one short story, and one essay every night for 1,000 nights." The app provides personalized daily recommendations using an embedding-based recommendation system.

## Development Commands

```bash
python run.py                    # Run Flask development server
python scripts/seed_content.py  # Seed database with content
pip install -r requirements.txt # Install dependencies
python scripts/find_gutenberg_urls.py --update # Find Project Gutenberg URLs
```

## Current App Features

### Authentication & User Management
- **User registration/login** - Username or email login supported
- **Onboarding flow** - Preference collection and work pool generation
- **Profile management** - Update preferences and view reading statistics

### Daily Recommendations
- **Daily view** (`/daily`) - Shows today's poem, short story, and essay
- **Individual ratings** - Rate each work 1-5 stars via AJAX
- **Reading tracking** - Tracks completion status and reading history

### Recommendation System
- **Embedding-based matching** - Google Gemini API with 3072-dimensional vectors
- **Preference pipeline** - Raw preferences → summary → embedding → recommendations
- **Work pool system** - Pre-generates personalized recommendations with confidence scores
- **Real-time updates** - Pool regeneration when preferences change

### Content Library
- **90 total works** - Poems, short stories, and essays
- **77 works with URLs** - Direct links to Project Gutenberg HTML versions
- **Automatic URL finding** - Script to populate missing content links

## Routes Available

| Route | Method | Description |
|-------|---------|-------------|
| `/` | GET | Welcome page or redirect to daily view |
| `/register` | GET/POST | User registration |
| `/login` | GET/POST | User login |
| `/logout` | GET | User logout |
| `/onboarding` | GET/POST | Preference collection for new users |
| `/daily` | GET | Today's recommendations |
| `/daily-test` | GET | Test daily view (bypasses onboarding) |
| `/profile` | GET/POST | View/update user preferences and stats |
| `/generate-pool` | GET | Manually regenerate work pool |
| `/rate-recommendation` | POST | AJAX endpoint for rating works |

## How the Recommendation System Works

### Overview
The app uses an embedding-based recommendation system powered by Google Gemini API to match users with literary works based on their preferences.

### Process Flow
1. **Onboarding**: User provides preferences (books, authors, interests, things to avoid)
2. **Preference Processing**: Raw preferences → natural language summary → embedding vector
3. **Work Pool Generation**: Algorithm finds matching works and generates confidence scores
4. **Daily Selection**: System picks highest-confidence works not recently recommended
5. **User Feedback**: Ratings help improve future recommendations

### Key Components

**UserWorkPool System**
- Pre-generates personalized recommendations with confidence scores (0-1)
- Tracks recommendation history and prevents recent repeats
- Updates when preferences change

**Individual Recommendations** 
- Each work type (poem/story/essay) recommended independently
- after user onboards, calls populate_user_work_pool() to generate workpool for user
    - weighs embedding similarity and llm output
- Daily algorithm selects from user's available work pool
    - TODO: how to update work pool based on feedback?
- Ratings tracked per work for learning system

**Embedding Technology**
- Google Gemini API (gemini-embedding-001) with 3072-dimensional vectors
- Cosine similarity matching between user preferences and work content
- Cost-efficient: embeddings generated only during onboarding/profile updates

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