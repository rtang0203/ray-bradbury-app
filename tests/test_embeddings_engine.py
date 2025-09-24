"""
Test script for generate_hybrid_recommendations and _llm_score_candidates functions
"""
import os
import sys
import json
import tempfile
from unittest.mock import Mock, patch, MagicMock

# Add the parent directory to Python path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import tempfile
from app.models import User, Work, UserWorkPool
from app.embeddings_engine import EmbeddingRecommendationEngine

# Create separate test database instance to avoid affecting main app
'''THIS DOESNT WORK BECAUSE MODELS STILL POINT TO app.db. fix later??? fuck this'''
test_db = SQLAlchemy()
test_login_manager = LoginManager()

def create_test_app():
    """Create an isolated test Flask app that won't affect development database"""
    app = Flask(__name__)

    # Use temporary database file for complete isolation
    test_db_file = tempfile.mkstemp(suffix='.db')[1]
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{test_db_file}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['GEMINI_API_KEY'] = 'test-key'

    # Initialize with isolated app
    test_db.init_app(app)
    test_login_manager.init_app(app)

    # Important: Create tables within app context so models are bound to our test DB
    with app.app_context():
        test_db.create_all()

    return app

def create_test_data(app):
    """Create test data for the functions"""
    with app.app_context():
        # Tables already created in create_test_app()

        # Create test user
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash='dummy_hash',
            preference_summary='I love classic literature, especially romantic poetry and philosophical essays. I enjoy works by Shakespeare, Dickinson, and Thoreau. I prefer medium-length works that are intellectually stimulating.',
            embedding_vector=json.dumps([0.1] * 3072),  # Mock embedding
            onboarding_completed=True
        )
        test_db.session.add(user)

        # Create test works
        works_data = [
            {
                'title': 'Sonnet 18',
                'author': 'William Shakespeare',
                'work_type': 'poem',
                'summary': 'A beautiful sonnet comparing the beloved to a summer day',
                'themes': 'love, beauty, immortality',
                'genres': 'romantic, classical',
                'embedding_vector': json.dumps([0.8] + [0.1] * 3071)  # High similarity
            },
            {
                'title': 'Because I could not stop for Death',
                'author': 'Emily Dickinson',
                'work_type': 'poem',
                'summary': 'A contemplation on death and eternity',
                'themes': 'death, eternity, journey',
                'genres': 'philosophical, classical',
                'embedding_vector': json.dumps([0.7] + [0.1] * 3071)  # Medium-high similarity
            },
            {
                'title': 'Civil Disobedience',
                'author': 'Henry David Thoreau',
                'work_type': 'essay',
                'summary': 'An essay on resistance to civil government',
                'themes': 'government, resistance, conscience',
                'genres': 'philosophical, political',
                'embedding_vector': json.dumps([0.6] + [0.1] * 3071)  # Medium similarity
            },
            {
                'title': 'The Lottery',
                'author': 'Shirley Jackson',
                'work_type': 'short_story',
                'summary': 'A disturbing tale of a small town tradition',
                'themes': 'tradition, violence, conformity',
                'genres': 'horror, social commentary',
                'embedding_vector': json.dumps([0.2] + [0.1] * 3071)  # Low similarity
            }
        ]

        for work_data in works_data:
            work = Work(**work_data)
            test_db.session.add(work)

        test_db.session.commit()
        return user.id

