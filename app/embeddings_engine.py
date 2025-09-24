from google import genai
from google.genai import types
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
from flask import current_app
from .models import User, Work, UserWorkPool, db

'''
Implementation Strategy for Embedding Recommendation Engine

1. Start simple: Add the embedding column and generate embeddings for existing works
2. Test similarity: Try the find_similar_works() function to see how well it works
3. Refine descriptions: Tune the work/user description formats based on results
4. Add hybrid scoring: Layer in the LLM refinement step
5. Optimize weights: Tune the embedding vs LLM score combination

'''

class EmbeddingRecommendationEngine:
    def __init__(self):
        self.client = genai.Client(api_key=current_app.config['GEMINI_API_KEY'])
        self.llm_model = "gemini-2.5-flash-lite"
        self.embedding_model = "gemini-embedding-001"  # using gemini free tier for now
        self.embedding_dim = 3072  # Dimension of the embedding vectors. lets just use default 3096 since it is normalized
        self.num_final_recommendations = 30  # Default number of recommendations per category
    
    def _get_embedding(self, text):
        """Get embedding for text using Gemini API"""
        try:
            result = self.client.models.embed_content(
                model=self.embedding_model,
                contents=text.replace("\n", " "),  # Clean up text
                config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
            )
            # Extract the actual embedding values from the ContentEmbedding object
            [embedding_obj] = result.embeddings
            return embedding_obj.values
        except Exception as e:
            print(f"Embedding error: {e}")
            return [0.0] * self.embedding_dim  # Return zero vector as fallback
        
    # STEP 1: Generate embeddings for all works (run once when adding works)
    def generate_work_embeddings(self, works=None, regenerate=False):
        """Generate embeddings for all works in the database"""
        if works is None:
            works = Work.query.all()
            
        for work in works:
            if work.embedding_vector is None or regenerate:  # Only generate if not exists
                # Create rich text representation of the work
                work_text = self._create_work_description(work)
                
                # Generate embedding
                embedding = self._get_embedding(work_text)
                
                # Store as JSON in database
                work.embedding_vector = json.dumps(embedding)
                
        db.session.commit()
        print(f"Generated embeddings for {len(works)} works")
    
    def _create_work_description(self, work):
        """Create rich text description for embedding generation"""
        description_parts = [
            f"Title: {work.title}",
            f"Author: {work.author}",
            f"Type: {work.work_type}",  # poem, short_story, essay
        ]
        
        if work.themes:
            description_parts.append(f"Themes: {work.themes}")
        if work.genres:
            description_parts.append(f"Genres: {work.genres}")
        if work.summary:
            description_parts.append(f"Summary: {work.summary}")
        
        return " | ".join(description_parts)
    
    # STEP 2: Generate user preference embedding
    def generate_user_embedding(self, user):
        """Generate embedding for user's preferences"""
        
        # Use the natural language preference summary you already have
        user_text = self._create_user_description(user)
        
        # Generate and return embedding
        return self._get_embedding(user_text)
    
    def _create_user_description(self, user):
        """Create description of user preferences for embedding generation"""
        # For now, just return the preference summary
        # Later we can enhance this with LLM refinement or additional user data
        return user.preference_summary or "No preferences specified"
    
    # STEP 3: Find similar works using cosine similarity
    def find_similar_works(self, user_id, work_type=None, top_k=100):
        """Find works most similar to user's preferences"""
        
        user = User.query.get(user_id)
        if not user or not user.embedding_vector:
            return []
            
        try:
            user_embedding = json.loads(user.embedding_vector)
        except (json.JSONDecodeError, TypeError):
            return []
        
        # Get all works (or filter by type)
        query = Work.query.filter(Work.embedding_vector.isnot(None))
        if work_type:
            query = query.filter(Work.work_type == work_type)
        works = query.all()
        
        if not works:
            return []
        
        # Convert stored embeddings back to numpy arrays
        work_embeddings = []
        work_objects = []
        
        for work in works:
            try:
                embedding = json.loads(work.embedding_vector)
                work_embeddings.append(embedding)
                work_objects.append(work)
            except (json.JSONDecodeError, TypeError):
                continue
        
        if not work_embeddings:
            return []
            
        work_embeddings = np.array(work_embeddings)
        user_embedding = np.array(user_embedding).reshape(1, -1)
        
        # Calculate cosine similarities
        similarities = cosine_similarity(user_embedding, work_embeddings)[0]
        
        # Get top K most similar works
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        similar_works = []
        for idx in top_indices:
            similar_works.append({
                'work': work_objects[idx],
                'similarity_score': float(similarities[idx])
            })
        
        return similar_works
    
    # STEP 3.5: Embedding-only recommendations (simpler, faster)
    def generate_embedding_recommendations(self, user_id, work_type, num_final_recommendations=None):
        """Generate recommendations using only embedding similarity (no LLM)"""
        if num_final_recommendations is None:
            num_final_recommendations = self.num_final_recommendations
            
        similar_works = self.find_similar_works(
            user_id, 
            work_type=work_type, 
            top_k=num_final_recommendations
        )
        
        # Convert to format expected by populate_user_work_pool
        recommendations = []
        for item in similar_works:
            recommendations.append({
                'work': item['work'],
                'confidence_score': item['similarity_score'],
                'embedding_score': item['similarity_score']
            })
        
        return recommendations
    
    # STEP 4: Hybrid approach - embeddings + LLM
    def generate_hybrid_recommendations(self, user_id, work_type, num_final_recommendations=None):
        """Use embeddings to pre-filter, then LLM to fine-tune"""
        if num_final_recommendations is None:
            num_final_recommendations = self.num_final_recommendations
        
        # Phase 1: Use embeddings to get top candidates (fast, cheap)
        similar_works = self.find_similar_works(
            user_id, 
            work_type=work_type, 
            top_k=50  # Get top 50 candidates
        )
        
        # Phase 2: Use LLM to refine the top candidates (slower, more expensive but better)
        user = User.query.get(user_id)
        candidate_works = [item['work'] for item in similar_works]
        
        llm_scores = self._llm_score_candidates(user, candidate_works)
        
        # Combine embedding and LLM scores
        final_recommendations = []
        for item in similar_works:
            work_id = item['work'].id
            embedding_score = item['similarity_score']
            llm_score = llm_scores.get(str(work_id), 0.5)  # Default to neutral if missing
            
            # Weighted combination (you can tune these weights)
            combined_score = (0.3 * embedding_score) + (0.7 * llm_score)
            
            final_recommendations.append({
                'work': item['work'],
                'confidence_score': combined_score,
                'embedding_score': embedding_score,
                'llm_score': llm_score
            })
        
        # Sort by combined score and return top recommendations
        final_recommendations.sort(key=lambda x: x['confidence_score'], reverse=True)
        return final_recommendations[:num_final_recommendations]
    
    def _llm_score_candidates(self, user, candidate_works):
        """Use LLM to score a smaller set of candidate works"""
        
        works_text = ""
        for i, work in enumerate(candidate_works):
            works_text += f"{i+1}. ID: {work.id} | {work.title} by {work.author} | {work.work_type}\n"
            if work.summary:
                works_text += f"   Summary: {work.summary[:200]}...\n"
            works_text += "\n"
        
        prompt = f"""
        Only respond with JSON. Do not add any extra text.
        You are an expert literary recommendation engine.

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
        
        try:
            response = self.client.models.generate_content(
                model=self.llm_model,
                contents=prompt
            )

            # Handle markdown-wrapped JSON responses
            response_text = response.text

            #print(response_text)

            # Extract JSON from markdown code block
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end > start:
                response_text = response_text[start:end]

            return json.loads(response_text)
        except Exception as e:
            print(f"LLM scoring error: {e}")
            # Fallback to neutral scores
            return {str(work.id): 0.5 for work in candidate_works}
    
    # STEP 5: Update work pool with embedding scores
    def populate_user_work_pool(self, user_id):
        """Populate UserWorkPool with embedding-based recommendation scores"""
        
        for work_type in ['poem', 'short_story', 'essay']:
            # recommendations = self.generate_embedding_recommendations(
            #     user_id, 
            #     work_type
            # )
            recommendations = self.generate_hybrid_recommendations(
                user_id, 
                work_type
            )
            
            for rec in recommendations:
                # Check if already in pool
                existing = UserWorkPool.query.filter_by(
                    user_id=user_id,
                    work_id=rec['work'].id
                ).first()
                
                if existing:
                    # Update existing confidence score
                    existing.confidence_score = rec['confidence_score']
                else:
                    # Create new pool entry
                    pool_entry = UserWorkPool(
                        user_id=user_id,
                        work_id=rec['work'].id,
                        work_type=work_type,
                        confidence_score=rec['confidence_score'],
                        status='available'
                    )
                    db.session.add(pool_entry)
        
        db.session.commit()
        print(f"Populated work pool for user {user_id}")

# Usage example
def setup_embedding_system():
    """Initialize the embedding system for your app"""
    engine = EmbeddingRecommendationEngine()
    
    # Step 1: Generate embeddings for all works (run once)
    engine.generate_work_embeddings()
    
    # Step 2: For each user, populate their work pool
    users = User.query.all()
    for user in users:
        if user.preference_summary:  # Only if they've completed onboarding
            engine.populate_user_work_pool(user.id)

# Database schema addition needed:
"""
ALTER TABLE works ADD COLUMN embedding_vector TEXT;
"""