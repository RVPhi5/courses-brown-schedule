"""
Database module for storing Brown University course catalog data.
"""

import sqlite3
from datetime import datetime
from typing import Dict, Optional, List
import os


class CourseDatabase:
    """Manages SQLite database for course information."""
    
    def __init__(self, db_path: str = "brown_courses.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
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
        """)
        self.conn.commit()
    
    def insert_course(self, course_data: Dict) -> bool:
        """
        Insert or update a course record.
        
        Args:
            course_data: Dictionary containing course information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.cursor.execute("""
                INSERT OR REPLACE INTO courses 
                (course_code, course_name, department, course_times, instructor, 
                 max_enrollment, seats_available, section, crn, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                course_data.get('course_code'),
                course_data.get('course_name'),
                course_data.get('department'),
                course_data.get('course_times'),
                course_data.get('instructor'),
                course_data.get('max_enrollment'),
                course_data.get('seats_available'),
                course_data.get('section'),
                course_data.get('crn'),
                datetime.now()
            ))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error inserting course: {e}")
            return False
    
    def get_course_by_crn(self, crn: str) -> Optional[Dict]:
        """
        Retrieve a course by CRN.
        
        Args:
            crn: Course Reference Number
            
        Returns:
            Course data dictionary or None
        """
        self.cursor.execute("SELECT * FROM courses WHERE crn = ?", (crn,))
        row = self.cursor.fetchone()
        if row:
            return self._row_to_dict(row)
        return None
    
    def get_all_courses(self) -> List[Dict]:
        """
        Retrieve all courses from database.
        
        Returns:
            List of course data dictionaries
        """
        self.cursor.execute("SELECT * FROM courses ORDER BY department, course_code")
        rows = self.cursor.fetchall()
        return [self._row_to_dict(row) for row in rows]
    
    def get_course_count(self) -> int:
        """
        Get total number of courses in database.
        
        Returns:
            Number of courses
        """
        self.cursor.execute("SELECT COUNT(*) FROM courses")
        return self.cursor.fetchone()[0]
    
    def _row_to_dict(self, row) -> Dict:
        """Convert database row to dictionary."""
        columns = ['id', 'course_code', 'course_name', 'department', 'course_times',
                   'instructor', 'max_enrollment', 'seats_available', 'section', 
                   'crn', 'last_updated']
        return dict(zip(columns, row))
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
