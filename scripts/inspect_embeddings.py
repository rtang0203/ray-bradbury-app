#!/usr/bin/env python3
"""
Inspect embedding values to see if they're zeros or real embeddings
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import User, Work
import json
# import numpy as np

def inspect_embeddings():
    app = create_app()
    
    with app.app_context():
        print("🔍 Inspecting embedding values")
        print("=" * 40)
        
        # Check Work embeddings
        print("\n📚 Work Embeddings:")
        work = Work.query.filter(Work.embedding_vector.isnot(None)).first()
        
        if work:
            embedding = json.loads(work.embedding_vector)
            
            print(f"Work: '{work.title}'")
            print(f"Dimensions: {len(embedding)}")
            print(f"First 10 values: {embedding[:10]}")
            print(f"Last 5 values: {embedding[-5:]}")
            
            # Check if all zeros (without numpy)
            all_zeros = all(x == 0.0 for x in embedding)
            print(f"All zeros? {all_zeros}")
            
            if not all_zeros:
                print(f"Min value: {min(embedding):.6f}")
                print(f"Max value: {max(embedding):.6f}")
                print(f"Sum: {sum(embedding):.6f}")
            else:
                print("This is a zero vector (fallback was used)")
        
        # Check User embeddings  
        print("\n👤 User Embeddings:")
        user = User.query.filter(User.embedding_vector.isnot(None)).first()
        
        if user:
            embedding = json.loads(user.embedding_vector)
            
            print(f"User: '{user.username}'")
            print(f"Dimensions: {len(embedding)}")
            print(f"First 10 values: {embedding[:10]}")
            print(f"Last 5 values: {embedding[-5:]}")
            
            # Check if all zeros (without numpy)
            all_zeros = all(x == 0.0 for x in embedding)
            print(f"All zeros? {all_zeros}")
            
            if not all_zeros:
                print(f"Min value: {min(embedding):.6f}")
                print(f"Max value: {max(embedding):.6f}")
                print(f"Sum: {sum(embedding):.6f}")
            else:
                print("This is a zero vector (fallback was used)")

if __name__ == "__main__":
    inspect_embeddings()