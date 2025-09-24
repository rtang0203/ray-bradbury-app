#!/usr/bin/env python3
"""
Script to find and update Project Gutenberg URLs for works missing content_url.

This script searches Project Gutenberg for works that don't have content URLs
and updates the database with the found URLs.
"""

import sys
import os
import requests
import time
from urllib.parse import quote_plus

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.models import Work
from app import db


def search_gutenberg(title, author):
    """
    Search Project Gutenberg for a work by title and author.
    Returns the URL if found, None otherwise.
    """
    # Project Gutenberg search URL
    base_url = "https://www.gutenberg.org/ebooks/search/"
    
    # Try different search combinations
    search_queries = [
        f"{title} {author}",
        title,
        f'"{title}" {author}',
        f"{author} {title}"
    ]
    
    for query in search_queries:
        try:
            params = {
                'query': query,
                'submit_search': 'Go!'
            }
            
            print(f"  Searching for: {query}")
            response = requests.get(base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                # Look for book links in the response
                text = response.text.lower()
                
                # Find ebook numbers in the HTML
                import re
                ebook_pattern = r'/ebooks/(\d+)'
                matches = re.findall(ebook_pattern, response.text)
                
                if matches:
                    # Use the first match and try HTML format first (more readable)
                    ebook_id = matches[0]
                    
                    # Try HTML format first, then fallback to plain text
                    url_formats = [
                        f"https://www.gutenberg.org/files/{ebook_id}/{ebook_id}-h/{ebook_id}-h.htm",
                        f"https://www.gutenberg.org/files/{ebook_id}/{ebook_id}-0.txt"
                    ]
                    
                    for gutenberg_url in url_formats:
                        try:
                            test_response = requests.head(gutenberg_url, timeout=5)
                            if test_response.status_code == 200:
                                return gutenberg_url
                        except:
                            continue
            
            # Be respectful to the server
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  Error searching for '{query}': {e}")
            continue
    
    return None


def update_work_urls(dry_run=True, limit=None):
    """
    Find and update Project Gutenberg URLs for works missing content_url.
    
    Args:
        dry_run (bool): If True, only print what would be updated without making changes
        limit (int): Limit number of works to process
    """
    app = create_app()
    
    with app.app_context():
        # Get all works without content URLs
        query = Work.query.filter(Work.content_url.is_(None))
        if limit:
            query = query.limit(limit)
        works_without_url = query.all()
        
        print(f"Found {len(works_without_url)} works without content URLs")
        
        if dry_run:
            print("DRY RUN MODE - No changes will be made to the database")
        
        updated_count = 0
        
        for i, work in enumerate(works_without_url):
            print(f"\n[{i+1}/{len(works_without_url)}] Processing: {work.title} by {work.author}")
            
            # Search for the work on Project Gutenberg
            url = search_gutenberg(work.title, work.author)
            
            if url:
                print(f"  ✓ Found URL: {url}")
                
                if not dry_run:
                    work.content_url = url
                    db.session.commit()
                    print(f"  ✓ Updated database")
                
                updated_count += 1
            else:
                print(f"  ✗ No URL found")
            
            # Be respectful to the server
            time.sleep(1)
        
        print(f"\n{'Would update' if dry_run else 'Updated'} {updated_count} works with URLs")
        
        if dry_run:
            print("\nTo actually update the database, run: python scripts/find_gutenberg_urls.py --update")


def main():
    """Main function to run the script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Find Project Gutenberg URLs for works')
    parser.add_argument('--update', action='store_true', 
                       help='Actually update the database (default is dry run)')
    parser.add_argument('--limit', type=int, 
                       help='Limit number of works to process (for testing)')
    
    args = parser.parse_args()
    
    # Run the update
    update_work_urls(dry_run=not args.update, limit=args.limit)


if __name__ == '__main__':
    main()