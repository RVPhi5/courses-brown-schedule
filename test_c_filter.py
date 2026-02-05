"""
Test to verify C-sections are being skipped.
"""

from scraper import BrownCourseScraper
from selenium.webdriver.common.by import By
import time


def main():
    print("Testing C-section filtering...\n")
    
    scraper = BrownCourseScraper(headless=False)
    
    try:
        scraper.setup_driver()
        scraper.load_all_courses()
        
        # Get first 20 course elements to find some C sections
        course_elements = scraper.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")[:20]
        
        print(f"Checking first {len(course_elements)} courses...\n")
        
        s_sections = 0
        c_sections = 0
        
        for element in course_elements:
            data = scraper.extract_list_data(element)
            if data:
                section = data.get('section', '')
                course_code = data.get('course_code', '')
                
                if section.startswith('S'):
                    s_sections += 1
                    print(f"✓ KEEP: {course_code} {section}")
                elif section.startswith('C'):
                    c_sections += 1
                    print(f"✗ SKIP: {course_code} {section} (discussion/conference section)")
                else:
                    print(f"? OTHER: {course_code} {section}")
        
        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"  S-sections (will be scraped): {s_sections}")
        print(f"  C-sections (will be skipped): {c_sections}")
        print(f"{'='*60}")
        
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
