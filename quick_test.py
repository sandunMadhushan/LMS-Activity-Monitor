import traceback
from scraper import MoodleScraper

try:
    print("Creating scraper...")
    s = MoodleScraper(headless=True)
    
    print("Starting scrape...")
    r = s.scrape_ousl()
    
    print(f"Result: {r}")
    
    s.close_driver()
except Exception as e:
    print(f"\nError occurred: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
