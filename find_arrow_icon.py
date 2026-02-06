"""
Targeted script to find back/arrow icons.
"""
from scraper import BrownCourseScraper
from selenium.webdriver.common.by import By
import time

def main():
    print("Finding arrow icons...")
    scraper = BrownCourseScraper(headless=False)
    
    try:
        scraper.setup_driver()
        scraper.load_all_courses()
        
        # Click first course
        print("Clicking first course...")
        course_elements = scraper.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")
        if course_elements:
            course_elements[0].click()
            time.sleep(2)
            
            print("\n--- Searching for Arrow/Back Icons ---")
            # Look for specific keywords in class names
            xpath = "//*[contains(@class, 'arrow') or contains(@class, 'chevron') or contains(@class, 'back') or contains(@class, 'left')]"
            elements = scraper.driver.find_elements(By.XPATH, xpath)
            
            seen_classes = set()
            for el in elements:
                # Only check visible elements
                if el.is_displayed():
                    cls = el.get_attribute("class")
                    tag = el.tag_name
                    if cls not in seen_classes:
                        print(f"Match: <{tag} class='{cls}'>")
                        parent = el.find_element(By.XPATH, "..")
                        print(f"  Parent: <{parent.tag_name} class='{parent.get_attribute('class')}'>")
                        seen_classes.add(cls)
                        
            print("\n--- Searching for 'Back' text ---")
            xpath_text = "//*[contains(text(), 'Back') or contains(text(), 'Results')]"
            text_elements = scraper.driver.find_elements(By.XPATH, xpath_text)
            for el in text_elements:
                if el.is_displayed():
                    print(f"Text Match: <{el.tag_name}> '{el.text}'")

        else:
            print("No courses found to click.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()
