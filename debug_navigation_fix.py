"""
Debug script to test the fix with heavy logging.
"""
from scraper import BrownCourseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def main():
    print("Testing navigation fix...")
    scraper = BrownCourseScraper(headless=False)
    
    try:
        scraper.setup_driver()
        scraper.load_all_courses()
        
        initial = scraper.get_course_count()
        print(f"Initial count: {initial}")
        
        # Click first course
        print("Clicking first course...")
        parts = scraper.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")
        parts[0].click()
        time.sleep(2)
        
        print(f"Current URL: {scraper.driver.current_url}")
        
        # Try to go back using the fix logic
        print("Attempting to go back...")
        try:
            back_button = WebDriverWait(scraper.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.panel__back"))
            )
            print(f"Found back button: {back_button.get_attribute('outerHTML')}")
            back_button.click()
            print("Clicked back button.")
            
            # Wait for list
            WebDriverWait(scraper.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".result.result--group-start"))
            )
            print("List element detected.")
            time.sleep(2)
            
            # Check count
            final_elements = scraper.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")
            print(f"Final count: {len(final_elements)}")
            
            if len(final_elements) > 1:
                print("SUCCESS: Count restored.")
            else:
                print("FAILURE: Count is low.")
                
                # Check what is visible
                visible = [e for e in final_elements if e.is_displayed()]
                print(f"Visible elements: {len(visible)}")
                
        except Exception as e:
            print(f"Error during back navigation: {e}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()
