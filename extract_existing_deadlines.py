#!/usr/bin/env python3
"""
Extract deadlines from existing activities in the database.
This is a one-time script to process all existing activities.
"""

from database import Database
from scraper import MoodleScraper

def main():
    db = Database()
    scraper = MoodleScraper()
    conn = db.get_connection()
    
    # Get all activities
    activities = conn.execute('''
        SELECT a.activity_id, a.course_id, a.title, a.description, c.lms_name
        FROM activities a
        JOIN courses c ON a.course_id = c.course_id
        WHERE a.description IS NOT NULL AND a.description != ""
    ''').fetchall()
    
    print(f"Processing {len(activities)} activities with descriptions...")
    print("=" * 60)
    
    extracted_count = 0
    
    for activity_id, course_id, title, description, lms_name in activities:
        try:
            # Extract and store deadline
            result = scraper._extract_and_store_deadline(
                activity_id=activity_id,
                course_id=course_id,
                title=title,
                description=description,
                lms_name=lms_name
            )
            
            if result:  # If a deadline was extracted
                extracted_count += 1
                
        except Exception as e:
            print(f"Error processing {activity_id}: {e}")
    
    print("=" * 60)
    print(f"\n✅ Processing complete!")
    print(f"   Total activities processed: {len(activities)}")
    print(f"   Deadlines extracted: {extracted_count}")
    
    # Show some examples
    print("\n📅 Sample extracted deadlines:")
    deadlines = conn.execute('''
        SELECT title, deadline_date, lms_name
        FROM deadlines
        WHERE source = 'scraped'
        ORDER BY deadline_date
        LIMIT 10
    ''').fetchall()
    
    for title, date, lms in deadlines:
        print(f"   - {title[:50]:50s} | {date[:10]} | {lms}")

if __name__ == "__main__":
    main()
