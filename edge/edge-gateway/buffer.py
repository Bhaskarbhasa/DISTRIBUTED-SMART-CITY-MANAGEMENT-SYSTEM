import sqlite3
import json
import structlog
from typing import List, Dict, Any
from config import settings

logger = structlog.get_logger()

class EventBuffer:
    def __init__(self):
        self.db_path = settings.DB_PATH
        self.init_db()
        
    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    retries INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS dead_letters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    error TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
    def add_event(self, topic: str, payload: dict):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO events (topic, payload) VALUES (?, ?)",
                    (topic, json.dumps(payload))
                )
            logger.info("event_buffered", topic=topic)
        except Exception as e:
            logger.error("buffer_add_failed", error=str(e))
            
    def get_pending_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM events ORDER BY created_at ASC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]
            
    def remove_event(self, event_id: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
            
    def increment_retry_or_dead_letter(self, event_id: int, topic: str, payload: str, error: str, max_retries: int = 5):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT retries FROM events WHERE id = ?", (event_id,))
            row = cursor.fetchone()
            if row:
                retries = row[0]
                if retries >= max_retries:
                    conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
                    conn.execute(
                        "INSERT INTO dead_letters (topic, payload, error) VALUES (?, ?, ?)",
                        (topic, payload, error)
                    )
                    logger.warning("event_dead_lettered", event_id=event_id, topic=topic)
                else:
                    conn.execute("UPDATE events SET retries = retries + 1 WHERE id = ?", (event_id,))
                    
    def count_buffered(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM events")
            return cursor.fetchone()[0]
