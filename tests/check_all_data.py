#!/usr/bin/env python3
"""
Check all data in the database
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app, db
from app.models import User, Work, UserWorkPool, WorkRecommendation

def check_all_data():
    """Check all data in the database"""
    app = create_app()

    with app.app_context():
        # Check all tables
        user_count = User.query.count()
        work_count = Work.query.count()
        pool_count = UserWorkPool.query.count()
        rec_count = WorkRecommendation.query.count()

        print("DATABASE OVERVIEW:")
        print(f"Users: {user_count}")
        print(f"Works: {work_count}")
        print(f"User Work Pool entries: {pool_count}")
        print(f"Work Recommendations: {rec_count}")

        # Check users with different criteria
        print(f"\nUSER ANALYSIS:")
        print(f"Total users: {User.query.count()}")
        print(f"Active users: {User.query.filter(User.active == True).count()}")
        print(f"Users with onboarding completed: {User.query.filter(User.onboarding_completed == True).count()}")
        print(f"Users with any preference_summary: {User.query.filter(User.preference_summary.isnot(None)).count()}")
        print(f"Users with non-empty preference_summary: {User.query.filter(User.preference_summary != '').count()}")
        print(f"Users with embedding_vector: {User.query.filter(User.embedding_vector.isnot(None)).count()}")

        # Show all users regardless of status
        all_users = User.query.all()
        print(f"\nALL USERS ({len(all_users)}):")
        for user in all_users:
            print(f"  {user.id}: {user.username} | Active: {user.active} | Onboarded: {user.onboarding_completed}")
            print(f"       Preferences: {'Yes' if user.preference_summary else 'No'}")
            print(f"       Embedding: {'Yes' if user.embedding_vector else 'No'}")

        # Check works
        works_with_embeddings = Work.query.filter(Work.embedding_vector.isnot(None)).count()
        print(f"\nWORK ANALYSIS:")
        print(f"Total works: {work_count}")
        print(f"Works with embeddings: {works_with_embeddings}")

        by_type = {}
        for work_type in ['poem', 'short_story', 'essay']:
            count = Work.query.filter(Work.work_type == work_type).count()
            with_embedding = Work.query.filter(
                Work.work_type == work_type,
                Work.embedding_vector.isnot(None)
            ).count()
            by_type[work_type] = {'total': count, 'with_embedding': with_embedding}

        for work_type, counts in by_type.items():
            print(f"  {work_type}: {counts['total']} total, {counts['with_embedding']} with embeddings")

if __name__ == '__main__':
    check_all_data()