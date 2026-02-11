"""
Export course schedule data from SQLite database to JSON format.
Parses course times and calculates current enrollment.
"""

import sqlite3
import json
import re
from typing import List, Dict, Optional, Tuple


def parse_days(day_string: str) -> List[str]:
    """
    Parse day abbreviations into individual days.
    
    Examples:
        'MWF' -> ['M', 'W', 'F']
        'TTh' -> ['T', 'Th']
        'M' -> ['M']
    """
    days = []
    i = 0
    while i < len(day_string):
        # Check for 'Th' first (two characters)
        if i < len(day_string) - 1 and day_string[i:i+2] == 'Th':
            days.append('Th')
            i += 2
        else:
            # Single character day
            days.append(day_string[i])
            i += 1
    return days


def parse_time(time_str: str) -> Optional[str]:
    """
    Parse time string to 24-hour format.
    
    Examples:
        '2:30p' -> '14:30'
        '12-12:50p' -> '12:00'
        '9a' -> '09:00'
        '10:30a' -> '10:30'
    """
    if not time_str:
        return None
    
    # Remove spaces
    time_str = time_str.strip()
    
    # Check if it ends with 'a' or 'p'
    is_pm = time_str.endswith('p')
    is_am = time_str.endswith('a')
    
    if not (is_pm or is_am):
        return None
    
    # Remove the 'a' or 'p'
    time_str = time_str[:-1]
    
    # Split on ':' to get hours and minutes
    if ':' in time_str:
        parts = time_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
    else:
        hours = int(time_str)
        minutes = 0
    
    # Convert to 24-hour format
    if is_pm and hours != 12:
        hours += 12
    elif is_am and hours == 12:
        hours = 0
    
    return f"{hours:02d}:{minutes:02d}"


def parse_course_times(course_times: str) -> Optional[Dict]:
    """
    Parse course time string into structured data.
    
    Examples:
        'TTh 2:30-3:50p' -> {
            'days': ['T', 'Th'],
            'start_time': '14:30',
            'end_time': '15:50'
        }
        'MWF 12-12:50p' -> {
            'days': ['M', 'W', 'F'],
            'start_time': '12:00',
            'end_time': '12:50'
        }
    """
    if not course_times or course_times.strip() == '':
        return None
    
    # Pattern: <days> <start>-<end>
    # Days can be: M, T, W, Th, F, S, Su
    # Times can be: 9a, 10:30a, 2:30p, etc.
    
    # Try to split on space to separate days from times
    parts = course_times.strip().split()
    if len(parts) < 2:
        return None
    
    days_str = parts[0]
    time_range = ' '.join(parts[1:])
    
    # Parse days
    days = parse_days(days_str)
    
    # Parse time range
    # Look for pattern: <start>-<end>
    time_match = re.search(r'([\d:]+[ap]?)-([\d:]+[ap])', time_range)
    if not time_match:
        return None
    
    start_str = time_match.group(1)
    end_str = time_match.group(2)
    
    # If start doesn't have a/p, inherit from end
    if not (start_str.endswith('a') or start_str.endswith('p')):
        if end_str.endswith('a'):
            start_str += 'a'
        elif end_str.endswith('p'):
            start_str += 'p'
    
    start_time = parse_time(start_str)
    end_time = parse_time(end_str)
    
    if not start_time or not end_time:
        return None
    
    return {
        'days': days,
        'start_time': start_time,
        'end_time': end_time
    }


def export_schedule_data(db_path: str, output_path: str):
    """
    Export course schedule data from database to JSON.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query courses with times
    cursor.execute('''
        SELECT course_code, course_name, course_times, instructor,
               max_enrollment, seats_available, section, crn
        FROM courses
        WHERE course_times IS NOT NULL AND course_times != ""
    ''')
    
    courses = []
    skipped = 0
    
    for row in cursor.fetchall():
        course_code, course_name, course_times, instructor, max_enrollment, seats_available, section, crn = row
        
        # Parse times
        parsed_times = parse_course_times(course_times)
        if not parsed_times:
            skipped += 1
            continue
        
        # Calculate current enrollment
        current_enrollment = 0
        if max_enrollment is not None and seats_available is not None:
            current_enrollment = max_enrollment - seats_available
        elif max_enrollment is not None:
            current_enrollment = max_enrollment
        
        course_data = {
            'code': course_code,
            'name': course_name,
            'instructor': instructor or '',
            'section': section or '',
            'crn': crn or '',
            'days': parsed_times['days'],
            'start_time': parsed_times['start_time'],
            'end_time': parsed_times['end_time'],
            'current_enrollment': current_enrollment,
            'max_enrollment': max_enrollment or 0,
            'raw_time_string': course_times
        }
        
        courses.append(course_data)
    
    conn.close()
    
    # Write to JSON
    output_data = {
        'courses': courses,
        'metadata': {
            'total_courses': len(courses),
            'skipped_courses': skipped
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"Exported {len(courses)} courses to {output_path}")
    print(f"Skipped {skipped} courses with unparseable times")


if __name__ == '__main__':
    export_schedule_data('brown_courses.db', 'schedule_data.json')
