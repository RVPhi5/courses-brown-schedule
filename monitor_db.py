"""
Monitor the database while the scraper runs.
"""

from database import CourseDatabase
import time


def main():
    print("Monitoring database... (Press Ctrl+C to stop)\n")
    
    db = CourseDatabase()
    last_count = 0
    
    try:
        while True:
            count = db.get_course_count()
            if count != last_count:
                print(f"[{time.strftime('%H:%M:%S')}] Courses in database: {count}")
                last_count = count
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\nStopped monitoring")
        print(f"Final count: {db.get_course_count()} courses")
    finally:
        db.close()


if __name__ == "__main__":
    main()
