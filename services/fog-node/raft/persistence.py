import json
import os
import sqlite3

class RaftPersistence:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.db_path = os.path.join(self.data_dir, "raft_state.db")
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS state (
                id INTEGER PRIMARY KEY,
                current_term INTEGER,
                voted_for TEXT
            )
        ''')
        c.execute('SELECT COUNT(*) FROM state')
        if c.fetchone()[0] == 0:
            c.execute('INSERT INTO state (id, current_term, voted_for) VALUES (1, 0, NULL)')
        conn.commit()
        conn.close()

    def save_state(self, current_term: int, voted_for: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('UPDATE state SET current_term = ?, voted_for = ? WHERE id = 1', 
                 (current_term, voted_for))
        conn.commit()
        conn.close()

    def load_state(self) -> tuple[int, str]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT current_term, voted_for FROM state WHERE id = 1')
        row = c.fetchone()
        conn.close()
        if row:
            return row[0], row[1]
        return 0, None
