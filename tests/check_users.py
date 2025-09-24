#!/usr/bin/env python3
"""
Check all users in the database and their preference/embedding status
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app, db
from app.models import User

def check_all_users():
    """Check all users in the database"""
    app = create_app()

    with app.app_context():
        # Get all users
        all_users = User.query.all()

        print(f"Found {len(all_users)} total users in database:")
        print("="*80)

        for i, user in enumerate(all_users, 1):
            print(f"{i}. Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Onboarding completed: {user.onboarding_completed}")
            print(f"   Has preference_summary: {'Yes' if user.preference_summary else 'No'}")
            if user.preference_summary:
                print(f"   Preference summary: {user.preference_summary[:100]}...")

            print(f"   Has embedding_vector: {'Yes' if user.embedding_vector else 'No'}")
            if user.embedding_vector:
                try:
                    embedding = json.loads(user.embedding_vector)
                    print(f"   Embedding vector length: {len(embedding)}")
                except:
                    print(f"   Embedding vector: Invalid JSON")

            print(f"   Active: {user.active}")
            print(f"   Created: {user.created_at}")
            print("-" * 50)

        # Summary stats
        print("\nSUMMARY STATISTICS:")
        total_users = len(all_users)
        onboarded_users = User.query.filter(User.onboarding_completed == True).count()
        users_with_preferences = User.query.filter(User.preference_summary.isnot(None)).count()
        users_with_embeddings = User.query.filter(User.embedding_vector.isnot(None)).count()
        users_ready_for_recs = User.query.filter(
            User.onboarding_completed == True,
            User.preference_summary.isnot(None),
            User.embedding_vector.isnot(None)
        ).count()

        print(f"Total users: {total_users}")
        print(f"Onboarded users: {onboarded_users}")
        print(f"Users with preferences: {users_with_preferences}")
        print(f"Users with embeddings: {users_with_embeddings}")
        print(f"Users ready for recommendations: {users_ready_for_recs}")

        # Show which users are ready for recommendations
        ready_users = User.query.filter(
            User.onboarding_completed == True,
            User.preference_summary.isnot(None),
            User.embedding_vector.isnot(None)
        ).all()

        if ready_users:
            print(f"\nUsers ready for recommendations ({len(ready_users)}):")
            for user in ready_users:
                print(f"  - {user.username}: {user.preference_summary[:60]}...")

        # Show users that need attention
        incomplete_users = User.query.filter(
            (User.onboarding_completed == False) |
            (User.preference_summary.is_(None)) |
            (User.embedding_vector.is_(None))
        ).all()

        if incomplete_users:
            print(f"\nUsers needing attention ({len(incomplete_users)}):")
            for user in incomplete_users:
                issues = []
                if not user.onboarding_completed:
                    issues.append("onboarding incomplete")
                if not user.preference_summary:
                    issues.append("no preferences")
                if not user.embedding_vector:
                    issues.append("no embedding")
                print(f"  - {user.username}: {', '.join(issues)}")

if __name__ == '__main__':
    check_all_users()