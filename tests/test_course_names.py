"""
Test script to verify course name extraction
"""
import os
import sys
from dotenv import load_dotenv
from scraper import MoodleScraper

load_dotenv()

def test_course_names():
    print("🔍 Testing Course Name Extraction\n")
    print("=" * 60)
    
    try:
        # Initialize scraper (headless mode for faster testing)
        scraper = MoodleScraper(headless=True)
        
        print("\n📚 Testing OUSL Course Scraping...")
        print("-" * 60)
        ousl_result = scraper.scrape_ousl()
        
        if ousl_result.get('success'):
            print(f"\n✅ Successfully scraped OUSL")
            print(f"Found {ousl_result.get('courses_found', 0)} courses\n")
            
            # Show first few courses
            courses = ousl_result.get('courses', [])[:5]
            for i, course in enumerate(courses, 1):
                print(f"{i}. {course.get('name', 'Unknown')}")
                print(f"   ID: {course.get('course_id')}")
                print(f"   Activities: {len(course.get('activities', []))}\n")
        else:
            print(f"❌ OUSL scraping failed: {ousl_result.get('error')}")
        
        print("\n📚 Testing RUSL Course Scraping...")
        print("-" * 60)
        rusl_result = scraper.scrape_rusl()
        
        if rusl_result.get('success'):
            print(f"\n✅ Successfully scraped RUSL")
            print(f"Found {rusl_result.get('courses_found', 0)} courses\n")
            
            # Show first few courses
            courses = rusl_result.get('courses', [])[:5]
            for i, course in enumerate(courses, 1):
                print(f"{i}. {course.get('name', 'Unknown')}")
                print(f"   ID: {course.get('course_id')}")
                print(f"   Activities: {len(course.get('activities', []))}\n")
        else:
            print(f"❌ RUSL scraping failed: {rusl_result.get('error')}")
        
        scraper.close_driver()
        
        print("\n" + "=" * 60)
        print("✅ Test completed!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_course_names()
