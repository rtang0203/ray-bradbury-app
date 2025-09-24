#!/usr/bin/env python3
"""
Real-world test script for generate_hybrid_recommendations and _llm_score_candidates
This script uses actual database data and makes real API calls to Gemini
"""
import os
import sys
import json
from datetime import datetime

# Add the parent directory to Python path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app, db
from app.models import User, Work, UserWorkPool
from app.embeddings_engine import EmbeddingRecommendationEngine

def test_real_recommendations():
    """Test with actual users and API calls"""
    app = create_app()

    with app.app_context():
        # Get actual users from database
        users = User.query.filter(
            User.onboarding_completed == True,
            User.preference_summary.isnot(None)
        ).all()

        if not users:
            print("❌ No users found with completed onboarding and preferences")
            return False

        print(f"Found {len(users)} users with preferences:")
        for user in users:
            print(f"  - {user.username}: {user.preference_summary[:100]}...")

        # Get available works by type
        work_counts = {}
        for work_type in ['poem', 'short_story', 'essay']:
            count = Work.query.filter(
                Work.work_type == work_type,
                Work.embedding_vector.isnot(None)
            ).count()
            work_counts[work_type] = count

        print(f"\nWork counts with embeddings: {work_counts}")

        if sum(work_counts.values()) == 0:
            print("❌ No works found with embeddings")
            return False

        # Test the functions
        engine = EmbeddingRecommendationEngine()
        test_user = users[1]  # Use first user

        print(f"\n🧪 Testing with user: {test_user.username}")
        print(f"User preferences: {test_user.preference_summary}")

        # Test each work type that has available works
        for work_type in ['poem', 'short_story', 'essay']:
            if work_counts[work_type] == 0:
                print(f"\n⏭️  Skipping {work_type} - no works with embeddings")
                continue

            print(f"\n📚 Testing {work_type} recommendations...")

            try:
                # Test _llm_score_candidates directly
                print("  Testing _llm_score_candidates...")
                candidate_works = Work.query.filter(
                    Work.work_type == work_type,
                    Work.embedding_vector.isnot(None)
                ).limit(5).all()

                if not candidate_works:
                    print(f"    ⏭️  No {work_type} works found")
                    continue

                print(f"    Scoring {len(candidate_works)} works with Gemini API...")
                scores = engine._llm_score_candidates(test_user, candidate_works)

                print(f"    ✅ LLM Scores received:")
                for work in candidate_works:
                    score = scores.get(str(work.id), 'N/A')
                    print(f"      {work.title} by {work.author}: {score}")

                # Test generate_hybrid_recommendations
                print(f"\n  Testing generate_hybrid_recommendations for {work_type}...")
                recommendations = engine.generate_hybrid_recommendations(
                    test_user.id,
                    work_type,
                    num_final_recommendations=3
                )

                print(f"    ✅ Generated {len(recommendations)} hybrid recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    work = rec['work']
                    print(f"      {i}. {work.title} by {work.author}")
                    print(f"         Combined: {rec['confidence_score']:.3f} | "
                          f"Embedding: {rec['embedding_score']:.3f} | "
                          f"LLM: {rec['llm_score']:.3f}")

                    # Show some work details
                    if work.themes:
                        print(f"         Themes: {work.themes}")
                    if work.summary:
                        print(f"         Summary: {work.summary[:100]}...")

                print(f"    ✅ {work_type.replace('_', ' ').title()} test completed successfully!")

            except Exception as e:
                print(f"    ❌ Error testing {work_type}: {e}")
                import traceback
                traceback.print_exc()
                continue

        return True

def test_api_connectivity():
    """Test basic API connectivity"""
    print("🔗 Testing Gemini API connectivity...")

    app = create_app()

    with app.app_context():
        try:
            engine = EmbeddingRecommendationEngine()

            # Test embedding generation
            test_text = "A beautiful romantic poem about love and nature"
            embedding = engine._get_embedding(test_text)

            if embedding and len(embedding) > 0:
                print(f"  ✅ Embedding API working - got vector of length {len(embedding)}")
            else:
                print("  ❌ Embedding API returned empty result")
                return False

            # Test LLM with a simple mock user and work
            from app.models import User, Work
            mock_user = User(preference_summary="I enjoy classic literature and poetry")
            mock_work = Work(
                id=999,
                title="Test Poem",
                author="Test Author",
                work_type="poem",
                summary="A test poem about testing"
            )

            scores = engine._llm_score_candidates(mock_user, [mock_work])

            if scores and '999' in scores:
                print(f"  ✅ LLM API working - got score: {scores['999']}")
            else:
                print(f"  ❌ LLM API returned unexpected result: {scores}")
                return False

            print("  ✅ API connectivity test passed!")
            return True

        except Exception as e:
            print(f"  ❌ API connectivity test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main test runner"""
    print("🚀 Starting real-world recommendation engine tests...")
    print(f"Timestamp: {datetime.now()}")

    # Test API connectivity first
    if not test_api_connectivity():
        print("\n❌ API connectivity failed - aborting tests")
        return False

    print("\n" + "="*60)

    # Test with real data
    success = test_real_recommendations()

    print("\n" + "="*60)

    if success:
        print("🎉 All real-world tests completed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)