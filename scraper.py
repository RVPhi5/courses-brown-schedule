"""
Web scraper for Brown University course catalog.
Extracts course information including enrollment data.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from database import CourseDatabase


class BrownCourseScraper:
    """Scraper for Brown University course catalog."""
    
    def __init__(self, headless: bool = False):
        """
        Initialize the scraper.
        
        Args:
            headless: Run browser in headless mode (no GUI)
        """
        self.base_url = "https://cab.brown.edu/"
        self.db = CourseDatabase()
        self.driver = None
        self.headless = headless
        self.courses_scraped = 0
        
    def setup_driver(self):
        """Set up Chrome WebDriver."""
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
        
    def load_all_courses(self):
        """Navigate to site and load all courses."""
        print("Loading Brown course catalog...")
        self.driver.get(self.base_url)
        
        # Wait for page to load
        time.sleep(2)
        
        try:
            # Find the search box and click it
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='title, tag, subject, CRN or keyword']"))
            )
            
            # Click the search box and press Enter
            search_box.click()
            time.sleep(0.5)
            search_box.send_keys(Keys.RETURN)
            
            print("Waiting for course list to load...")
            # Wait for search results to appear
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".result"))
            )
            
            time.sleep(2)  # Additional wait for all courses to render
            print("Course list loaded successfully!")
            
        except TimeoutException:
            print("Error: Timeout waiting for course list to load")
            raise
    
    def get_course_count(self):
        """Get the total number of courses found."""
        try:
            count_element = self.driver.find_element(By.CSS_SELECTOR, ".result-count")
            count_text = count_element.text
            # Extract number from text like "Found 1645 courses"
            match = re.search(r'(\d+)', count_text)
            if match:
                return int(match.group(1))
        except:
            pass
        return 0
    
    def extract_department(self, course_code: str) -> str:
        """
        Extract department code from course code.
        
        Args:
            course_code: Full course code (e.g., "AFRI 0370")
            
        Returns:
            Department code (e.g., "AFRI")
        """
        match = re.match(r'^([A-Z]+)', course_code)
        return match.group(1) if match else ""
    
    def scrape_course_list(self, max_courses: int = None):
        """
        Scrape all courses from the list.
        
        Args:
            max_courses: Maximum number of courses to scrape (None for all)
        """
        total_courses = self.get_course_count()
        print(f"Found {total_courses} courses to scrape")
        
        if max_courses:
            total_courses = min(total_courses, max_courses)
            print(f"Limiting to {max_courses} courses")
        
        course_index = 0
        
        while course_index < total_courses:
            try:
                # Get all course elements (re-fetch to avoid stale references)
                course_elements = self.driver.find_elements(By.CSS_SELECTOR, ".result")
                
                if course_index >= len(course_elements):
                    print("No more courses found")
                    break
                
                course_element = course_elements[course_index]
                
                # Scroll to element
                self.driver.execute_script("arguments[0].scrollIntoView(true);", course_element)
                time.sleep(0.3)
                
                # Extract basic info from list view
                course_data = self.extract_list_data(course_element)
                
                if course_data:
                    # Click into course for enrollment data
                    try:
                        course_element.click()
                        time.sleep(1)
                        
                        # Extract enrollment data from detail page
                        enrollment_data = self.extract_enrollment_data()
                        course_data.update(enrollment_data)
                        
                        # Go back to list
                        self.driver.back()
                        time.sleep(1)
                        
                        # Save to database
                        self.db.insert_course(course_data)
                        self.courses_scraped += 1
                        
                        if self.courses_scraped % 10 == 0:
                            print(f"Progress: {self.courses_scraped}/{total_courses} courses scraped")
                        
                    except Exception as e:
                        print(f"Error processing course detail: {e}")
                        # Try to go back if we're stuck
                        try:
                            self.driver.back()
                            time.sleep(1)
                        except:
                            pass
                
                course_index += 1
                
            except StaleElementReferenceException:
                print(f"Stale element at index {course_index}, retrying...")
                continue
            except Exception as e:
                print(f"Error at course index {course_index}: {e}")
                course_index += 1
                continue
        
        print(f"\nScraping complete! Total courses scraped: {self.courses_scraped}")
    
    def extract_list_data(self, course_element) -> dict:
        """
        Extract course data from list view.
        
        Args:
            course_element: Selenium WebElement for the course
            
        Returns:
            Dictionary with course data
        """
        try:
            course_data = {}
            
            # Course code (e.g., "AFRI 0370")
            try:
                code_element = course_element.find_element(By.CSS_SELECTOR, ".result--group-start")
                course_data['course_code'] = code_element.text.strip()
                course_data['department'] = self.extract_department(course_data['course_code'])
            except:
                course_data['course_code'] = ""
                course_data['department'] = ""
            
            # Course name
            try:
                name_element = course_element.find_element(By.CSS_SELECTOR, ".result__title")
                course_data['course_name'] = name_element.text.strip()
            except:
                course_data['course_name'] = ""
            
            # Section
            try:
                section_element = course_element.find_element(By.CSS_SELECTOR, ".result__section")
                course_data['section'] = section_element.text.strip()
            except:
                course_data['section'] = ""
            
            # Course times
            try:
                time_element = course_element.find_element(By.CSS_SELECTOR, ".result__time")
                course_data['course_times'] = time_element.text.strip()
            except:
                course_data['course_times'] = ""
            
            # Instructor
            try:
                instructor_element = course_element.find_element(By.CSS_SELECTOR, ".result__instructor")
                course_data['instructor'] = instructor_element.text.strip()
            except:
                course_data['instructor'] = ""
            
            return course_data
            
        except Exception as e:
            print(f"Error extracting list data: {e}")
            return None
    
    def extract_enrollment_data(self) -> dict:
        """
        Extract enrollment data from course detail page.
        
        Returns:
            Dictionary with enrollment data and CRN
        """
        enrollment_data = {
            'max_enrollment': None,
            'seats_available': None,
            'crn': None
        }
        
        try:
            # Wait for detail page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".course-title"))
            )
            
            # Extract CRN from section info
            try:
                section_info = self.driver.find_element(By.CSS_SELECTOR, ".course-section-info")
                crn_match = re.search(r'CRN\s+(\d+)', section_info.text)
                if crn_match:
                    enrollment_data['crn'] = crn_match.group(1)
            except:
                pass
            
            # Extract enrollment numbers
            try:
                enrollment_text = self.driver.find_element(By.CSS_SELECTOR, ".course-enrollment").text
                
                # Parse "Maximum Enrollment: 40 / Seats Avail: 16"
                max_match = re.search(r'Maximum Enrollment:\s*(\d+)', enrollment_text)
                seats_match = re.search(r'Seats Avail:\s*(\d+)', enrollment_text)
                
                if max_match:
                    enrollment_data['max_enrollment'] = int(max_match.group(1))
                if seats_match:
                    enrollment_data['seats_available'] = int(seats_match.group(1))
                    
            except NoSuchElementException:
                # Enrollment info might not be available for all courses
                pass
            
        except Exception as e:
            print(f"Error extracting enrollment data: {e}")
        
        return enrollment_data
    
    def run(self, max_courses: int = None):
        """
        Run the complete scraping process.
        
        Args:
            max_courses: Maximum number of courses to scrape (None for all)
        """
        try:
            print("Starting Brown Course Catalog Scraper...")
            self.setup_driver()
            self.load_all_courses()
            self.scrape_course_list(max_courses)
            
        except Exception as e:
            print(f"Fatal error: {e}")
            raise
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        if self.driver:
            self.driver.quit()
        if self.db:
            self.db.close()
        print("Cleanup complete")


def main():
    """Main entry point."""
    # Create scraper instance
    scraper = BrownCourseScraper(headless=False)
    
    # Run scraper
    # Set max_courses to a small number for testing, or None to scrape all
    scraper.run(max_courses=None)  # Change to None to scrape all courses
    
    # Print summary
    print(f"\nDatabase summary:")
    db = CourseDatabase()
    print(f"Total courses in database: {db.get_course_count()}")
    db.close()


if __name__ == "__main__":
    main()
