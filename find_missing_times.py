"""
Find courses that don't have times in the list view.
"""

from scraper import BrownCourseScraper
from selenium.webdriver.common.by import By
import time


def main():
    print("Searching for courses without times in list view...\n")
    
    scraper = BrownCourseScraper(headless=False)
    
    try:
        scraper.setup_driver()
        scraper.load_all_courses()
        
        # Get first 50 courses
        course_elements = scraper.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")[:50]
        
        print(f"Checking {len(course_elements)} courses...\n")
        
        courses_without_times = []
        
        for i, element in enumerate(course_elements, 1):
            data = scraper.extract_list_data(element)
            if data:
                course_code = data.get('course_code', '')
                times = data.get('course_times', '')
                instructor = data.get('instructor', '')
                section = data.get('section', '')
                
                if not times or not instructor:
                    print(f"✗ {course_code} {section}: times='{times}', instructor='{instructor}'")
                    courses_without_times.append(data)
                elif i <= 10:  # Show first 10 for reference
                    print(f"✓ {course_code} {section}: {times}, {instructor}")
        
        print(f"\n{'='*60}")
        print(f"Found {len(courses_without_times)} courses without times/instructor")
        print(f"{'='*60}")
        
        if courses_without_times:
            print("\nCourses to test with:")
            for course in courses_without_times[:5]:
                print(f"  - {course.get('course_code')} {course.get('section')}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if scraper.driver:
            input("\nPress Enter to close...")
            scraper.driver.quit()


if __name__ == "__main__":
    main()
