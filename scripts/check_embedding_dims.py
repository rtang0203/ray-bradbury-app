#!/usr/bin/env python3
"""
Check embedding dimensions in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import User, Work
import json

def check_embedding_dimensions():
    app = create_app()
    
    with app.app_context():
        print("🔍 Checking embedding dimensions in database")
        print("=" * 50)
        
        # Check Work embeddings
        print("\n📚 Work Embeddings:")
        works_with_embeddings = Work.query.filter(Work.embedding_vector.isnot(None)).limit(3).all()
        
        for work in works_with_embeddings:
            try:
                embedding = json.loads(work.embedding_vector)
                print(f"  '{work.title}': {len(embedding)} dimensions")
            except Exception as e:
                print(f"  '{work.title}': Error parsing - {e}")
        
        # Check User embeddings  
        print("\n👤 User Embeddings:")
        users_with_embeddings = User.query.filter(User.embedding_vector.isnot(None)).limit(3).all()
        
        for user in users_with_embeddings:
            try:
                embedding = json.loads(user.embedding_vector)
                print(f"  '{user.username}': {len(embedding)} dimensions")
            except Exception as e:
                print(f"  '{user.username}': Error parsing - {e}")
        
        # Summary
        print("\n📊 Summary:")
        if works_with_embeddings:
            sample_work_embedding = json.loads(works_with_embeddings[0].embedding_vector)
            print(f"Work embedding dimension: {len(sample_work_embedding)}")
        
        if users_with_embeddings:
            sample_user_embedding = json.loads(users_with_embeddings[0].embedding_vector)
            print(f"User embedding dimension: {len(sample_user_embedding)}")

if __name__ == "__main__":
    check_embedding_dimensions()