# Brown Course Catalog Scraper

A Python web scraper that extracts comprehensive course information from Brown University's course catalog (https://cab.brown.edu/).

## Features

- **Automated Data Collection**: Uses Selenium to navigate the course catalog and extract data
- **Comprehensive Information**: Collects course names, codes, times, instructors, departments, and enrollment data
- **SQLite Database**: Stores all course information in a structured database
- **Progress Tracking**: Shows real-time progress during scraping
- **Error Handling**: Robust error handling and retry logic for reliable scraping

## Data Collected

For each course, the scraper collects:
- Course code (e.g., "AFRI 0370")
- Course name (e.g., "African American Novels of the 1970s")
- Department (e.g., "AFRI")
- Course times (e.g., "M 3-5:30p")
- Instructor name
- Section number
- CRN (Course Reference Number)
- Maximum enrollment
- Seats available
- Last updated timestamp

**Note**: The scraper automatically **skips sections starting with "C"** (discussion/conference sections) and only collects data for primary course sections (typically starting with "S").

## Installation

1. **Prerequisites**:
   - Python 3.7 or higher
   - Google Chrome browser installed

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Run the scraper to collect all courses:

```bash
python scraper.py
```

### Testing with Limited Courses

To test the scraper with only the first 10 courses, edit `scraper.py` and change:

```python
scraper.run(max_courses=None)  # Scrape all courses
```

to:

```python
scraper.run(max_courses=10)  # Scrape only 10 courses
```

### Headless Mode

To run without opening a visible browser window, modify the scraper initialization:

```python
scraper = BrownCourseScraper(headless=True)
```

## Database

The scraper creates a SQLite database file `brown_courses.db` with the following schema:

```sql
CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT NOT NULL,
    course_name TEXT NOT NULL,
    department TEXT NOT NULL,
    course_times TEXT,
    instructor TEXT,
    max_enrollment INTEGER,
    seats_available INTEGER,
    section TEXT,
    crn TEXT UNIQUE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(course_code, section)
)
```

### Querying the Database

You can query the database using Python:

```python
from database import CourseDatabase

db = CourseDatabase()

# Get all courses
courses = db.get_all_courses()

# Get a specific course by CRN
course = db.get_course_by_crn("26343")

# Get total count
count = db.get_course_count()

db.close()
```

Or use any SQLite client:

```bash
sqlite3 brown_courses.db "SELECT * FROM courses WHERE department = 'AFRI'"
```

## Performance

- **Scraping Time**: Approximately 30-60 minutes for ~1,645 courses (depends on network speed and page load times)
- **Progress Updates**: Shows progress every 10 courses
- **Database Updates**: Courses are saved to the database in real-time

## Troubleshooting

### ChromeDriver Issues

If you encounter ChromeDriver errors:
- Ensure Google Chrome is installed
- The `webdriver-manager` package will automatically download the correct ChromeDriver version

### Timeout Errors

If the scraper times out:
- Check your internet connection
- The website might be slow; increase timeout values in the code
- Try running in non-headless mode to see what's happening

### Stale Element Errors

The scraper includes retry logic for stale element references. If you see these errors frequently:
- The page structure might have changed
- Increase the `time.sleep()` delays in the code

## File Structure

```
courses-brown-schedule/
├── scraper.py          # Main scraper script
├── database.py         # Database management module
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── brown_courses.db   # SQLite database (created after running)
```

## Notes

- The scraper respects the website by including appropriate delays between requests
- Duplicate courses (by CRN) are automatically handled with INSERT OR REPLACE
- The scraper can be stopped and restarted; it will update existing courses in the database

## License

This tool is for educational purposes. Please respect Brown University's terms of service when using this scraper.
