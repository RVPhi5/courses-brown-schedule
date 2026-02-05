"""
Debug script to check what's happening with course count.
"""

from scraper import BrownCourseScraper
from selenium.webdriver.common.by import By
import time


def main():
    scraper = BrownCourseScraper(headless=False)
    
    try:
        scraper.setup_driver()
        scraper.load_all_courses()
        
        print("\nChecking for course count element...")
        
        # Try to find the count element
        try:
            count_elem = scraper.driver.find_element(By.CSS_SELECTOR, ".result-count")
            print(f"✓ Found .result-count: {count_elem.text}")
        except:
            print("✗ Could not find .result-count")
        
        # Try alternative selectors
        page_text = scraper.driver.find_element(By.TAG_NAME, "body").text
        print(f"\nSearching page text for 'Found' or 'courses'...")
        
        import re
        matches = re.findall(r'Found \d+ courses?', page_text, re.IGNORECASE)
        if matches:
            print(f"✓ Found in page text: {matches}")
        else:
            print("✗ Pattern not found")
        
        # Count course elements directly
        course_elements = scraper.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")
        print(f"\n✓ Direct count of .result.result--group-start: {len(course_elements)}")
        
        # Try get_course_count method
        count = scraper.get_course_count()
        print(f"\nget_course_count() returned: {count}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nPress Enter to close...")
        scraper.cleanup()


if __name__ == "__main__":
    main()
