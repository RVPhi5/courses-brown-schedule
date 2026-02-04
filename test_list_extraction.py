"""
Simple test to check if we can extract course list data without clicking into details.
"""

from scraper import BrownCourseScraper
from database import CourseDatabase


def main():
    print("Testing course list extraction only...")
    
    scraper = BrownCourseScraper(headless=False)
    
    try:
        scraper.setup_driver()
        scraper.load_all_courses()
        
        # Get first 3 course elements
        course_elements = scraper.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")[:3]
        
        print(f"\nFound {len(course_elements)} course elements\n")
        
        for i, element in enumerate(course_elements, 1):
            print(f"Course {i}:")
            data = scraper.extract_list_data(element)
            if data:
                for key, value in data.items():
                    print(f"  {key}: {value}")
            else:
                print("  ERROR: Could not extract data")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if scraper.driver:
            input("Press Enter to close browser...")
            scraper.driver.quit()


if __name__ == "__main__":
    from selenium.webdriver.common.by import By
    main()
