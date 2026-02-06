"""
Debug script to only print the header HTML of the detail page.
"""
from scraper import BrownCourseScraper
from selenium.webdriver.common.by import By
import time

def main():
    scraper = BrownCourseScraper(headless=False)
    try:
        scraper.setup_driver()
        scraper.load_all_courses()
        
        # Click first course
        print("Clicking course...")
        scraper.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")[0].click()
        time.sleep(3)
        
        print("\n--- Header Analysis ---")
        # Find anything that looks like a header
        headers = scraper.driver.find_elements(By.CSS_SELECTOR, "header, .header, #header, [class*='head']")
        for h in headers:
            print(f"Header tag: {h.tag_name}, class: {h.get_attribute('class')}")
            print(f"Inner HTML: {h.get_attribute('innerHTML')[:300]}")
            
        print("\n--- Icon Analysis ---")
        # Find all icons
        icons = scraper.driver.find_elements(By.CSS_SELECTOR, "i, span[class*='icon'], svg")
        for icon in icons:
            if icon.is_displayed():
                cls = icon.get_attribute('class')
                print(f"Visible Icon: tag={icon.tag_name} class='{cls}'")
                # print parent
                parent = icon.find_element(By.XPATH, "..")
                print(f"   Parent: tag={parent.tag_name} class='{parent.get_attribute('class')}'")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()
