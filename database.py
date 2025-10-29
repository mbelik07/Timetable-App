import sqlite3
from typing import List, Optional, Tuple

DB_FILENAME = "timetable.db"


class Database:
    def __init__(self, db_path: str = DB_FILENAME):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._enable_foreign_keys()
        self._create_tables()

    def _enable_foreign_keys(self):
        self.conn.execute("PRAGMA foreign_keys = ON;")

    def _create_tables(self):
        cur = self.conn.cursor()
        # Teachers table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            );
        """
        )
        # Courses table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT,
                name TEXT NOT NULL
            );
        """
        )
        # Units table - linked to a course
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS units (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT,
                name TEXT NOT NULL,
                course_id INTEGER,
                FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
            );
        """
        )
        # Schedule table - one entry per (day, timeslot)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT NOT NULL,
                timeslot TEXT NOT NULL,
                teacher_id INTEGER,
                unit_id INTEGER,
                room TEXT,
                UNIQUE(day, timeslot),
                FOREIGN KEY(teacher_id) REFERENCES teachers(id) ON DELETE SET NULL,
                FOREIGN KEY(unit_id) REFERENCES units(id) ON DELETE SET NULL
            );
        """
        )
        self.conn.commit()

    # ----- Teachers -----
    def add_teacher(self, name: str) -> int:
        cur = self.conn.cursor()
        cur.execute("INSERT INTO teachers (name) VALUES (?)", (name,))
        self.conn.commit()
        return cur.lastrowid

    def delete_teacher(self, teacher_id: int):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
        self.conn.commit()

    def get_teachers(self) -> List[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, name FROM teachers ORDER BY name")
        return cur.fetchall()

    # ----- Courses -----
    def add_course(self, code: Optional[str], name: str) -> int:
        cur = self.conn.cursor()
        cur.execute("INSERT INTO courses (code, name) VALUES (?, ?)", (code, name))
        self.conn.commit()
        return cur.lastrowid

    def delete_course(self, course_id: int):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM courses WHERE id = ?", (course_id,))
        self.conn.commit()

    def get_courses(self) -> List[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, code, name FROM courses ORDER BY name")
        return cur.fetchall()

    def get_course_by_id(self, course_id: int) -> Optional[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute("SELECT id, code, name FROM courses WHERE id = ?", (course_id,))
        return cur.fetchone()

    # ----- Units -----
    def add_unit(self, code: Optional[str], name: str, course_id: Optional[int]) -> int:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO units (code, name, course_id) VALUES (?, ?, ?)",
            (code, name, course_id),
        )
        self.conn.commit()
        return cur.lastrowid

    def delete_unit(self, unit_id: int):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM units WHERE id = ?", (unit_id,))
        self.conn.commit()

    def get_units(self) -> List[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT u.id, u.code, u.name, u.course_id, c.name AS course_name, c.code AS course_code
            FROM units u
            LEFT JOIN courses c ON u.course_id = c.id
            ORDER BY u.name
            """
        )
        return cur.fetchall()

    def get_units_by_course(self, course_id: int) -> List[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT u.id, u.code, u.name, u.course_id
            FROM units u
            WHERE u.course_id = ?
            ORDER BY u.name
            """,
            (course_id,),
        )
        return cur.fetchall()

    def get_unit_by_id(self, unit_id: int) -> Optional[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT u.id, u.code, u.name, u.course_id, c.name AS course_name, c.code AS course_code
            FROM units u
            LEFT JOIN courses c ON u.course_id = c.id
            WHERE u.id = ?
            """,
            (unit_id,),
        )
        return cur.fetchone()

    # ----- Schedule -----
    def get_all_schedule(self) -> List[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT s.id, s.day, s.timeslot, s.teacher_id, s.unit_id, s.room,
                   t.name AS teacher_name, u.name AS unit_name, u.code AS unit_code
            FROM schedule s
            LEFT JOIN teachers t ON s.teacher_id = t.id
            LEFT JOIN units u ON s.unit_id = u.id
            ORDER BY
              CASE s.day WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 ELSE 6 END,
              CASE s.timeslot WHEN 'Morning' THEN 1 WHEN 'Afternoon' THEN 2 WHEN 'Night' THEN 3 ELSE 4 END
            """
        )
        return cur.fetchall()

    def get_schedule_cell(self, day: str, timeslot: str) -> Optional[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT s.id, s.day, s.timeslot, s.teacher_id, s.unit_id, s.room,
                   t.name AS teacher_name, u.name AS unit_name, u.code AS unit_code
            FROM schedule s
            LEFT JOIN teachers t ON s.teacher_id = t.id
            LEFT JOIN units u ON s.unit_id = u.id
            WHERE s.day = ? AND s.timeslot = ?
            """,
            (day, timeslot),
        )
        return cur.fetchone()

    def add_or_update_schedule(
        self, day: str, timeslot: str, teacher_id: Optional[int], unit_id: Optional[int], room: Optional[str]
    ) -> int:
        cur = self.conn.cursor()
        # Insert or replace using unique(day,timeslot)
        # We'll attempt to update first
        existing = self.get_schedule_cell(day, timeslot)
        if existing:
            cur.execute(
                "UPDATE schedule SET teacher_id = ?, unit_id = ?, room = ? WHERE day = ? AND timeslot = ?",
                (teacher_id, unit_id, room, day, timeslot),
            )
            self.conn.commit()
            return existing["id"]
        else:
            cur.execute(
                "INSERT INTO schedule (day, timeslot, teacher_id, unit_id, room) VALUES (?, ?, ?, ?, ?)",
                (day, timeslot, teacher_id, unit_id, room),
            )
            self.conn.commit()
            return cur.lastrowid

    def delete_schedule(self, day: str, timeslot: str):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM schedule WHERE day = ? AND timeslot = ?", (day, timeslot))
        self.conn.commit()

    # Close connection
    def close(self):
        self.conn.close()


# Simple convenience factory
def get_db(db_path: str = DB_FILENAME) -> Database:
    return Database(db_path)
