"""
Run the full scraper with better error reporting.
"""

from scraper import BrownCourseScraper
from database import CourseDatabase
import traceback


def main():
    print("="*60)
    print("Brown Course Catalog - Full Scraper")
    print("="*60)
    print("\nThis will scrape ALL courses (~1645 courses)")
    print("Estimated time: 30-60 minutes")
    print("Progress updates every 10 courses\n")
    
    scraper = BrownCourseScraper(headless=False)
    
    try:
        scraper.setup_driver()
        print("[+] Driver setup complete")
        
        scraper.load_all_courses()
        print("[+] Course list loaded")
        
        scraper.scrape_course_list(max_courses=None)
        print("[+] Scraping complete")
        
    except Exception as e:
        print(f"\n[!] Error: {e}")
        traceback.print_exc()
    finally:
        scraper.cleanup()
        
        # Print summary
        print(f"\n{'='*60}")
        print("Final Summary")
        print('='*60)
        print(f"Courses scraped: {scraper.courses_scraped}")
        
        db = CourseDatabase()
        count = db.get_course_count()
        print(f"Courses in database: {count}")
        db.close()
        
        print('='*60)


if __name__ == "__main__":
    main()
