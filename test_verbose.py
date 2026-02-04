"""
Test with verbose logging to see what's happening.
"""

from scraper import BrownCourseScraper
from database import CourseDatabase


def main():
    print("Testing with 2 courses and verbose logging...\n")
    
    scraper = BrownCourseScraper(headless=False)
    
    try:
        scraper.setup_driver()
        scraper.load_all_courses()
        
        # Manually process 2 courses with logging
        from selenium.webdriver.common.by import By
        import time
        
        course_elements = scraper.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")[:2]
        
        for i, element in enumerate(course_elements, 1):
            print(f"\n{'='*60}")
            print(f"Processing Course {i}")
            print('='*60)
            
            # Extract list data
            print("Extracting list data...")
            course_data = scraper.extract_list_data(element)
            if course_data:
                print("List data extracted:")
                for key, value in course_data.items():
                    print(f"  {key}: {value}")
            else:
                print("ERROR: Could not extract list data")
                continue
            
            # Click into course
            print("\nClicking into course...")
            try:
                element.click()
                time.sleep(2)
                print("Clicked successfully, waiting for detail page...")
                
                # Extract enrollment data
                print("Extracting enrollment data...")
                enrollment_data = scraper.extract_enrollment_data()
                print("Enrollment data extracted:")
                for key, value in enrollment_data.items():
                    print(f"  {key}: {value}")
                
                course_data.update(enrollment_data)
                
                # Go back
                print("\nGoing back to list...")
                scraper.driver.back()
                time.sleep(2)
                print("Back to list")
                
                # Save to database
                print("\nSaving to database...")
                success = scraper.db.insert_course(course_data)
                if success:
                    print("✓ Saved successfully!")
                else:
                    print("✗ Failed to save")
                    
            except Exception as e:
                print(f"ERROR during detail extraction: {e}")
                import traceback
                traceback.print_exc()
                try:
                    scraper.driver.back()
                    time.sleep(1)
                except:
                    pass
        
        print(f"\n{'='*60}")
        print("Test complete!")
        print('='*60)
        
        # Check database
        db = CourseDatabase()
        count = db.get_course_count()
        print(f"\nCourses in database: {count}")
        
        if count > 0:
            courses = db.get_all_courses()
            for course in courses:
                print(f"\n{course['course_code']} - {course['course_name']}")
                print(f"  CRN: {course['crn']}")
                print(f"  Enrollment: {course['max_enrollment']}/{course['seats_available']}")
        
        db.close()
        
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if scraper.driver:
            input("\nPress Enter to close browser...")
            scraper.cleanup()


if __name__ == "__main__":
    main()
