#!/usr/bin/env python3
"""
Test script for the recommendation system.
Run this to test the recommendation logic with existing data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Work, UserWorkPool, DailyRecommendationSet, WorkRecommendation
from app.recommendations import populate_user_work_pool, get_daily_recommendations
from datetime import date

def main():
    app = create_app()
    
    with app.app_context():
        print("=== RECOMMENDATION SYSTEM TEST ===\n")
        
        # 1. Check database state
        print("1. DATABASE STATE:")
        users = User.query.all()
        works = Work.query.all()
        poems = Work.query.filter_by(work_type='poem').count()
        stories = Work.query.filter_by(work_type='short_story').count()
        essays = Work.query.filter_by(work_type='essay').count()
        
        print(f"   Total users: {len(users)}")
        print(f"   Total works: {len(works)} (Poems: {poems}, Stories: {stories}, Essays: {essays})")
        
        if not users:
            print("   ERROR: No users found! Please register a user first.")
            return
        
        if poems == 0 or stories == 0 or essays == 0:
            print("   ERROR: Missing works in one or more categories!")
            return
        
        user = users[0]
        print(f"   Testing with user: {user.username} (ID: {user.id})")
        
        # 2. Check existing user work pool
        print(f"\n2. USER WORK POOL (User: {user.username}):")
        pool_count = UserWorkPool.query.filter_by(user_id=user.id).count()
        print(f"   Works in pool: {pool_count}")
        
        if pool_count == 0:
            print("   No works in pool. Generating...")
            try:
                success = populate_user_work_pool(user.id)
                if success:
                    pool_count = UserWorkPool.query.filter_by(user_id=user.id).count()
                    print(f"   ✓ Generated {pool_count} works in pool")
                else:
                    print("   ✗ Failed to generate work pool")
                    return
            except Exception as e:
                print(f"   ✗ Error generating pool: {e}")
                return
        
        # Show pool breakdown
        pool_poems = UserWorkPool.query.filter_by(user_id=user.id, work_type='poem').count()
        pool_stories = UserWorkPool.query.filter_by(user_id=user.id, work_type='short_story').count()
        pool_essays = UserWorkPool.query.filter_by(user_id=user.id, work_type='essay').count()
        print(f"   Pool breakdown: Poems: {pool_poems}, Stories: {pool_stories}, Essays: {pool_essays}")
        
        # Show top confidence works for each type
        print(f"\n   Top confidence works:")
        for work_type in ['poem', 'short_story', 'essay']:
            top_work = UserWorkPool.query.filter_by(
                user_id=user.id, 
                work_type=work_type,
                status='available'
            ).order_by(UserWorkPool.confidence_score.desc()).first()
            
            if top_work:
                print(f"   {work_type}: {top_work.work.title} by {top_work.work.author} (confidence: {top_work.confidence_score:.2f})")
        
        # 3. Test daily recommendations
        print(f"\n3. DAILY RECOMMENDATIONS:")
        today = date.today()
        existing_set = DailyRecommendationSet.query.filter_by(
            user_id=user.id,
            date=today
        ).first()
        
        if existing_set:
            print(f"   Existing recommendations for {today}:")
            if existing_set.poem_rec:
                print(f"   Poem: {existing_set.poem_rec.work.title} by {existing_set.poem_rec.work.author}")
            if existing_set.story_rec:
                print(f"   Story: {existing_set.story_rec.work.title} by {existing_set.story_rec.work.author}")
            if existing_set.essay_rec:
                print(f"   Essay: {existing_set.essay_rec.work.title} by {existing_set.essay_rec.work.author}")
        else:
            print(f"   No recommendations for {today}. Generating...")
            try:
                daily_set = get_daily_recommendations(user.id, today, regenerate=True)
                if daily_set:
                    print(f"   ✓ Generated recommendations for {today}")
                    print(f"   Poem: {daily_set.poem_rec.work.title} by {daily_set.poem_rec.work.author}")
                    print(f"   Story: {daily_set.story_rec.work.title} by {daily_set.story_rec.work.author}")
                    print(f"   Essay: {daily_set.essay_rec.work.title} by {daily_set.essay_rec.work.author}")
                else:
                    print("   ✗ Failed to generate daily recommendations")
            except Exception as e:
                print(f"   ✗ Error generating recommendations: {e}")
        
        # 4. Show recommendation history
        print(f"\n4. RECOMMENDATION HISTORY:")
        all_recommendations = WorkRecommendation.query.filter_by(user_id=user.id).count()
        daily_sets = DailyRecommendationSet.query.filter_by(user_id=user.id).count()
        print(f"   Total individual recommendations: {all_recommendations}")
        print(f"   Total daily sets: {daily_sets}")
        
        # 5. Show pool status after recommendations
        print(f"\n5. WORK POOL STATUS AFTER RECOMMENDATIONS:")
        available = UserWorkPool.query.filter_by(user_id=user.id, status='available').count()
        recommended = UserWorkPool.query.filter_by(user_id=user.id, status='recommended').count()
        exhausted = UserWorkPool.query.filter_by(user_id=user.id, status='exhausted').count()
        
        print(f"   Available: {available}")
        print(f"   Recommended: {recommended}")
        print(f"   Exhausted: {exhausted}")
        
        print(f"\n=== TEST COMPLETE ===")
        print(f"Recommendation system is working! Visit /daily to see recommendations.")

if __name__ == "__main__":
    main()