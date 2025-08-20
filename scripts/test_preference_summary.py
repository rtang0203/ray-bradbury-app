#!/usr/bin/env python3
"""
Test script for preference summary generation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User
from app.preference_utils import generate_preference_summary, update_user_preference_summary

def main():
    app = create_app()
    
    with app.app_context():
        print("=== PREFERENCE SUMMARY TEST ===\n")
        
        # Find users
        users = User.query.filter_by(onboarding_completed=True).all()
        
        if not users:
            print("No users with completed onboarding found.")
            return
        
        for user in users:
            print(f"User: {user.username}")
            print(f"Basic settings: {user.difficulty_preference} difficulty, {user.preferred_length} length, {user.adventurousness_level:.2f} adventurousness")
            
            # Generate summary
            summary = generate_preference_summary(user.id)
            print(f"Generated summary:\n{summary}")
            
            # Update in database
            success = update_user_preference_summary(user.id)
            print(f"Saved to database: {'✓' if success else '✗'}")
            
            # Show what's now in database
            user_refreshed = User.query.get(user.id)
            print(f"Database summary:\n{user_refreshed.preference_summary}")
            
            print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()