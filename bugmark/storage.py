import json
import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from .models import Bug, Comment, HistoryItem
from .constants import Severity, Status

class BugStorage:
    def save_bug(self, bug: Bug):
        raise NotImplementedError

    def get_bug(self, bug_id: str) -> Optional[Bug]:
        raise NotImplementedError

    def list_bugs(self) -> List[Bug]:
        raise NotImplementedError

    def delete_bug(self, bug_id: str):
        raise NotImplementedError

class JSONStorage(BugStorage):
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self):
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, 'w') as f:
                json.dump({}, f)

    def _load_bugs(self) -> Dict[str, dict]:
        with open(self.file_path, 'r') as f:
            return json.load(f)

    def _save_bugs(self, bugs: Dict[str, dict]):
        with open(self.file_path, 'w') as f:
            json.dump(bugs, f, indent=4)

    def save_bug(self, bug: Bug):
        bugs = self._load_bugs()
        bugs[bug.bug_id] = bug.to_dict()
        self._save_bugs(bugs)

    def get_bug(self, bug_id: str) -> Optional[Bug]:
        bugs = self._load_bugs()
        data = bugs.get(bug_id)
        return Bug.from_dict(data) if data else None

    def list_bugs(self) -> List[Bug]:
        bugs = self._load_bugs()
        return [Bug.from_dict(data) for data in bugs.values()]

    def delete_bug(self, bug_id: str):
        bugs = self._load_bugs()
        if bug_id in bugs:
            del bugs[bug_id]
            self._save_bugs(bugs)

class SQLiteStorage(BugStorage):
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bugs (
                bug_id TEXT PRIMARY KEY,
                desc TEXT,
                file TEXT,
                line INTEGER,
                tags TEXT,
                severity TEXT,
                status TEXT,
                owner TEXT,
                due_date TEXT,
                created TEXT,
                resolved TEXT,
                comments TEXT,
                history TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def save_bug(self, bug: Bug):
        data = bug.to_dict()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO bugs 
            (bug_id, desc, file, line, tags, severity, status, owner, due_date, created, resolved, comments, history)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data["bug_id"],
            data["desc"],
            data["file"],
            data["line"],
            ",".join(data["tags"]),
            data["severity"],
            data["status"],
            data["owner"],
            data["due_date"],
            data["created"],
            data["resolved"],
            json.dumps(data["comments"]),
            json.dumps(data["history"])
        ))
        conn.commit()
        conn.close()

    def get_bug(self, bug_id: str) -> Optional[Bug]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bugs WHERE bug_id = ?', (bug_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return self._row_to_bug(row)
        return None

    def list_bugs(self) -> List[Bug]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM bugs')
        rows = cursor.fetchall()
        conn.close()
        return [self._row_to_bug(row) for row in rows]

    def delete_bug(self, bug_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM bugs WHERE bug_id = ?', (bug_id,))
        conn.commit()
        conn.close()

    def _row_to_bug(self, row) -> Bug:
        return Bug.from_dict({
            "bug_id": row[0],
            "desc": row[1],
            "file": row[2],
            "line": row[3],
            "tags": row[4].split(",") if row[4] else [],
            "severity": row[5],
            "status": row[6],
            "owner": row[7],
            "due_date": row[8],
            "created": row[9],
            "resolved": row[10],
            "comments": json.loads(row[11]),
            "history": json.loads(row[12])
        })
