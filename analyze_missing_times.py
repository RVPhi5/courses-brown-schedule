import sqlite3
import json

# Connect to database
conn = sqlite3.connect('brown_courses.db')
cursor = conn.cursor()

# Get total count
cursor.execute('SELECT COUNT(*) FROM courses')
total = cursor.fetchone()[0]
print(f"Total courses in database: {total}")

# Load exported data
with open('schedule_data.json', 'r') as f:
    data = json.load(f)
    exported = len(data['courses'])
    print(f"Exported courses: {exported}")
    print(f"Skipped: {total - exported}")

# Get sample of courses with times that weren't exported
cursor.execute('''
    SELECT course_code, course_times 
    FROM courses 
    WHERE course_times IS NOT NULL 
    AND course_times != ''
    AND course_times NOT LIKE '%-%'
    LIMIT 20
''')

print("\nSample courses with non-standard time formats:")
for row in cursor.fetchall():
    print(f"  {row[0]}: '{row[1]}'")

# Get courses with NULL or empty times
cursor.execute('''
    SELECT COUNT(*) 
    FROM courses 
    WHERE course_times IS NULL OR course_times = ''
''')
no_times = cursor.fetchone()[0]
print(f"\nCourses with no time data: {no_times}")

# Get courses with "Arranged" or "TBA"
cursor.execute('''
    SELECT COUNT(*) 
    FROM courses 
    WHERE course_times LIKE '%Arranged%' OR course_times LIKE '%TBA%'
''')
arranged = cursor.fetchone()[0]
print(f"Courses with 'Arranged' or 'TBA': {arranged}")

conn.close()
