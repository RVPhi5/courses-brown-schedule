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
                EC.presence_of_element_located((By.CSS_SELECTOR, ".result.result--group-start"))
            )
            
            time.sleep(2)  # Additional wait for all courses to render
            print("Course list loaded successfully!")
            
        except TimeoutException:
            print("Error: Timeout waiting for course list to load")
            raise
    
    def get_course_count(self):
        """Get the total number of courses found."""
        try:
            # Directly count the course elements
            course_elements = self.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")
            return len(course_elements)
        except:
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
                course_elements = self.driver.find_elements(By.CSS_SELECTOR, ".result.result--group-start")
                
                if course_index >= len(course_elements):
                    print("No more courses found")
                    break
                
                course_element = course_elements[course_index]
                
                # Scroll to element
                self.driver.execute_script("arguments[0].scrollIntoView(true);", course_element)
                time.sleep(0.3)
                
                # Extract basic info from list view
                course_data = self.extract_list_data(course_element)
                
                # Skip sections that start with 'C' (discussion/conference sections)
                if course_data and course_data.get('section', '').startswith('C'):
                    print(f"Skipping section {course_data.get('section')} for {course_data.get('course_code')}")
                    course_index += 1
                    continue
                
                if course_data:
                    # Click into course for enrollment data
                    try:
                        course_element.click()
                        time.sleep(1)
                        
                        # Check if we need to extract data from the detail page
                        # (for courses that don't show times/instructor in list view)
                        if not course_data.get('course_times') or not course_data.get('instructor'):
                            print(f"Extracting from All Sections table for {course_data.get('course_code')}")
                            # Extract everything from the All Sections table
                            section_data = self.extract_section_from_table(course_data.get('course_code', ''))
                            
                            # Update course_data with section table data
                            if section_data.get('course_times'):
                                course_data['course_times'] = section_data['course_times']
                            if section_data.get('instructor'):
                                course_data['instructor'] = section_data['instructor']
                            if section_data.get('crn'):
                                course_data['crn'] = section_data['crn']
                            if section_data.get('section'):
                                course_data['section'] = section_data['section']
                            if section_data.get('max_enrollment') is not None:
                                course_data['max_enrollment'] = section_data['max_enrollment']
                            if section_data.get('seats_available') is not None:
                                course_data['seats_available'] = section_data['seats_available']
                        else:
                            # Extract enrollment data normally
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
                code_element = course_element.find_element(By.CSS_SELECTOR, ".result__code")
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
            
            # Section - extract from the part section
            try:
                part_section = course_element.find_element(By.CSS_SELECTOR, ".result__part")
                # Section is in the flex--3 span
                section_element = part_section.find_element(By.CSS_SELECTOR, ".result__flex--3")
                section_text = section_element.text.strip()
                course_data['section'] = section_text
            except:
                course_data['section'] = ""
            
            # Course times - in flex--grow span
            try:
                time_element = course_element.find_element(By.CSS_SELECTOR, ".flex--grow")
                time_text = time_element.text.strip()
                # Remove "Meets:" prefix if present
                if "Meets:" in time_text:
                    time_text = time_text.replace("Meets:", "").strip()
                course_data['course_times'] = time_text
            except:
                course_data['course_times'] = ""
            
            # Instructor - in result__flex--9 text--right span
            try:
                instructor_element = course_element.find_element(By.CSS_SELECTOR, ".result__flex--9.text--right")
                instructor_text = instructor_element.text.strip()
                # Remove "Instructor:" prefix if present
                if "Instructor:" in instructor_text:
                    instructor_text = instructor_text.replace("Instructor:", "").strip()
                course_data['instructor'] = instructor_text
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
            # Wait for detail page to load - try multiple selectors
            time.sleep(1)
            
            # Try to get the entire page text and parse it
            try:
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                
                # Extract CRN - look for pattern "CRN 26343" or "CRN: 26343"
                crn_match = re.search(r'CRN[:\s]+(\d+)', page_text, re.IGNORECASE)
                if crn_match:
                    enrollment_data['crn'] = crn_match.group(1)
                
                # Extract enrollment - look for "Maximum Enrollment: 40 / Seats Avail: 16"
                enrollment_match = re.search(r'Maximum Enrollment[:\s]+(\d+)\s*/\s*Seats Avail[:\s]+(\d+)', page_text, re.IGNORECASE)
                if enrollment_match:
                    enrollment_data['max_enrollment'] = int(enrollment_match.group(1))
                    enrollment_data['seats_available'] = int(enrollment_match.group(2))
                else:
                    # Try alternative pattern
                    max_match = re.search(r'Maximum Enrollment[:\s]+(\d+)', page_text, re.IGNORECASE)
                    seats_match = re.search(r'Seats Avail[:\s]+(\d+)', page_text, re.IGNORECASE)
                    
                    if max_match:
                        enrollment_data['max_enrollment'] = int(max_match.group(1))
                    if seats_match:
                        enrollment_data['seats_available'] = int(seats_match.group(1))
                        
            except Exception as e:
                print(f"Could not extract from page text: {e}")
            
        except Exception as e:
            print(f"Error extracting enrollment data: {e}")
        
        return enrollment_data
    
    def extract_section_from_table(self, course_code: str) -> dict:
        """
        Extract section data from the "All Sections" table on the detail page.
        This is used for courses that don't show times/instructor in the list view.
        
        Args:
            course_code: The course code to help with logging
            
        Returns:
            Dictionary with section data (times, instructor, CRN, enrollment)
        """
        section_data = {
            'course_times': '',
            'instructor': '',
            'crn': None,
            'max_enrollment': None,
            'seats_available': None,
            'section': ''
        }
        
        try:
            time.sleep(1)
            
            # Look for the "All Sections" table
            # Try to find rows in the table - S01 row should have the data
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Look for S01 section data in the table
            # Pattern: S01 followed by CRN, Meets time, and Instructor
            # Example from table: "S01    26810    MWF 12-12:50p    K. Mallory"
            
            # Try to find the table and parse it
            try:
                # Find all table rows
                rows = self.driver.find_elements(By.CSS_SELECTOR, "table tr, .section-row, [class*='section']")
                
                for row in rows:
                    row_text = row.text.strip()
                    
                    # Look for S01 in the row
                    if re.search(r'\bS01\b', row_text):
                        # Try to extract data from the row
                        # Pattern: S01 <CRN> <Meets> <Instructor>
                        parts = row_text.split()
                        
                        if len(parts) >= 4:
                            section_data['section'] = 'S01'
                            
                            # Try to find CRN (5-digit number)
                            for i, part in enumerate(parts):
                                if part.isdigit() and len(part) == 5:
                                    section_data['crn'] = part
                                    
                                    # Times should be after CRN
                                    if i + 1 < len(parts):
                                        # Collect time parts (e.g., "MWF 12-12:50p")
                                        time_parts = []
                                        j = i + 1
                                        while j < len(parts) and not parts[j][0].isupper() or re.match(r'^[MTWRF]+$', parts[j]):
                                            time_parts.append(parts[j])
                                            j += 1
                                            if j < len(parts) and re.search(r'\d', parts[j]):
                                                time_parts.append(parts[j])
                                                j += 1
                                                break
                                        
                                        if time_parts:
                                            section_data['course_times'] = ' '.join(time_parts)
                                        
                                        # Instructor is the rest
                                        if j < len(parts):
                                            section_data['instructor'] = ' '.join(parts[j:])
                                    break
                        
                        # If we found S01, we're done
                        if section_data['section'] == 'S01':
                            break
                
                # If table parsing didn't work, try regex on full page text
                if not section_data['section']:
                    # Look for pattern: S01 followed by 5-digit CRN, time, and instructor
                    s01_match = re.search(r'S01\s+(\d{5})\s+([MTWRF\s\d:\-apm]+)\s+([A-Z][^\n]+)', page_text)
                    if s01_match:
                        section_data['section'] = 'S01'
                        section_data['crn'] = s01_match.group(1)
                        section_data['course_times'] = s01_match.group(2).strip()
                        section_data['instructor'] = s01_match.group(3).strip()
                
            except Exception as e:
                print(f"Error parsing table for {course_code}: {e}")
            
            # Also try to get enrollment data
            # Look for "Current enrollment: 143" or "Maximum Enrollment: X / Seats Avail: Y"
            enrollment_match = re.search(r'Current enrollment[:\s]+(\d+)', page_text, re.IGNORECASE)
            if enrollment_match:
                section_data['max_enrollment'] = int(enrollment_match.group(1))
                # For current enrollment, seats available would be 0 or we need to find max
                # Try to find max enrollment separately
                max_match = re.search(r'Maximum Enrollment[:\s]+(\d+)', page_text, re.IGNORECASE)
                if max_match:
                    actual_max = int(max_match.group(1))
                    current = int(enrollment_match.group(1))
                    section_data['max_enrollment'] = actual_max
                    section_data['seats_available'] = max(0, actual_max - current)
            else:
                # Try the standard pattern
                enrollment_match = re.search(r'Maximum Enrollment[:\s]+(\d+)\s*/\s*Seats Avail[:\s]+(\d+)', page_text, re.IGNORECASE)
                if enrollment_match:
                    section_data['max_enrollment'] = int(enrollment_match.group(1))
                    section_data['seats_available'] = int(enrollment_match.group(2))
            
        except Exception as e:
            print(f"Error extracting section table data for {course_code}: {e}")
        
        return section_data
    
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
