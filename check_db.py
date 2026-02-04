"""Quick script to check database contents."""
from database import CourseDatabase

db = CourseDatabase()
courses = db.get_all_courses()

print(f"\nTotal courses in database: {len(courses)}\n")

for i, course in enumerate(courses[:10], 1):
    print(f"{i}. {course['course_code']} - {course['course_name']}")
    print(f"   Instructor: {course['instructor']}")
    print(f"   Times: {course['course_times']}")
    print(f"   Enrollment: {course['max_enrollment']} max, {course['seats_available']} available")
    print(f"   CRN: {course['crn']}")
    print()

db.close()
