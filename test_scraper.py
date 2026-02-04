"""
Test script to verify the scraper works with a small number of courses.
"""

from scraper import BrownCourseScraper
from database import CourseDatabase


def main():
    print("=" * 60)
    print("Brown Course Catalog Scraper - Test Run")
    print("=" * 60)
    print("\nThis will scrape only the first 5 courses as a test.\n")
    
    # Create scraper instance (not headless so you can see what's happening)
    scraper = BrownCourseScraper(headless=False)
    
    # Run scraper with limit of 5 courses
    scraper.run(max_courses=5)
    
    # Print results
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    
    db = CourseDatabase()
    courses = db.get_all_courses()
    
    print(f"\nTotal courses in database: {len(courses)}\n")
    
    for i, course in enumerate(courses, 1):
        print(f"\nCourse {i}:")
        print(f"  Code: {course['course_code']}")
        print(f"  Name: {course['course_name']}")
        print(f"  Department: {course['department']}")
        print(f"  Times: {course['course_times']}")
        print(f"  Instructor: {course['instructor']}")
        print(f"  Section: {course['section']}")
        print(f"  CRN: {course['crn']}")
        print(f"  Max Enrollment: {course['max_enrollment']}")
        print(f"  Seats Available: {course['seats_available']}")
    
    db.close()
    
    print("\n" + "=" * 60)
    print("Test complete! If the data looks correct, you can run")
    print("the full scraper with: python scraper.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
