"""
Math Quiz - Database Integration Module
Stores quiz results, user progress, and settings in SQLite database
"""

import sqlite3
from datetime import datetime, timezone
from typing import Optional, Dict, List, Tuple
import pytz

TZ = pytz.timezone("Asia/Tashkent")


def init_math_tables(db_path: str):
    """Initialize trigonometry-related database tables"""
    conn = sqlite3.connect(db_path)
    
    # Create each table separately
    conn.execute("""
        CREATE TABLE IF NOT EXISTS math_quiz_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tg_id INTEGER NOT NULL,
            session_start TEXT NOT NULL,
            session_end TEXT,
            total_questions INTEGER NOT NULL,
            correct_count INTEGER NOT NULL DEFAULT 0,
            wrong_count INTEGER NOT NULL DEFAULT 0,
            percentage REAL NOT NULL DEFAULT 0.0,
            status TEXT NOT NULL DEFAULT 'in_progress',
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS math_quiz_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            question_number INTEGER NOT NULL,
            angle INTEGER NOT NULL,
            function TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            user_answer TEXT NOT NULL,
            is_correct INTEGER NOT NULL,
            answered_at TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES math_quiz_sessions(id) ON DELETE CASCADE
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS math_user_stats (
            user_id INTEGER PRIMARY KEY,
            tg_id INTEGER NOT NULL,
            total_sessions INTEGER NOT NULL DEFAULT 0,
            total_questions INTEGER NOT NULL DEFAULT 0,
            total_correct INTEGER NOT NULL DEFAULT 0,
            total_wrong INTEGER NOT NULL DEFAULT 0,
            average_percentage REAL NOT NULL DEFAULT 0.0,
            best_score REAL NOT NULL DEFAULT 0.0,
            best_session_id INTEGER,
            last_quiz_date TEXT,
            unlocked_date TEXT,
            is_unlocked INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(best_session_id) REFERENCES math_quiz_sessions(id) ON DELETE SET NULL
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS math_question_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            angle INTEGER NOT NULL,
            function TEXT NOT NULL,
            total_attempts INTEGER NOT NULL DEFAULT 0,
            correct_attempts INTEGER NOT NULL DEFAULT 0,
            accuracy REAL NOT NULL DEFAULT 0.0,
            last_attempted TEXT,
            UNIQUE(user_id, angle, function),
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Create indexes
    conn.execute("CREATE INDEX IF NOT EXISTS idx_math_sessions_user ON math_quiz_sessions(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_math_sessions_status ON math_quiz_sessions(status)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_math_answers_session ON math_quiz_answers(session_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_math_question_stats ON math_question_stats(user_id)")
    
    conn.commit()
    conn.close()


class MathDatabase:
    """Database manager for trigonometry quiz"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def unlock_user(self, user_id: int, tg_id: int) -> bool:
        """Unlock trigonometry module for user after correct code"""
        conn = sqlite3.connect(self.db_path)
        now = datetime.now(TZ).isoformat()
        
        try:
            conn.execute(
                """
                INSERT OR IGNORE INTO math_user_stats 
                (user_id, tg_id, is_unlocked, unlocked_date)
                VALUES (?, ?, 1, ?)
                """,
                (user_id, tg_id, now)
            )
            conn.execute(
                """
                UPDATE math_user_stats 
                SET is_unlocked = 1, unlocked_date = ?
                WHERE user_id = ?
                """,
                (now, user_id)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error unlocking user: {e}")
            return False
        finally:
            conn.close()
    
    def is_user_unlocked(self, user_id: int) -> bool:
        """Check if user has unlocked trigonometry module"""
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute(
                "SELECT is_unlocked FROM math_user_stats WHERE user_id = ?",
                (user_id,)
            )
            row = cur.fetchone()
            return row[0] == 1 if row else False
        finally:
            conn.close()
    
    def create_quiz_session(self, user_id: int, tg_id: int, total_questions: int) -> int:
        """Create new quiz session and return session_id"""
        conn = sqlite3.connect(self.db_path)
        now = datetime.now(TZ).isoformat()
        
        try:
            cur = conn.execute(
                """
                INSERT INTO math_quiz_sessions 
                (user_id, tg_id, session_start, total_questions)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, tg_id, now, total_questions)
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()
    
    def save_quiz_answer(self, session_id: int, question_num: int, angle: int, 
                        function: str, correct_answer: str, user_answer: str, 
                        is_correct: bool) -> int:
        """Save user's answer to a question"""
        conn = sqlite3.connect(self.db_path)
        now = datetime.now(TZ).isoformat()
        
        try:
            cur = conn.execute(
                """
                INSERT INTO math_quiz_answers 
                (session_id, question_number, angle, function, correct_answer, user_answer, is_correct, answered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (session_id, question_num, angle, function, correct_answer, user_answer, int(is_correct), now)
            )
            conn.commit()
            
            # Update question stats
            self._update_question_stats(conn, session_id, angle, function, is_correct)
            
            return cur.lastrowid
        finally:
            conn.close()
    
    def _update_question_stats(self, conn: sqlite3.Connection, session_id: int, 
                               angle: int, function: str, is_correct: bool):
        """Update statistics for specific angle-function pair"""
        # Get user_id from session
        cur = conn.execute(
            "SELECT user_id FROM math_quiz_sessions WHERE id = ?",
            (session_id,)
        )
        row = cur.fetchone()
        if not row:
            return
        
        user_id = row[0]
        now = datetime.now(TZ).isoformat()
        
        # Insert or update question stats
        conn.execute(
            """
            INSERT INTO math_question_stats 
            (user_id, angle, function, total_attempts, correct_attempts, accuracy, last_attempted)
            VALUES (?, ?, ?, 1, ?, 0, ?)
            ON CONFLICT(user_id, angle, function) DO UPDATE SET
                total_attempts = total_attempts + 1,
                correct_attempts = correct_attempts + ?,
                last_attempted = ?
            """,
            (user_id, angle, function, int(is_correct), now, int(is_correct), now)
        )
        
        # Recalculate accuracy
        cur = conn.execute(
            """
            SELECT total_attempts, correct_attempts FROM math_question_stats 
            WHERE user_id = ? AND angle = ? AND function = ?
            """,
            (user_id, angle, function)
        )
        row = cur.fetchone()
        if row:
            total, correct = row
            accuracy = (correct / total * 100) if total > 0 else 0
            conn.execute(
                """
                UPDATE math_question_stats 
                SET accuracy = ? WHERE user_id = ? AND angle = ? AND function = ?
                """,
                (accuracy, user_id, angle, function)
            )
        
        conn.commit()
    
    def finish_quiz_session(self, session_id: int, correct_count: int, 
                           wrong_count: int) -> Dict:
        """Finish quiz session and update user stats"""
        conn = sqlite3.connect(self.db_path)
        now = datetime.now(TZ).isoformat()
        
        try:
            total = correct_count + wrong_count
            percentage = (correct_count / total * 100) if total > 0 else 0
            
            # Update session
            conn.execute(
                """
                UPDATE math_quiz_sessions 
                SET session_end = ?, correct_count = ?, wrong_count = ?, percentage = ?, status = 'completed'
                WHERE id = ?
                """,
                (now, correct_count, wrong_count, percentage, session_id)
            )
            
            # Get user_id
            cur = conn.execute(
                "SELECT user_id, tg_id FROM math_quiz_sessions WHERE id = ?",
                (session_id,)
            )
            row = cur.fetchone()
            user_id, tg_id = row
            
            # Update user stats
            cur = conn.execute(
                """
                SELECT total_sessions, total_questions, total_correct, total_wrong, average_percentage, best_score
                FROM math_user_stats WHERE user_id = ?
                """,
                (user_id,)
            )
            stats_row = cur.fetchone()
            
            if stats_row:
                prev_sessions, prev_questions, prev_correct, prev_wrong, prev_avg, prev_best = stats_row
                new_sessions = prev_sessions + 1
                new_questions = prev_questions + total
                new_correct = prev_correct + correct_count
                new_wrong = prev_wrong + wrong_count
                new_avg = (new_correct / new_questions * 100) if new_questions > 0 else 0
                new_best = max(prev_best, percentage)
                
                best_session_id = session_id if percentage == new_best else None
                if prev_best > 0 and percentage < new_best:
                    # Keep previous best session
                    cur = conn.execute(
                        "SELECT best_session_id FROM math_user_stats WHERE user_id = ?",
                        (user_id,)
                    )
                    best_session_id = cur.fetchone()[0]
                
                conn.execute(
                    """
                    UPDATE math_user_stats 
                    SET total_sessions = ?, total_questions = ?, total_correct = ?, total_wrong = ?, 
                        average_percentage = ?, best_score = ?, best_session_id = ?, last_quiz_date = ?
                    WHERE user_id = ?
                    """,
                    (new_sessions, new_questions, new_correct, new_wrong, new_avg, new_best, 
                     best_session_id, now, user_id)
                )
            else:
                conn.execute(
                    """
                    INSERT INTO math_user_stats 
                    (user_id, tg_id, total_sessions, total_questions, total_correct, total_wrong, 
                     average_percentage, best_score, best_session_id, last_quiz_date, is_unlocked)
                    VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?, ?, 1)
                    """,
                    (user_id, tg_id, total, correct_count, wrong_count, percentage, percentage, 
                     session_id, now)
                )
            
            conn.commit()
            
            # Get updated stats
            cur = conn.execute(
                """
                SELECT total_sessions, total_questions, total_correct, total_wrong, average_percentage, best_score
                FROM math_user_stats WHERE user_id = ?
                """,
                (user_id,)
            )
            final_row = cur.fetchone()
            
            return {
                "session_id": session_id,
                "correct": correct_count,
                "wrong": wrong_count,
                "percentage": percentage,
                "total_sessions": final_row[0],
                "total_questions": final_row[1],
                "total_correct": final_row[2],
                "average_percentage": final_row[4],
                "best_score": final_row[5]
            }
        finally:
            conn.close()
    
    def get_user_stats(self, user_id: int) -> Optional[Dict]:
        """Get user's trigonometry statistics"""
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute(
                """
                SELECT user_id, total_sessions, total_questions, total_correct, total_wrong, 
                       average_percentage, best_score, last_quiz_date, is_unlocked
                FROM math_user_stats WHERE user_id = ?
                """,
                (user_id,)
            )
            row = cur.fetchone()
            if not row:
                return None
            
            return {
                "user_id": row[0],
                "total_sessions": row[1],
                "total_questions": row[2],
                "total_correct": row[3],
                "total_wrong": row[4],
                "average_percentage": row[5],
                "best_score": row[6],
                "last_quiz_date": row[7],
                "is_unlocked": row[8] == 1
            }
        finally:
            conn.close()
    
    def get_question_stats(self, user_id: int) -> List[Dict]:
        """Get statistics for each angle-function pair"""
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute(
                """
                SELECT angle, function, total_attempts, correct_attempts, accuracy, last_attempted
                FROM math_question_stats 
                WHERE user_id = ? 
                ORDER BY accuracy ASC, angle ASC
                """,
                (user_id,)
            )
            rows = cur.fetchall()
            
            return [
                {
                    "angle": row[0],
                    "function": row[1],
                    "total_attempts": row[2],
                    "correct_attempts": row[3],
                    "accuracy": row[4],
                    "last_attempted": row[5]
                }
                for row in rows
            ]
        finally:
            conn.close()
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top users by average percentage"""
        conn = sqlite3.connect(self.db_path)
        try:
            cur = conn.execute(
                """
                SELECT trig_stats.user_id, users.tg_id, users.username, 
                       trig_stats.average_percentage, trig_stats.total_sessions, 
                       trig_stats.best_score
                FROM math_user_stats as trig_stats
                JOIN users ON trig_stats.user_id = users.id
                WHERE trig_stats.is_unlocked = 1
                ORDER BY trig_stats.average_percentage DESC, trig_stats.total_sessions DESC
                LIMIT ?
                """,
                (limit,)
            )
            rows = cur.fetchall()
            
            return [
                {
                    "user_id": row[0],
                    "tg_id": row[1],
                    "username": row[2],
                    "average_percentage": row[3],
                    "total_sessions": row[4],
                    "best_score": row[5]
                }
                for row in rows
            ]
        finally:
            conn.close()


if __name__ == "__main__":
    # Test
    db = TrigonometryDatabase("/home/ubuntu/bot/bot.db")
    print("Database initialized successfully")
