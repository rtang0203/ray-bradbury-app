"""
Content seeding script for Literary Recommendations App
Populates the Work table with curated poems, short stories, and essays
"""

from app import create_app, db
from app.models import Work
from datetime import datetime

app = create_app()

def seed_poems():
    """Seed curated poems"""
    poems = [
        {
            "title": "The Road Not Taken",
            "author": "Robert Frost",
            "work_type": "poem",
            "content_url": "https://www.poetryfoundation.org/poems/44272/the-road-not-taken",
            "summary": "A reflective poem about life choices and their consequences, told through the metaphor of choosing between two forest paths.",
            "estimated_reading_time": 3,
            "difficulty_level": "beginner",
            "genres": "nature poetry,philosophical",
            "themes": "choice,regret,life paths,nature",
            "publication_year": 1916,
            "public_domain": True,
            "word_count": 95
        },
        {
            "title": "Because I could not stop for Death",
            "author": "Emily Dickinson",
            "work_type": "poem", 
            "content_url": "https://www.poetryfoundation.org/poems/47652/because-i-could-not-stop-for-death-479",
            "summary": "Death is personified as a courteous carriage driver who takes the speaker on a journey through life and into eternity.",
            "estimated_reading_time": 4,
            "difficulty_level": "intermediate",
            "genres": "metaphysical poetry,death poetry",
            "themes": "death,eternity,time,personification",
            "publication_year": 1890,
            "public_domain": True,
            "word_count": 120
        },
        {
            "title": "Harlem",
            "author": "Langston Hughes",
            "work_type": "poem",
            "content_url": "https://www.poetryfoundation.org/poems/46548/harlem",
            "summary": "A powerful exploration of deferred dreams and their consequences, using vivid imagery to ask what happens to dreams that are postponed.",
            "estimated_reading_time": 2,
            "difficulty_level": "intermediate",
            "genres": "social poetry,Harlem Renaissance",
            "themes": "dreams,social justice,inequality,hope",
            "publication_year": 1951,
            "public_domain": False,  # Still under copyright
            "word_count": 55
        },
        {
            "title": "Ozymandias",
            "author": "Percy Bysshe Shelley",
            "work_type": "poem",
            "content_url": "https://www.poetryfoundation.org/poems/46565/ozymandias",
            "summary": "A sonnet about the ruins of a statue of an ancient king, exploring themes of power, pride, and the inevitable passage of time.",
            "estimated_reading_time": 3,
            "difficulty_level": "intermediate",
            "genres": "romantic poetry,sonnet",
            "themes": "power,pride,time,mortality,hubris",
            "publication_year": 1818,
            "public_domain": True,
            "word_count": 110
        },
        {
            "title": "The Love Song of J. Alfred Prufrock",
            "author": "T.S. Eliot",
            "work_type": "poem",
            "content_url": "https://www.poetryfoundation.org/poetrymagazine/poems/44212/the-love-song-of-j-alfred-prufrock",
            "summary": "A modernist masterpiece exploring social anxiety, aging, and missed opportunities through the internal monologue of a hesitant, self-conscious narrator.",
            "estimated_reading_time": 12,
            "difficulty_level": "advanced",
            "genres": "modernist poetry,dramatic monologue",
            "themes": "anxiety,aging,indecision,modern life,alienation",
            "publication_year": 1915,
            "public_domain": True,
            "word_count": 1300
        }
    ]
    
    for poem_data in poems:
        poem = Work(**poem_data)
        db.session.add(poem)
    
    print(f"Added {len(poems)} poems")

def seed_short_stories():
    """Seed curated short stories"""
    stories = [
        {
            "title": "The Gift of the Magi",
            "author": "O. Henry",
            "work_type": "short_story",
            "content_url": "https://www.gutenberg.org/files/7256/7256-h/7256-h.htm",
            "summary": "A young married couple each sacrifice their most treasured possession to buy a Christmas gift for the other, only to discover the ironic twist of their mutual sacrifice.",
            "estimated_reading_time": 15,
            "difficulty_level": "beginner",
            "genres": "Christmas story,irony,romance",
            "themes": "sacrifice,love,irony,Christmas,poverty",
            "publication_year": 1905,
            "public_domain": True,
            "word_count": 2000
        },
        {
            "title": "The Tell-Tale Heart",
            "author": "Edgar Allan Poe",
            "work_type": "short_story",
            "content_url": "https://www.gutenberg.org/files/2148/2148-h/2148-h.htm",
            "summary": "A psychological horror story told by an unreliable narrator who insists on his sanity after murdering an old man, driven by the victim's 'vulture eye.'",
            "estimated_reading_time": 12,
            "difficulty_level": "intermediate",
            "genres": "horror,psychological fiction,gothic",
            "themes": "guilt,madness,murder,paranoia,unreliable narrator",
            "publication_year": 1843,
            "public_domain": True,
            "word_count": 2000
        },
        {
            "title": "The Lady with the Dog",
            "author": "Anton Chekhov",
            "work_type": "short_story",
            "content_url": "https://www.gutenberg.org/files/13415/13415-h/13415-h.htm",
            "summary": "A married man's casual affair during a vacation unexpectedly develops into profound love, changing both participants' understanding of themselves and relationships.",
            "estimated_reading_time": 25,
            "difficulty_level": "advanced",
            "genres": "realism,romance,literary fiction",
            "themes": "love,adultery,transformation,middle age,Russian society",
            "publication_year": 1899,
            "public_domain": True,
            "word_count": 4500
        },
        {
            "title": "A Good Man Is Hard to Find",
            "author": "Flannery O'Connor",
            "work_type": "short_story",
            "content_url": "https://www.classicshorts.com/stories/goodman.html",
            "summary": "A family road trip takes a dark turn when they encounter an escaped convict called The Misfit, leading to a violent confrontation that explores themes of grace and redemption.",
            "estimated_reading_time": 30,
            "difficulty_level": "advanced",
            "genres": "Southern Gothic,religious fiction",
            "themes": "grace,violence,family,religion,moral complexity",
            "publication_year": 1953,
            "public_domain": False,
            "word_count": 6000
        },
        {
            "title": "The Necklace",
            "author": "Guy de Maupassant",
            "work_type": "short_story",
            "content_url": "https://www.gutenberg.org/files/3090/3090-h/3090-h.htm",
            "summary": "A woman borrows an expensive necklace for a party, loses it, and spends years in poverty paying for a replacement, only to discover a devastating truth.",
            "estimated_reading_time": 20,
            "difficulty_level": "intermediate",
            "genres": "irony,social realism",
            "themes": "vanity,social class,irony,sacrifice,deception",
            "publication_year": 1884,
            "public_domain": True,
            "word_count": 3500
        }
    ]
    
    for story_data in stories:
        story = Work(**story_data)
        db.session.add(story)
    
    print(f"Added {len(stories)} short stories")

