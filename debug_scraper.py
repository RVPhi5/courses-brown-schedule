"""
Debug script to see what's happening with the scraper.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


def main():
    print("Starting debug scraper...")
    
    # Setup driver
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    
    try:
        # Navigate to site
        print("\n1. Loading https://cab.brown.edu/...")
        driver.get("https://cab.brown.edu/")
        time.sleep(3)
        
        # Find search box
        print("\n2. Looking for search box...")
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input"))
        )
        print(f"   Found input: {search_box.get_attribute('placeholder')}")
        
        # Click and press Enter
        print("\n3. Clicking search box and pressing Enter...")
        search_box.click()
        time.sleep(0.5)
        search_box.send_keys(Keys.RETURN)
        
        print("\n4. Waiting for results to load...")
        time.sleep(5)
        
        # Try to find course elements with different selectors
        print("\n5. Trying different selectors for course list...")
        
        selectors_to_try = [
            ".result",
            "[class*='result']",
            ".course",
            "[class*='course']",
            "li",
            "div[role='listitem']",
            ".search-result",
            "[class*='search']"
        ]
        
        for selector in selectors_to_try:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"   ✓ '{selector}' found {len(elements)} elements")
                    if len(elements) > 0 and len(elements) < 100:
                        print(f"     First element text: {elements[0].text[:100]}...")
                else:
                    print(f"   ✗ '{selector}' found 0 elements")
            except Exception as e:
                print(f"   ✗ '{selector}' error: {e}")
        
        # Save page source for inspection
        print("\n6. Saving page source...")
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("   Saved to page_source.html")
        
        # Take screenshot
        print("\n7. Taking screenshot...")
        driver.save_screenshot("debug_screenshot.png")
        print("   Saved to debug_screenshot.png")
        
        print("\n8. Keeping browser open for 30 seconds for manual inspection...")
        time.sleep(30)
        
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
        print("\nDebug complete!")


if __name__ == "__main__":
    main()
