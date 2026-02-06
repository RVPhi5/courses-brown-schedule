"""
Debug clicking the next course without going back.
"""
from scraper import BrownCourseScraper
from selenium.webdriver.common.by import By
import time

def main():
    print("Testing next click...")
    scraper = BrownCourseScraper(headless=False)
    
    try:
        scraper.setup_driver()
        scraper.load_all_courses()
        
        # Click 1st course
        print("Clicking 1st course...")
        courses = scraper.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")
        courses[0].click()
        time.sleep(2)
        
        # Click 2nd course
        print("Clicking 2nd course...")
        # Re-find elements
        courses = scraper.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")
        if len(courses) > 1:
            try:
                # Scroll into view
                scraper.driver.execute_script("arguments[0].scrollIntoView(true);", courses[1])
                time.sleep(1)
                
                courses[1].click()
                print("Clicked 2nd course!")
                time.sleep(2)
                
                # Verify we are on 2nd course
                # Check if detail  updated
                body_text = scraper.driver.find_element(By.TAG_NAME, "body").text
                # Get 2nd course code
                code = courses[1].find_element(By.CSS_SELECTOR, ".result__code").text
                print(f"Expected code: {code}")
                
                if code in body_text:
                     print("SUCCESS: 2nd course details loaded.")
                else:
                     print("FAILURE: 2nd course details NOT loaded.")
                     
            except Exception as e:
                print(f"Error clicking 2nd course: {e}")
                scraper.driver.save_screenshot("debug_click_fail.png")
                print("Saved debug_click_fail.png")
        else:
             print("Less than 2 courses found!")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()
