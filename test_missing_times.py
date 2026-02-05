"""
Test scraping a course that doesn't have times in the list view (like APMA 0355).
"""

from scraper import BrownCourseScraper
from database import CourseDatabase
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


def main():
    print("Testing course with missing times in list view...\n")
    
    scraper = BrownCourseScraper(headless=False)
    db = CourseDatabase()
    
    try:
        scraper.setup_driver()
        
        # Navigate and search for APMA 0355 specifically
        print("Loading Brown course catalog...")
        scraper.driver.get("https://cab.brown.edu/")
        
        search_box = scraper.driver.find_element(By.CSS_SELECTOR, "input[placeholder*='title, tag, subject, CRN or keyword']")
        search_box.click()
        time.sleep(0.5)
        
        # Search for APMA 0355
        search_box.send_keys("APMA 0355")
        search_box.send_keys(Keys.RETURN)
        
        print("Waiting for search results...")
        time.sleep(3)
        
        # Find the course
        course_elements = scraper.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")
        
        if not course_elements:
            print("No courses found!")
            return
        
        print(f"Found {len(course_elements)} course(s)\n")
        
        # Process first course
        course_element = course_elements[0]
        
        print("Extracting list data...")
        course_data = scraper.extract_list_data(course_element)
        
        if course_data:
            print("List view data:")
            for key, value in course_data.items():
                print(f"  {key}: {value if value else '(empty)'}")
            
            # Check if times/instructor are missing
            if not course_data.get('course_times') or not course_data.get('instructor'):
                print("\n⚠️  Times/Instructor missing from list view")
                print("Clicking into course to extract from All Sections table...\n")
                
                course_element.click()
                time.sleep(2)
                
                # Extract from table
                section_data = scraper.extract_section_from_table(course_data.get('course_code', ''))
                
                print("All Sections table data:")
                for key, value in section_data.items():
                    if value:
                        print(f"  {key}: {value}")
                
                # Update course_data
                course_data.update(section_data)
                
                print("\n✓ Combined data:")
                print(f"  Course: {course_data.get('course_code')} - {course_data.get('course_name')}")
                print(f"  Section: {course_data.get('section')}")
                print(f"  Times: {course_data.get('course_times')}")
                print(f"  Instructor: {course_data.get('instructor')}")
                print(f"  CRN: {course_data.get('crn')}")
                print(f"  Enrollment: {course_data.get('max_enrollment')} max, {course_data.get('seats_available')} available")
                
                # Save to database
                scraper.db.insert_course(course_data)
                print("\n✓ Saved to database")
                
                # Verify in database
                saved_course = db.get_course_by_crn(course_data.get('crn'))
                if saved_course:
                    print("\n✓ Verified in database:")
                    print(f"  {saved_course['course_code']} - {saved_course['course_name']}")
                    print(f"  Times: {saved_course['course_times']}")
                    print(f"  Instructor: {saved_course['instructor']}")
                else:
                    print("\n✗ Not found in database")
            else:
                print("\n✓ Times/Instructor present in list view")
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if scraper.driver:
            input("\nPress Enter to close...")
            scraper.cleanup()
        db.close()


if __name__ == "__main__":
    main()
