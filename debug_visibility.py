"""
Debug visibility of panels and results.
"""
from scraper import BrownCourseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def main():
    print("Testing visibility...")
    scraper = BrownCourseScraper(headless=False)
    
    try:
        scraper.setup_driver()
        scraper.load_all_courses()
        
        print("\n--- Initial State ---")
        results_panel = scraper.driver.find_elements(By.CSS_SELECTOR, ".panel--kind-results")
        if results_panel:
            print(f"Results Panel: {results_panel[0].get_attribute('class')} Visible={results_panel[0].is_displayed()}")
        
        # Click first course
        print("\nClicking first course...")
        parts = scraper.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")
        if parts:
            parts[0].click()
        else:
            print("No courses found!")
            return
            
        time.sleep(2)
        
        print("\n--- Detail State ---")
        results_panel = scraper.driver.find_elements(By.CSS_SELECTOR, ".panel--kind-results")
        if results_panel:
            print(f"Results Panel: {results_panel[0].get_attribute('class')} Visible={results_panel[0].is_displayed()}")
            
        # Click Back
        print("\nClicking Back...")
        back_button = scraper.driver.find_element(By.CSS_SELECTOR, "a.panel__back")
        back_button.click()
        time.sleep(2)
        
        print("\n--- After Back State ---")
        results_panel = scraper.driver.find_elements(By.CSS_SELECTOR, ".panel--kind-results")
        if results_panel:
            print(f"Results Panel: {results_panel[0].get_attribute('class')} Visible={results_panel[0].is_displayed()}")
            
        # Check what element triggered presence
        print("\nChecking presence of .result...")
        try:
            el = WebDriverWait(scraper.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".result.result--group-start"))
            )
            print(f"Element found via Wait: {el.tag_name} class='{el.get_attribute('class')}'")
            print(f"Is Displayed: {el.is_displayed()}")
            print(f"Size: {el.size}")
            print(f"Location: {el.location}")
            
            # Find all again
            all_res = scraper.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")
            print(f"Find Elements count: {len(all_res)}")
            
        except Exception as e:
            print(f"Wait failed: {e}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()
