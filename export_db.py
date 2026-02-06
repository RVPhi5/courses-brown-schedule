"""
Export database to CSV for easy viewing.
"""
import sqlite3
import csv
from database import CourseDatabase

def main():
    print("Exporting database to brown_courses.csv...")
    
    db = CourseDatabase()
    courses = db.get_all_courses()
    
    if not courses:
        print("No courses found in database.")
        return

    # Get headers from first dictionary
    headers = list(courses[0].keys())
    
    with open('brown_courses.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(courses)
        
    print(f"Successfully exported {len(courses)} courses to brown_courses.csv")
    print("You can now open 'brown_courses.csv' in Excel or any text editor.")

if __name__ == "__main__":
    main()
