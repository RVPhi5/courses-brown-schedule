"""
Inspect detail page to find a Back or Close button.
"""
from scraper import BrownCourseScraper
from selenium.webdriver.common.by import By
import time

def main():
    print("Inspecting detail page navigation...")
    scraper = BrownCourseScraper(headless=False)
    
    try:
        scraper.setup_driver()
        scraper.load_all_courses()
        
        print("\nClicking first course...")
        course_elements = scraper.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")
        course_elements[0].click()
        time.sleep(2)
        
        print("In detail page.")
        
        # Look for typical back buttons
        print("\nSearching for 'Back' buttons...")
        buttons = scraper.driver.find_elements(By.TAG_NAME, "button")
        for btn in buttons:
            text = btn.text.strip()
            if text and len(text) < 30:
                print(f"Button: '{text}' (class: {btn.get_attribute('class')})")
                
        links = scraper.driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            text = link.text.strip()
            if text and ("Back" in text or "Return" in text or "Results" in text):
                print(f"Link: '{text}' (href: {link.get_attribute('href')})")
        
        # Look for specific classes
        back_arrow = scraper.driver.find_elements(By.CSS_SELECTOR, ".back-button, .return-link, .close-detail")
        if back_arrow:
            print(f"Found specific back selectors: {len(back_arrow)}")
            
        # Print top 1000 chars of body to see structure
        print("\nTop HTML:")
        body = scraper.driver.find_element(By.TAG_NAME, "body")
        print(body.get_attribute('innerHTML')[:1000])
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()