def seed_essays():
    """Seed curated essays"""
    essays = [
        {
            "title": "Self-Reliance",
            "author": "Ralph Waldo Emerson",
            "work_type": "essay",
            "content_url": "https://www.gutenberg.org/files/16643/16643-h/16643-h.htm#SELF-RELIANCE",
            "summary": "A foundational transcendentalist essay advocating for individualism, nonconformity, and trusting one's own instincts over societal expectations.",
            "estimated_reading_time": 45,
            "difficulty_level": "advanced",
            "genres": "transcendentalism,philosophy,American literature",
            "themes": "individualism,nonconformity,self-trust,society,intuition",
            "publication_year": 1841,
            "public_domain": True,
            "word_count": 8000
        },
        {
            "title": "Civil Disobedience",
            "author": "Henry David Thoreau",
            "work_type": "essay",
            "content_url": "https://www.gutenberg.org/files/71/71-h/71-h.htm",
            "summary": "A influential essay arguing that individuals should not permit government to override their conscience, and that they have a duty to avoid enabling injustice through compliance.",
            "estimated_reading_time": 40,
            "difficulty_level": "advanced",
            "genres": "political philosophy,transcendentalism",
            "themes": "civil disobedience,government,conscience,justice,individual responsibility",
            "publication_year": 1849,
            "public_domain": True,
            "word_count": 7500
        },
        {
            "title": "A Room of One's Own (Chapter 1)",
            "author": "Virginia Woolf",
            "work_type": "essay",
            "content_url": "https://www.gutenberg.org/files/48545/48545-h/48545-h.htm",
            "summary": "The opening chapter of Woolf's famous feminist essay exploring the relationship between women and literature, introducing her thesis about women needing financial independence and space to write.",
            "estimated_reading_time": 35,
            "difficulty_level": "advanced",
            "genres": "feminist literature,literary criticism",
            "themes": "feminism,women writers,economic independence,literary tradition",
            "publication_year": 1929,
            "public_domain": True,
            "word_count": 6500
        },
        {
            "title": "The Death of the Moth",
            "author": "Virginia Woolf",
            "work_type": "essay",
            "content_url": "https://www.gutenberg.org/files/60996/60996-h/60996-h.htm",
            "summary": "A meditative essay observing a moth's struggle against death, using this simple scene to explore larger themes about life, death, and the human condition.",
            "estimated_reading_time": 8,
            "difficulty_level": "intermediate",
            "genres": "personal essay,nature writing",
            "themes": "death,life,nature,observation,mortality",
            "publication_year": 1942,
            "public_domain": True,
            "word_count": 1200
        },
        {
            "title": "Politics and the English Language",
            "author": "George Orwell",
            "work_type": "essay",
            "content_url": "https://www.gutenberg.org/files/66356/66356-h/66356-h.htm",
            "summary": "A critique of contemporary English prose and political language, arguing that unclear writing enables unclear thinking and political manipulation.",
            "estimated_reading_time": 25,
            "difficulty_level": "intermediate",
            "genres": "political essay,language criticism",
            "themes": "language,politics,clarity,propaganda,writing",
            "publication_year": 1946,
            "public_domain": True,
            "word_count": 4500
        }
    ]
    
    for essay_data in essays:
        essay = Work(**essay_data)
        db.session.add(essay)
    
    print(f"Added {len(essays)} essays")

def clear_existing_works():
    """Clear existing works (useful for development)"""
    Work.query.delete()
    db.session.commit()
    print("Cleared existing works")

def main():
    """Main seeding function"""
    with app.app_context():
        print("Starting content seeding...")
        
        # Uncomment next line if you want to clear existing data
        # clear_existing_works()
        
        # Create tables if they don't exist
        db.create_all()
        
        # Seed content
        seed_poems()
        seed_short_stories() 
        seed_essays()
        
        # Commit all changes
        db.session.commit()
        print("Content seeding completed successfully!")
        
        # Print summary
        total_works = Work.query.count()
        poems = Work.query.filter_by(work_type='poem').count()
        stories = Work.query.filter_by(work_type='short_story').count()
        essays = Work.query.filter_by(work_type='essay').count()
        
        print(f"\nDatabase now contains:")
        print(f"  Total works: {total_works}")
        print(f"  Poems: {poems}")
        print(f"  Short stories: {stories}")
        print(f"  Essays: {essays}")

if __name__ == "__main__":
    main()