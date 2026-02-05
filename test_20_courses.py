"""
Test scraper with 20 courses to debug the stopping issue.
"""

from scraper import BrownCourseScraper
from database import CourseDatabase


def main():
    print("="*60)
    print("Testing Scraper - 20 Courses")
    print("="*60)
    print("\nThis will scrape 20 courses to test if the scraper works\n")
    
    scraper = BrownCourseScraper(headless=False)
    
    try:
        scraper.setup_driver()
        print("✓ Driver setup complete")
        
        scraper.load_all_courses()
        print("✓ Course list loaded")
        
        # Run with limit of 20
        scraper.scrape_course_list(max_courses=20)
        print("✓ Scraping complete")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.cleanup()
        
        # Print summary
        print(f"\n{'='*60}")
        print("Summary")
        print('='*60)
        print(f"Courses scraped: {scraper.courses_scraped}")
        
        db = CourseDatabase()
        count = db.get_course_count()
        print(f"Courses in database: {count}")
        
        if count > 0:
            print("\nSample courses:")
            courses = db.get_all_courses()
            for i, course in enumerate(courses[:5], 1):
                print(f"\n{i}. {course['course_code']} {course['section']} - {course['course_name']}")
                print(f"   Times: {course['course_times']}")
                print(f"   Instructor: {course['instructor']}")
                print(f"   CRN: {course['crn']}")
        
        db.close()
        print('='*60)


if __name__ == "__main__":
    main()