def test_llm_score_candidates():
    """Test the _llm_score_candidates function"""
    print("Testing _llm_score_candidates function...")

    app = create_test_app()

    with app.app_context():
        user_id = create_test_data(app)
        user = User.query.get(user_id)
        works = Work.query.all()

        # Mock the Gemini API client
        with patch('app.embeddings_engine.genai.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Mock successful LLM response
            mock_response = Mock()
            mock_response.text = json.dumps({
                str(works[0].id): 0.9,  # Shakespeare sonnet - high score
                str(works[1].id): 0.85, # Dickinson poem - high score
                str(works[2].id): 0.7,  # Thoreau essay - medium score
                str(works[3].id): 0.3   # Horror story - low score
            })
            mock_client.models.generate_content.return_value = mock_response

            # Test the function
            engine = EmbeddingRecommendationEngine()
            scores = engine._llm_score_candidates(user, works)

            # Verify results
            print(f"✓ LLM scores returned: {scores}")
            assert len(scores) == 4, f"Expected 4 scores, got {len(scores)}"
            assert str(works[0].id) in scores, "Shakespeare sonnet should be scored"
            assert scores[str(works[0].id)] == 0.9, "Shakespeare sonnet should have high score"
            assert scores[str(works[3].id)] == 0.3, "Horror story should have low score"

            # Verify the API was called with correct prompt structure
            call_args = mock_client.models.generate_content.call_args
            assert call_args is not None, "API should have been called"
            prompt = call_args[1]['contents']
            assert 'User\'s Reading Preferences:' in prompt, "Prompt should contain user preferences"
            assert user.preference_summary in prompt, "Prompt should contain user's actual preferences"
            assert 'Shakespeare' in prompt, "Prompt should contain work details"

            print("✓ _llm_score_candidates test passed!")

def test_llm_score_candidates_error_handling():
    """Test _llm_score_candidates error handling"""
    print("Testing _llm_score_candidates error handling...")

    app = create_test_app()

    with app.app_context():
        user_id = create_test_data(app)
        user = User.query.get(user_id)
        works = Work.query.all()

        # Mock the Gemini API client to raise an exception
        with patch('app.embeddings_engine.genai.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.models.generate_content.side_effect = Exception("API Error")

            # Test the function
            engine = EmbeddingRecommendationEngine()
            scores = engine._llm_score_candidates(user, works)

            # Verify fallback behavior
            print(f"✓ Fallback scores returned: {scores}")
            assert len(scores) == 4, f"Expected 4 fallback scores, got {len(scores)}"
            for work in works:
                assert str(work.id) in scores, f"Work {work.id} should have fallback score"
                assert scores[str(work.id)] == 0.5, "Fallback score should be 0.5"

            print("✓ _llm_score_candidates error handling test passed!")

def test_generate_hybrid_recommendations():
    """Test the generate_hybrid_recommendations function"""
    print("Testing generate_hybrid_recommendations function...")

    app = create_test_app()

    with app.app_context():
        user_id = create_test_data(app)

        # Mock the Gemini API client
        with patch('app.embeddings_engine.genai.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Mock LLM response for scoring
            mock_response = Mock()
            works = Work.query.filter_by(work_type='poem').all()
            llm_scores = {}
            for work in works:
                # Give higher LLM scores to works with lower embedding similarity for testing
                if 'Shakespeare' in work.author:
                    llm_scores[str(work.id)] = 0.6  # Lower LLM score
                else:
                    llm_scores[str(work.id)] = 0.9  # Higher LLM score

            mock_response.text = json.dumps(llm_scores)
            mock_client.models.generate_content.return_value = mock_response

            # Test the function
            engine = EmbeddingRecommendationEngine()
            recommendations = engine.generate_hybrid_recommendations(user_id, 'poem', 5)

            # Verify results
            print(f"✓ Generated {len(recommendations)} hybrid recommendations")
            assert len(recommendations) <= 5, "Should not exceed requested number"
            assert len(recommendations) > 0, "Should return at least one recommendation"

            for rec in recommendations:
                print(f"  - {rec['work'].title} by {rec['work'].author}")
                print(f"    Combined: {rec['confidence_score']:.3f}, Embedding: {rec['embedding_score']:.3f}, LLM: {rec['llm_score']:.3f}")

                # Verify structure
                assert 'work' in rec, "Recommendation should contain work"
                assert 'confidence_score' in rec, "Should have combined confidence score"
                assert 'embedding_score' in rec, "Should have embedding score"
                assert 'llm_score' in rec, "Should have LLM score"

                # Verify score ranges
                assert 0 <= rec['confidence_score'] <= 1, "Combined score should be 0-1"
                assert 0 <= rec['embedding_score'] <= 1, "Embedding score should be 0-1"
                assert 0 <= rec['llm_score'] <= 1, "LLM score should be 0-1"

            # Verify recommendations are sorted by confidence score (descending)
            for i in range(len(recommendations) - 1):
                assert recommendations[i]['confidence_score'] >= recommendations[i+1]['confidence_score'], \
                    "Recommendations should be sorted by confidence score"

            print("✓ generate_hybrid_recommendations test passed!")

def test_hybrid_recommendations_few_candidates():
    """Test hybrid recommendations with fewer candidates than requested"""
    print("Testing generate_hybrid_recommendations with few candidates...")

    app = create_test_app()

    with app.app_context():
        user_id = create_test_data(app)

        # Mock the Gemini API client - now it will always be called
        with patch('app.embeddings_engine.genai.Client') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client

            # Mock LLM response for the single essay
            essay_work = Work.query.filter_by(work_type='essay').first()
            mock_response = Mock()
            mock_response.text = json.dumps({str(essay_work.id): 0.8})
            mock_client.models.generate_content.return_value = mock_response

            # Test with work type that has only 1 work
            engine = EmbeddingRecommendationEngine()
            recommendations = engine.generate_hybrid_recommendations(user_id, 'essay', 5)

            # Should return the available work with hybrid scoring
            print(f"✓ Generated {len(recommendations)} recommendations for limited candidates")
            assert len(recommendations) == 1, "Should return the only available essay"
            assert recommendations[0]['work'].work_type == 'essay'

            # Verify proper hybrid structure
            assert 'confidence_score' in recommendations[0], "Should have confidence score"
            assert 'embedding_score' in recommendations[0], "Should have embedding score"
            assert 'llm_score' in recommendations[0], "Should have LLM score"

            # Verify LLM was called since we now always use hybrid scoring
            mock_client.models.generate_content.assert_called_once()

            print("✓ Few candidates test passed!")

def test_hybrid_recommendations_no_embedding():
    """Test hybrid recommendations when user has no embedding"""
    print("Testing generate_hybrid_recommendations with no user embedding...")

    app = create_test_app()

    with app.app_context():
        create_test_data(app)

        # Create user without embedding
        user_no_embedding = User(
            username='no_embedding_user',
            email='no_embedding@example.com',
            password_hash='dummy_hash',
            preference_summary='I have preferences but no embedding',
            embedding_vector=None,
            onboarding_completed=True
        )
        test_db.session.add(user_no_embedding)
        test_db.session.commit()

        # Test the function
        engine = EmbeddingRecommendationEngine()
        recommendations = engine.generate_hybrid_recommendations(user_no_embedding.id, 'poem', 5)

        # Should return empty list
        print(f"✓ Generated {len(recommendations)} recommendations for user without embedding")
        assert len(recommendations) == 0, "Should return empty list for user without embedding"

        print("✓ No embedding test passed!")

def run_all_tests():
    """Run all test functions"""
    print("Running embeddings engine tests...\n")

    try:
        test_llm_score_candidates()
        print()

        test_llm_score_candidates_error_handling()
        print()

        test_generate_hybrid_recommendations()
        print()

        test_hybrid_recommendations_few_candidates()
        print()

        test_hybrid_recommendations_no_embedding()
        print()

        print("🎉 All tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)