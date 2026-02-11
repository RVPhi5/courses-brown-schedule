import sqlite3

conn = sqlite3.connect('brown_courses.db')
cursor = conn.cursor()

# Get column names
cursor.execute('SELECT * FROM courses LIMIT 1')
columns = [desc[0] for desc in cursor.description]
print("Columns:", columns)
print()

# Get sample data with times
cursor.execute('''
    SELECT course_code, course_name, course_times, instructor, 
           max_enrollment, seats_available 
    FROM courses 
    WHERE course_times IS NOT NULL AND course_times != "" 
    LIMIT 10
''')

print("Sample courses with times:")
for row in cursor.fetchall():
    print(row)

conn.close()
