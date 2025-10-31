
import sqlite3
from typing import List, Optional

DB_FILENAME = "timetable.db"

class Database:
    def __init__(self, db_path: str = DB_FILENAME):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self._create_tables()

    def _create_tables(self):
        with self.conn:
            # Core Data Tables
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS colleges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                );
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    college_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    capacity INTEGER DEFAULT 0,
                    type TEXT,
                    FOREIGN KEY(college_id) REFERENCES colleges(id) ON DELETE CASCADE
                );
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS teachers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    initials TEXT,
                    email TEXT,
                    home_college_id INTEGER,
                    FOREIGN KEY(home_college_id) REFERENCES colleges(id) ON DELETE SET NULL
                );
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT,
                    name TEXT NOT NULL
                );
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS units (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id INTEGER NOT NULL,
                    code TEXT,
                    name TEXT NOT NULL,
                    required_hours INTEGER DEFAULT 0,
                    FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
                );
            """)
            # Linking Tables (Many-to-Many Relationships)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS teacher_qualifications (
                    teacher_id INTEGER NOT NULL,
                    unit_id INTEGER NOT NULL,
                    PRIMARY KEY (teacher_id, unit_id),
                    FOREIGN KEY(teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
                    FOREIGN KEY(unit_id) REFERENCES units(id) ON DELETE CASCADE
                );
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS teacher_availability (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    teacher_id INTEGER NOT NULL,
                    day TEXT NOT NULL,
                    time_slot TEXT NOT NULL, -- "08:00", "08:30", etc.
                    is_available BOOLEAN DEFAULT TRUE,
                    UNIQUE(teacher_id, day, time_slot),
                    FOREIGN KEY(teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
                );
            """)
            # The Main Timetable Schedule
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS schedule (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    college_id INTEGER NOT NULL,
                    day TEXT NOT NULL,
                    start_time TEXT NOT NULL, -- "08:00", "08:30", etc.
                    duration_minutes INTEGER NOT NULL,
                    unit_id INTEGER NOT NULL,
                    teacher_id INTEGER,
                    room_id INTEGER,
                    FOREIGN KEY(college_id) REFERENCES colleges(id) ON DELETE CASCADE,
                    FOREIGN KEY(unit_id) REFERENCES units(id) ON DELETE CASCADE,
                    FOREIGN KEY(teacher_id) REFERENCES teachers(id) ON DELETE SET NULL,
                    FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE SET NULL
                );
            """)

    # --- Management Methods for each table ---
    
    def get_colleges(self) -> List[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, name FROM colleges ORDER BY name")
        return cur.fetchall()

    def get_teachers(self) -> List[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, initials, email FROM teachers ORDER BY name")
        return cur.fetchall()
        
    def get_courses(self) -> List[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, code, name FROM courses ORDER BY name")
        return cur.fetchall()

    def get_units(self) -> List[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT u.id, u.code, u.name, u.required_hours, c.name as course_name
            FROM units u
            JOIN courses c ON u.course_id = c.id
            ORDER BY c.name, u.name
        """)
        return cur.fetchall()

    def get_rooms(self) -> List[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT r.id, r.name, r.capacity, r.type, c.name as college_name
            FROM rooms r
            JOIN colleges c ON r.college_id = c.id
            ORDER BY c.name, r.name
        """)
        return cur.fetchall()

    def get_unscheduled_units_summary(self) -> List[sqlite3.Row]:
        """
        Calculates the required vs. scheduled hours for each unit
        to determine what still needs to be scheduled.
        """
        cur = self.conn.cursor()
        cur.execute("""
            SELECT
                u.id,
                u.code,
                u.name,
                c.name as course_name,
                u.required_hours,
                COALESCE(SUM(s.duration_minutes) / 60.0, 0) as scheduled_hours
            FROM units u
            LEFT JOIN schedule s ON u.id = s.unit_id
            JOIN courses c ON u.course_id = c.id
            GROUP BY u.id
            HAVING scheduled_hours < u.required_hours
            ORDER BY c.name, u.name;
        """)
        return cur.fetchall()

    def close(self):
        self.conn.close()


def get_db(db_path: str = DB_FILENAME) -> Database:
    db = Database(db_path)
    # Ensure default colleges exist on first run
    if not db.get_colleges():
        with db.conn:
            db.conn.execute("INSERT OR IGNORE INTO colleges (name) VALUES (?)", ("Moss Vale",))
            db.conn.execute("INSERT OR IGNORE INTO colleges (name) VALUES (?)", ("Goulburn",))
            db.conn.execute("INSERT OR IGNORE INTO colleges (name) VALUES (?)", ("Queanbeyan",))
    return db

