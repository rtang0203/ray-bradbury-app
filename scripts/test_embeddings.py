#!/usr/bin/env python3
"""
Test script for embedding generation using existing methods.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Work
from app.recommendations_embeddings import EmbeddingRecommendationEngine
import json

def test_embedding_system():
    """Test the complete embedding system"""
    print("🚀 Testing Embedding System")
    print("=" * 40)
    
    app = create_app()
    
    with app.app_context():
        engine = EmbeddingRecommendationEngine()
        
        # Step 1: Generate work embeddings
        print("\n📚 Generating work embeddings...")
        works = Work.query.filter_by(active=True).all()
        print(f"Found {len(works)} active works")
        
        if not works:
            print("❌ No works found. Please seed content first.")
            return False
        
        try:
            # Use existing method - pass works or let it default to all
            engine.generate_work_embeddings(works, regenerate=True)
            print("✅ Work embeddings completed!")
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        
        # Step 2: Generate user embeddings
        print("\n👤 Generating user embeddings...")
        users = User.query.filter(
            User.preference_summary.isnot(None),
            User.onboarding_completed == True
        ).all()
        print(f"Found {len(users)} users with preferences")
        
        if not users:
            print("❌ No users with preferences found.")
            return False
        
        try:
            for user in users:
                # Force regenerate to ensure consistent dimensions
                print(f"  Regenerating for: {user.username}")
                embedding = engine.generate_user_embedding(user)
                user.embedding_vector = json.dumps(embedding)
                print(f"    New embedding dimension: {len(embedding)}")
            
            db.session.commit()
            print("✅ User embeddings completed!")
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
        
        # Step 3: Test similarity
        print("\n🔍 Testing similarity...")
        test_user = users[0]
        print(f"Testing with: {test_user.username}")
        
        try:
            similar_poems = engine.find_similar_works(test_user.id, 'poem', top_k=3)
            print(f"\nTop poems for {test_user.username}:")
            for i, item in enumerate(similar_poems, 1):
                work = item['work']
                score = item['similarity_score']
                print(f"  {i}. {work.title} by {work.author} ({score:.3f})")
                
        except Exception as e:
            print(f"❌ Similarity test failed: {e}")
            return False
        
        print("\n🎉 All tests passed!")
        return True

if __name__ == "__main__":
    success = test_embedding_system()
    if not success:
        print("💡 Check your .env file and database content")