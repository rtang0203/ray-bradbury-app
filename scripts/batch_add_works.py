#!/usr/bin/env python3
"""
Batch Add Works Script

This script reads works from a JSON file and adds them to the database.
Generates embeddings for each work using the Google Gemini API.

Usage:
    python scripts/batch_add_works.py <json_file_path> [--dry-run]

Example:
    python scripts/batch_add_works.py content/content_to_add.json
    python scripts/batch_add_works.py content/content_to_add.json --dry-run
"""

import sys
import json
import argparse
from datetime import datetime, timezone

# Add the parent directory to sys.path to import from app
sys.path.insert(0, '.')

from app import create_app, db
from app.models import Work
from app.embeddings_engine import EmbeddingRecommendationEngine

def load_works_from_json(file_path):
    """Load works from JSON file and validate structure."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if 'works' not in data:
            raise ValueError("JSON file must contain a 'works' array")
        
        works = data['works']
        batch_name = data.get('batch_name', 'Unknown Batch')
        
        print(f"Loaded {len(works)} works from batch: {batch_name}")
        return works, batch_name
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file '{file_path}': {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

def validate_work(work_data, index):
    """Validate that a work has all required fields."""
    required_fields = [
        'title', 'author', 'work_type', 'publication_year', 
        'themes', 'difficulty_level', 'estimated_reading_time', 
        'genres', 'summary'
    ]
    
    errors = []
    
    for field in required_fields:
        if field not in work_data or work_data[field] is None:
            errors.append(f"Missing required field: {field}")
        elif field == 'themes' and not isinstance(work_data[field], list):
            errors.append(f"Field 'themes' must be a list")
        elif field == 'genres' and not isinstance(work_data[field], list):
            errors.append(f"Field 'genres' must be a list")
    
    # Validate work_type
    valid_work_types = ['poem', 'short_story', 'essay']
    if work_data.get('work_type') not in valid_work_types:
        errors.append(f"work_type must be one of: {valid_work_types}")
    
    # Validate difficulty_level
    valid_difficulties = ['beginner', 'intermediate', 'advanced']
    if work_data.get('difficulty_level') not in valid_difficulties:
        errors.append(f"difficulty_level must be one of: {valid_difficulties}")
    
    if errors:
        print(f"Validation errors for work {index + 1} ('{work_data.get('title', 'Unknown')}'): {', '.join(errors)}")
        return False
    
    return True

def work_exists(title, author):
    """Check if a work with the same title and author already exists."""
    return Work.query.filter_by(title=title, author=author).first() is not None

def create_work_from_data(work_data):
    """Create a Work object from JSON data."""
    work = Work(
        title=work_data['title'],
        author=work_data['author'],
        work_type=work_data['work_type'],
        content_url=work_data.get('content_url'),
        summary=work_data['summary'],
        estimated_reading_time=work_data['estimated_reading_time'],
        difficulty_level=work_data['difficulty_level'],
        genres=','.join(work_data['genres']) if isinstance(work_data['genres'], list) else work_data['genres'],
        themes=','.join(work_data['themes']) if isinstance(work_data['themes'], list) else work_data['themes'],
        publication_year=work_data['publication_year'],
        public_domain=work_data.get('public_domain', True),
        word_count=work_data.get('word_count'),
        created_at=datetime.now(timezone.utc),
        active=True
    )
    
    return work

def generate_work_embedding(work, embedding_engine):
    """Generate and set embedding for a work using the embedding engine."""
    try:
        print(f"  Generating embedding for '{work.title}'...")
        
        # Use the existing _create_work_description method
        work_text = embedding_engine._create_work_description(work)
        
        # Get embedding using the engine's method
        embedding = embedding_engine._get_embedding(work_text)
        work.embedding_vector = json.dumps(embedding)
        
        print(f"  ✓ Generated {len(embedding)}-dimensional embedding")
        return True
        
    except Exception as e:
        print(f"  ✗ Failed to generate embedding for '{work.title}': {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Batch add works from JSON file to database')
    parser.add_argument('json_file', help='Path to JSON file containing works')
    parser.add_argument('--dry-run', action='store_true', help='Validate and preview without adding to database')
    args = parser.parse_args()
    
    # Load and validate works
    works_data, batch_name = load_works_from_json(args.json_file)
    
    # Validate all works first
    print(f"\nValidating {len(works_data)} works...")
    valid_works = []
    for i, work_data in enumerate(works_data):
        if validate_work(work_data, i):
            valid_works.append(work_data)
        else:
            print(f"Skipping invalid work {i + 1}")
    
    if not valid_works:
        print("No valid works found. Exiting.")
        sys.exit(1)
    
    print(f"✓ {len(valid_works)} works passed validation")
    
    # Create Flask app context
    app = create_app()
    with app.app_context():
        # Check for duplicates
        print(f"\nChecking for existing works...")
        new_works = []
        duplicate_count = 0
        
        for work_data in valid_works:
            if work_exists(work_data['title'], work_data['author']):
                print(f"  Duplicate: '{work_data['title']}' by {work_data['author']} already exists")
                duplicate_count += 1
            else:
                new_works.append(work_data)
        
        if duplicate_count > 0:
            print(f"Found {duplicate_count} duplicate works that will be skipped")
        
        if not new_works:
            print("No new works to add. All works already exist in database.")
            return
        
        print(f"✓ {len(new_works)} new works ready to add")
        
        if args.dry_run:
            print(f"\n--- DRY RUN SUMMARY ---")
            print(f"Batch: {batch_name}")
            print(f"Total works in file: {len(works_data)}")
            print(f"Valid works: {len(valid_works)}")
            print(f"Duplicate works (skipped): {duplicate_count}")
            print(f"New works to add: {len(new_works)}")
            print(f"\nNew works preview:")
            for work_data in new_works[:5]:  # Show first 5
                print(f"  - {work_data['title']} by {work_data['author']} ({work_data['work_type']})")
            if len(new_works) > 5:
                print(f"  ... and {len(new_works) - 5} more")
            print(f"\nRun without --dry-run to add these works to the database.")
            return
        
        # Initialize embedding engine
        print(f"\nInitializing embedding engine...")
        embedding_engine = EmbeddingRecommendationEngine()
        
        # Add works to database
        print(f"Adding {len(new_works)} works to database...")
        added_count = 0
        failed_count = 0
        
        for i, work_data in enumerate(new_works, 1):
            print(f"\n[{i}/{len(new_works)}] Processing '{work_data['title']}' by {work_data['author']}")
            
            try:
                # Create work object
                work = create_work_from_data(work_data)
                
                # Generate embedding
                if not generate_work_embedding(work, embedding_engine):
                    print(f"  ✗ Failed to generate embedding, skipping work")
                    failed_count += 1
                    continue
                
                # Add to database
                db.session.add(work)
                db.session.commit()
                
                print(f"  ✓ Successfully added to database (ID: {work.id})")
                added_count += 1
                
            except Exception as e:
                print(f"  ✗ Error adding work: {e}")
                db.session.rollback()
                failed_count += 1
        
        # Final summary
        print(f"\n--- BATCH ADD COMPLETE ---")
        print(f"Batch: {batch_name}")
        print(f"Successfully added: {added_count} works")
        print(f"Failed: {failed_count} works")
        print(f"Duplicates skipped: {duplicate_count} works")
        print(f"Total processed: {len(works_data)} works")
        
        if added_count > 0:
            print(f"\n✓ Database now contains {Work.query.count()} total works")

if __name__ == '__main__':
    main()