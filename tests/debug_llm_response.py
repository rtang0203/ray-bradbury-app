#!/usr/bin/env python3
"""
Debug script to see what the LLM is actually returning
"""
import os
import sys

# Add the parent directory to Python path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import create_app, db
from app.models import User, Work
from app.embeddings_engine import EmbeddingRecommendationEngine

def debug_llm_response():
    """Debug what the LLM is actually returning"""
    app = create_app()

    with app.app_context():
        # Get a real user
        user = User.query.filter(
            User.onboarding_completed == True,
            User.preference_summary.isnot(None)
        ).first()

        if not user:
            print("No user found with preferences")
            return

        # Get some works
        works = Work.query.filter(Work.embedding_vector.isnot(None)).limit(2).all()

        if not works:
            print("No works found with embeddings")
            return

        print(f"Testing with user: {user.username}")
        print(f"User preferences: {user.preference_summary}")
        print(f"\nTesting with {len(works)} works:")
        for work in works:
            print(f"  - {work.title} by {work.author}")

        # Test the LLM directly and see raw response
        engine = EmbeddingRecommendationEngine()

        # Build the same prompt that _llm_score_candidates uses
        works_text = ""
        for i, work in enumerate(works):
            works_text += f"{i+1}. ID: {work.id} | {work.title} by {work.author} | {work.work_type}\n"
            if work.summary:
                works_text += f"   Summary: {work.summary[:200]}...\n"
            works_text += "\n"

        prompt = f"""
        User's Reading Preferences:
        {user.preference_summary}

        Based on these preferences, rate how well each work would match this user's taste.
        Consider genre preferences, themes, writing style, difficulty level, and personal interests.

        Rate each work from 0.0 (terrible match) to 1.0 (perfect match).

        Works to evaluate:
        {works_text}

        Respond with JSON format: {{"work_id": confidence_score}}
        Example: {{"123": 0.85, "124": 0.62, "125": 0.91}}
        """

        print("\n" + "="*50)
        print("PROMPT SENT TO LLM:")
        print(prompt)
        print("="*50)

        try:
            # Make the API call directly
            response = engine.client.models.generate_content(
                model=engine.llm_model,
                contents=prompt
            )

            print("\nRAW LLM RESPONSE:")
            print(f"Response text: '{response.text}'")
            print(f"Response text type: {type(response.text)}")
            print(f"Response text length: {len(response.text) if response.text else 'None'}")

            if hasattr(response, 'candidates') and response.candidates:
                print(f"Number of candidates: {len(response.candidates)}")
                for i, candidate in enumerate(response.candidates):
                    print(f"  Candidate {i}: {candidate}")

            # Try to parse as JSON
            if response.text:
                try:
                    import json
                    parsed = json.loads(response.text)
                    print(f"\n✅ Successfully parsed JSON: {parsed}")
                except json.JSONDecodeError as e:
                    print(f"\n❌ JSON parse error: {e}")
                    print(f"Attempting to extract JSON from response...")

                    # Try to find JSON in the response
                    text = response.text
                    start = text.find('{')
                    end = text.rfind('}') + 1
                    if start != -1 and end > start:
                        json_part = text[start:end]
                        print(f"Extracted JSON candidate: '{json_part}'")
                        try:
                            parsed = json.loads(json_part)
                            print(f"✅ Successfully parsed extracted JSON: {parsed}")
                        except json.JSONDecodeError as e2:
                            print(f"❌ Still couldn't parse extracted JSON: {e2}")
            else:
                print("\n❌ Response text is empty")

        except Exception as e:
            print(f"\n❌ API call failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    debug_llm_response()