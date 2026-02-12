import sqlite3

conn = sqlite3.connect('brown_courses.db')
cursor = conn.cursor()

# Total courses
cursor.execute('SELECT COUNT(*) FROM courses')
total = cursor.fetchone()[0]
print(f"Total courses: {total}")

# Courses with empty/null times
cursor.execute("SELECT COUNT(*) FROM courses WHERE course_times IS NULL OR course_times = ''")
no_time = cursor.fetchone()[0]
print(f"Courses with no time: {no_time}")

# Courses with "Arranged"
cursor.execute("SELECT COUNT(*) FROM courses WHERE course_times LIKE '%Arranged%'")
arranged = cursor.fetchone()[0]
print(f"Courses with 'Arranged': {arranged}")

# Sample of courses with times
cursor.execute("SELECT course_code, course_times FROM courses WHERE course_times IS NOT NULL AND course_times != '' LIMIT 50")
print("\nSample course times:")
for code, times in cursor.fetchall()[:20]:
    print(f"  {code}: {times}")

conn.close()
