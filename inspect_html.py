"""
Inspect first course element HTML to see if it's a link.
"""
from scraper import BrownCourseScraper
from selenium.webdriver.common.by import By
import time

def main():
    print("Inspecting course element HTML...")
    scraper = BrownCourseScraper(headless=False)
    
    try:
        scraper.setup_driver()
        scraper.load_all_courses()
        
        print("\nFinding first course...")
        course_elements = scraper.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")
        
        if course_elements:
            elem = course_elements[0]
            print(f"Tag name: {elem.tag_name}")
            
            # Print outer HTML (truncated)
            html = elem.get_attribute('outerHTML')
            print("\nOuter HTML start:")
            print(html[:1000])
            
            # Check for links inside
            links = elem.find_elements(By.TAG_NAME, "a")
            print(f"\nLinks found inside: {len(links)}")
            for link in links:
                print(f"Link text: '{link.text}', href: '{link.get_attribute('href')}'")
                
            # Check for onclick
            print(f"\nOnclick attribute: {elem.get_attribute('onclick')}")
            
            # Check data attributes that might contain URL
            print(f"data-url: {elem.get_attribute('data-url')}")
            print(f"data-href: {elem.get_attribute('data-href')}")
            
        else:
            print("No courses found.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()
