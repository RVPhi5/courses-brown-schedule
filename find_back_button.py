"""
Find the back button selector.
"""
from scraper import BrownCourseScraper
from selenium.webdriver.common.by import By
import time

def main():
    print("Finding back button...")
    scraper = BrownCourseScraper(headless=False)
    
    try:
        scraper.setup_driver()
        scraper.load_all_courses()
        
        print("\nClicking first course...")
        course_elements = scraper.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")
        course_elements[0].click()
        time.sleep(2)
        
        # Look for elements with "back" or arrow classes
        print("\nSearching for potential back buttons...")
        
        # Strategy 1: Look for common icon classes
        potential_icons = scraper.driver.find_elements(By.CSS_SELECTOR, "i, span[class*='icon']")
        for icon in potential_icons:
            cls = icon.get_attribute("class")
            parent = icon.find_element(By.XPATH, "..")
            parent_cls = parent.get_attribute("class")
            
            # Filter for likely candidates
            if "left" in cls or "back" in cls or "arrow" in cls or "chevron" in cls:
                print(f"Candidate Icon: Class='{cls}' | Parent Tag='{parent.tag_name}' Class='{parent_cls}'")
                
        # Strategy 2: Look for the specific structure user described
        # Header with left arrow
        headers = scraper.driver.find_elements(By.CSS_SELECTOR, "header, .header, .title-bar, div[class*='head']")
        print(f"\nChecking {len(headers)} potential headers:")
        for header in headers:
            print(f"Header: {header.get_attribute('class')} Text: '{header.text[:20]}'")
            # Check for button inside
            btns = header.find_elements(By.CSS_SELECTOR, "button, a, div[role='button']")
            for btn in btns:
                print(f"  -> Inner element: {btn.tag_name}.{btn.get_attribute('class')}")

        # Strategy 3: Check explicitly for the "AFRI 0370" panel header if we can find it
        # The screenshot shows a red header
        print("\nChecking for panel headers...")
        panels = scraper.driver.find_elements(By.CSS_SELECTOR, "#panel_1, .panel, .detail-view, div[id*='panel']")
        for panel in panels:
            print(f"Panel: {panel.get_attribute('id')} class='{panel.get_attribute('class')}'")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()
