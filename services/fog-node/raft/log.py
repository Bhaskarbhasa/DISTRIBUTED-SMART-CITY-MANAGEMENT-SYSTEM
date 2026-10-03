import sqlite3
import json
import os
from typing import List, Dict, Any, Tuple
import structlog

logger = structlog.get_logger()

class RaftLog:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.db_path = os.path.join(self.data_dir, "raft_log.db")
        self._init_db()
        self.entries = self._load_entries()
        
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS log (
                id INTEGER PRIMARY KEY,
                term INTEGER NOT NULL,
                command TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def _load_entries(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT id, term, command FROM log ORDER BY id ASC')
        rows = c.fetchall()
        conn.close()
        # entries: list of dicts, index is 1-based (0 is dummy)
        entries = [{"term": 0, "command": None}] 
        for row in rows:
            entries.append({
                "term": row[1],
                "command": json.loads(row[2])
            })
        return entries

    def get_last_log_index(self) -> int:
        return len(self.entries) - 1

    def get_last_log_term(self) -> int:
        if len(self.entries) > 0:
            return self.entries[-1]["term"]
        return 0
        
    def get_term_at(self, index: int) -> int:
        if 0 <= index < len(self.entries):
            return self.entries[index]["term"]
        return 0

    def append_entry(self, term: int, command: dict) -> int:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        cmd_str = json.dumps(command)
        index = len(self.entries)
        c.execute('INSERT INTO log (id, term, command) VALUES (?, ?, ?)', (index, term, cmd_str))
        conn.commit()
        conn.close()
        
        self.entries.append({"term": term, "command": command})
        return index

    def append_entries(self, prev_log_index: int, prev_log_term: int, new_entries: List[Dict[str, Any]]) -> bool:
        # Check if log contains an entry at prev_log_index whose term matches prev_log_term
        if prev_log_index >= len(self.entries):
            return False
        if prev_log_index > 0 and self.entries[prev_log_index]["term"] != prev_log_term:
            return False
            
        # Truncate conflicting entries
        i = 0
        while i < len(new_entries):
            log_idx = prev_log_index + 1 + i
            if log_idx < len(self.entries):
                if self.entries[log_idx]["term"] != new_entries[i]["term"]:
                    # Conflict: truncate from log_idx
                    self._truncate(log_idx)
                    break
            else:
                break
            i += 1
            
        # Append new entries not already in log
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        while i < len(new_entries):
            entry = new_entries[i]
            log_idx = prev_log_index + 1 + i
            cmd_str = json.dumps(entry["command"])
            c.execute('INSERT INTO log (id, term, command) VALUES (?, ?, ?)', (log_idx, entry["term"], cmd_str))
            self.entries.append(entry)
            i += 1
        conn.commit()
        conn.close()
        
        return True

    def _truncate(self, from_index: int):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('DELETE FROM log WHERE id >= ?', (from_index,))
        conn.commit()
        conn.close()
        self.entries = self.entries[:from_index]
        
    def get_entries_after(self, index: int) -> List[Dict[str, Any]]:
        if index + 1 < len(self.entries):
            return self.entries[index + 1:]
        return []
        
    def get_entry(self, index: int) -> Dict[str, Any]:
        if 0 < index < len(self.entries):
            return self.entries[index]
        return None
