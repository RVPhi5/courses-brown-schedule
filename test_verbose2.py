"""
Verbose test to see what's happening with the scraper.
"""

from scraper import BrownCourseScraper
from database import CourseDatabase


def main():
    print("="*60)
    print("Verbose Test - First 10 Courses")
    print("="*60)
    
    scraper = BrownCourseScraper(headless=False)
    
    try:
        scraper.setup_driver()
        scraper.load_all_courses()
        
        from selenium.webdriver.common.by import By
        import time
        
        # Get first 10 courses
        course_elements = scraper.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")[:10]
        
        print(f"\nFound {len(course_elements)} courses\n")
        
        scraped_count = 0
        skipped_count = 0
        
        for i, element in enumerate(course_elements, 1):
            print(f"\n{'='*60}")
            print(f"Course {i}")
            print('='*60)
            
            # Extract list data
            course_data = scraper.extract_list_data(element)
            
            if not course_data:
                print("ERROR: Could not extract data")
                continue
            
            print(f"Code: {course_data.get('course_code')}")
            print(f"Name: {course_data.get('course_name')}")
            print(f"Section: {course_data.get('section')}")
            print(f"Times: '{course_data.get('course_times')}'")
            print(f"Instructor: '{course_data.get('instructor')}'")
            
            # Check if C-section
            if course_data.get('section', '').startswith('C'):
                print("→ SKIPPING (C-section)")
                skipped_count += 1
                continue
            
            print("→ SCRAPING...")
            
            try:
                # Click into course
                element.click()
                time.sleep(1.5)
                
                # Check if we need table extraction
                if not course_data.get('course_times') or not course_data.get('instructor'):
                    print("  → Extracting from All Sections table")
                    section_data = scraper.extract_section_from_table(course_data.get('course_code', ''))
                    print(f"     Times: {section_data.get('course_times')}")
                    print(f"     Instructor: {section_data.get('instructor')}")
                    print(f"     CRN: {section_data.get('crn')}")
                    course_data.update(section_data)
                else:
                    print("  → Extracting enrollment data")
                    enrollment_data = scraper.extract_enrollment_data()
                    print(f"     CRN: {enrollment_data.get('crn')}")
                    print(f"     Enrollment: {enrollment_data.get('max_enrollment')}/{enrollment_data.get('seats_available')}")
                    course_data.update(enrollment_data)
                
                # Go back
                scraper.driver.back()
                time.sleep(1)
                
                # Save
                scraper.db.insert_course(course_data)
                scraped_count += 1
                print("  ✓ Saved to database")
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                try:
                    scraper.driver.back()
                    time.sleep(1)
                except:
                    pass
        
        print(f"\n{'='*60}")
        print(f"Summary:")
        print(f"  Scraped: {scraped_count}")
        print(f"  Skipped (C-sections): {skipped_count}")
        print(f"{'='*60}")
        
        # Check database
        db = CourseDatabase()
        count = db.get_course_count()
        print(f"\nCourses in database: {count}")
        
        if count > 0:
            courses = db.get_all_courses()
            for course in courses:
                print(f"\n  {course['course_code']} {course['section']} - {course['course_name']}")
                print(f"    Times: {course['course_times']}")
                print(f"    Instructor: {course['instructor']}")
                print(f"    CRN: {course['crn']}")
        
        db.close()
        
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if scraper.driver:
            input("\nPress Enter to close...")
            scraper.cleanup()


if __name__ == "__main__":
    main()
