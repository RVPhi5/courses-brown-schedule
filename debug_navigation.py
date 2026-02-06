"""
Debug script to check why scraper stops after one course.
Verifies element count after navigation.
"""
from scraper import BrownCourseScraper
from selenium.webdriver.common.by import By
import time

def main():
    print("Starting navigation debug script...")
    scraper = BrownCourseScraper(headless=False)
    
    try:
        scraper.setup_driver()
        scraper.load_all_courses()
        
        # Initial count
        initial_courses = scraper.get_course_count()
        print(f"\nInitial course count: {initial_courses}")
        print(f"Initial URL: {scraper.driver.current_url}")
        
        if initial_courses == 0:
            print("No courses found initially!")
            return
            
        # Try to click first course and go back
        print("\nClicking first course...")
        course_elements = scraper.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")
        course_elements[0].click()
        
        time.sleep(2)
        print(f"In detail page. URL: {scraper.driver.current_url}")
        print("Going back...")
        
        scraper.driver.back()
        time.sleep(2)  # Wait for page to restore
        print(f"Back in list view. URL: {scraper.driver.current_url}")
        
        # Check if we need to re-wait for elements
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        try:
           WebDriverWait(scraper.driver, 5).until(
               EC.presence_of_element_located((By.CSS_SELECTOR, ".result.result--group-start"))
           )
           print("Found course elements again.")
        except:
           print("Timed out waiting for course elements to reappear.")
        
        # Count again
        final_course_elements = scraper.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")
        print(f"Final course count: {len(final_course_elements)}")
        
        if len(final_course_elements) < initial_courses:
            print("\nISSUE REPRODUCED: specific count dropped!")
            # Check if search term is still there
            try:
                search_box = scraper.driver.find_element(By.CSS_SELECTOR, "input[placeholder*='title, tag, subject, CRN or keyword']")
                print(f"Search box value: '{search_box.get_attribute('value')}'")
            except:
                print("Could not find search box")
        else:
            print("\nIssue NOT reproduced with simple back navigation.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()
