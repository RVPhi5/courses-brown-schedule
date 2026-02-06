"""
Dump HTML after clicking back to see what's left.
"""
from scraper import BrownCourseScraper
from selenium.webdriver.common.by import By
import time

def main():
    print("Dumping state...")
    scraper = BrownCourseScraper(headless=False)
    
    try:
        scraper.setup_driver()
        scraper.load_all_courses()
        
        # Click first course
        scraper.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")[0].click()
        time.sleep(2)
        
        # Click Back
        try:
            scraper.driver.find_element(By.CSS_SELECTOR, "a.panel__back").click()
            time.sleep(2)
            
            # Dump body HTML
            body = scraper.driver.find_element(By.TAG_NAME, "body").get_attribute("innerHTML")
            with open("post_back_state.html", "w", encoding="utf-8") as f:
                f.write(body)
            print("Dumped to post_back_state.html")
            
        except Exception as e:
            print(f"Error clicking back: {e}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()
