"""
Run scraper with detailed logging to see what's happening.
"""

from scraper import BrownCourseScraper
from selenium.webdriver.common.by import By
import time


def main():
    print("Running scraper with detailed logging...\n")
    
    scraper = BrownCourseScraper(headless=False)
    
    try:
        scraper.setup_driver()
        scraper.load_all_courses()
        
        # Manually run the scraping loop with logging
        total_courses = scraper.get_course_count()
        print(f"Total courses found: {total_courses}\n")
        
        max_courses = 5  # Test with 5
        course_index = 0
        
        while course_index < max_courses:
            print(f"\n{'='*60}")
            print(f"Processing index {course_index}")
            print('='*60)
            
            try:
                # Get course elements
                course_elements = scraper.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")
                print(f"Found {len(course_elements)} course elements")
                
                if course_index >= len(course_elements):
                    print("Index out of range!")
                    break
                
                course_element = course_elements[course_index]
                
                # Extract data
                course_data = scraper.extract_list_data(course_element)
                print(f"Course: {course_data.get('course_code')} {course_data.get('section')}")
                
                # Check if C-section
                if course_data and course_data.get('section', '').startswith('C'):
                    print("→ Skipping C-section")
                    course_index += 1
                    continue
                
                if course_data:
                    print("→ Clicking into course...")
                    course_element.click()
                    time.sleep(1.5)
                    
                    # Extract enrollment
                    if not course_data.get('course_times') or not course_data.get('instructor'):
                        print("→ Extracting from table")
                        section_data = scraper.extract_section_from_table(course_data.get('course_code', ''))
                        course_data.update(section_data)
                    else:
                        print("→ Extracting enrollment")
                        enrollment_data = scraper.extract_enrollment_data()
                        course_data.update(enrollment_data)
                    
                    print("→ Going back...")
                    scraper.driver.back()
                    time.sleep(1.5)
                    
                    print("→ Saving to database...")
                    scraper.db.insert_course(course_data)
                    scraper.courses_scraped += 1
                    print(f"✓ Saved! Total scraped: {scraper.courses_scraped}")
                
                course_index += 1
                
            except Exception as e:
                print(f"✗ Error: {e}")
                import traceback
                traceback.print_exc()
                try:
                    scraper.driver.back()
                    time.sleep(1)
                except:
                    pass
                course_index += 1
        
        print(f"\n{'='*60}")
        print(f"Scraping complete! Scraped {scraper.courses_scraped} courses")
        print('='*60)
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nPress Enter to close...")
        scraper.cleanup()


if __name__ == "__main__":
    main()
