#!/usr/bin/env python3
"""
Test script for embedding-based recommendation integration.
Run this to verify the embedding system works with existing routes.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.recommendations import populate_user_work_pool, get_daily_recommendations
from app.models import User, UserWorkPool, Work
from datetime import date

def test_embedding_integration():
    """Test the embedding-based recommendation system integration"""
    
    print("🧪 Testing Embedding Integration")
    print("=" * 50)
    
    app = create_app()
    with app.app_context():
        # Find a user with preference summary (completed onboarding)
        user = User.query.filter(User.preference_summary.isnot(None)).first()
        
        if not user:
            print("❌ No users with preference summary found")
            print("   Please complete user onboarding first")
            return False
            
        print(f"👤 Testing with user: {user.username} (ID: {user.id})")
        print(f"📝 Preference summary: {user.preference_summary[:100]}...")
        
        # Check if works have embeddings
        works_with_embeddings = Work.query.filter(Work.embedding_vector.isnot(None)).count()
        total_works = Work.query.count()
        print(f"📚 Works with embeddings: {works_with_embeddings}/{total_works}")
        
        if works_with_embeddings == 0:
            print("❌ No works have embeddings yet")
            print("   Run: python scripts/generate_embeddings.py")
            return False
            
        # Clear existing pool to test fresh
        existing_count = UserWorkPool.query.filter_by(user_id=user.id).count()
        print(f"🗄️  Existing pool size: {existing_count}")
        
        # Test populate_user_work_pool function
        print("\n🔄 Testing populate_user_work_pool...")
        try:
            result = populate_user_work_pool(user.id)
            print(f"✅ Population result: {result}")
            
            # Check new pool size
            new_count = UserWorkPool.query.filter_by(user_id=user.id).count()
            print(f"📊 New pool size: {new_count}")
            
            if new_count == 0:
                print("⚠️  Warning: No works added to pool")
                return False
                
        except Exception as e:
            print(f"❌ Error in populate_user_work_pool: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        # Show top recommendations by category
        print("\n🏆 Top 3 recommendations by category:")
        for work_type in ['poem', 'short_story', 'essay']:
            entries = UserWorkPool.query.filter_by(
                user_id=user.id, 
                work_type=work_type
            ).order_by(UserWorkPool.confidence_score.desc()).limit(3).all()
            
            print(f"\n  {work_type.replace('_', ' ').title()}s:")
            if not entries:
                print("    No recommendations found")
            else:
                for entry in entries:
                    print(f"    • {entry.work.title} by {entry.work.author}")
                    print(f"      Confidence: {entry.confidence_score:.3f}")
        
        # Test daily recommendation generation
        print(f"\n📅 Testing daily recommendations for {date.today()}...")
        try:
            daily_recs = get_daily_recommendations(user.id,regenerate=True)
            
            print("Daily recommendations:")
            for work_type, rec in daily_recs.items():
                if rec:
                    print(f"  {work_type}: {rec.work.title} by {rec.work.author}")
                else:
                    print(f"  {work_type}: No recommendation generated")
                    
        except Exception as e:
            print(f"❌ Error in daily recommendations: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        print(f"\n✅ Integration test completed successfully!")
        return True

if __name__ == "__main__":
    success = test_embedding_integration()
    sys.exit(0 if success else 1)