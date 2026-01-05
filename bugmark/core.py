from pathlib import Path
from typing import Optional, List, Any, Dict
import json
import os
import re
import subprocess
from .storage import JSONStorage, SQLiteStorage, BugStorage
from .constants import Status, Severity
from .utils import (
    export_bugs, import_bugs, create_backup, install_git_hook, 
    scan_for_todos, get_bug_stats, generate_ascii_chart
)

class BugmarkCore:
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.config = self._load_config()
        self.storage = self._init_storage()
        self._auto_backup()

    def _load_config(self):
        config_path = self.project_root / ".bugmark.json"
        default_config = {
            "storage_type": "json",
            "data_dir": str(Path.home() / "bugmark"),
            "db_name": "bugs.json",
            "saved_filters": {}
        }
        if config_path.exists():
            with open(config_path, "r") as f:
                return {**default_config, **json.load(f)}
        return default_config

    def _save_config(self):
        config_path = self.project_root / ".bugmark.json"
        with open(config_path, "w") as f:
            json.dump(self.config, f, indent=4)

    def _init_storage(self) -> BugStorage:
        data_dir = Path(self.config["data_dir"])
        storage_type = self.config["storage_type"]
        
        if storage_type == "sqlite":
            db_path = data_dir / "bugs.db"
            return SQLiteStorage(db_path)
        else:
            db_path = data_dir / "bugs.json"
            return JSONStorage(db_path)

    def _auto_backup(self):
        data_dir = Path(self.config["data_dir"])
        create_backup(data_dir)

    def add_bug(self, desc: str, file: str, line: int, tags: List[str], severity: str = "major", owner: str = None, due_date: str = None):
        from .models import Bug
        bug = Bug(desc=desc, file=file, line=line, tags=tags, severity=Severity(severity), owner=owner, due_date=due_date)
        self.storage.save_bug(bug)
        return bug.bug_id

    def list_bugs(self, tag=None, file=None, status=None, severity=None, search=None, sort_by="date"):
        bugs = self.storage.list_bugs()
        filtered = []
        for bug in bugs:
            if tag and tag not in bug.tags:
                continue
            if file and file != bug.file:
                continue
            if status and status != bug.status:
                continue
            if severity and severity != bug.severity:
                continue
            if search:
                try:
                    if not re.search(search, bug.desc, re.IGNORECASE):
                        continue
                except re.error:
                    if search.lower() not in bug.desc.lower():
                        continue
            filtered.append(bug)

        # Sorting
        if sort_by == "severity":
            severity_order = {Severity.CRITICAL: 0, Severity.MAJOR: 1, Severity.MINOR: 2}
            filtered.sort(key=lambda b: severity_order.get(b.severity, 3))
        elif sort_by == "status":
            status_order = {Status.OPEN: 0, Status.IN_PROGRESS: 1, Status.RESOLVED: 2, Status.CLOSED: 3}
            filtered.sort(key=lambda b: status_order.get(b.status, 4))
        elif sort_by == "file":
            filtered.sort(key=lambda b: (b.file, b.line))
        else: # date
            filtered.sort(key=lambda b: b.created, reverse=True)

        return filtered

    def resolve_bug(self, bug_id: str, user: str = "system"):
        bug = self.storage.get_bug(bug_id)
        if bug:
            bug.update_field(user, "status", Status.RESOLVED)
            self.storage.save_bug(bug)
            return True
        return False

    def delete_bug(self, bug_id: str):
        self.storage.delete_bug(bug_id)
        return True

    def add_comment(self, bug_id: str, author: str, text: str):
        bug = self.storage.get_bug(bug_id)
        if bug:
            bug.add_comment(author, text)
            self.storage.save_bug(bug)
            return True
        return False

    def save_filter(self, name: str, filters: Dict[str, Any]):
        self.config["saved_filters"][name] = filters
        self._save_config()

    def get_filter(self, name: str) -> Optional[Dict[str, Any]]:
        return self.config["saved_filters"].get(name)

    def export_all(self, format: str, output_path: str):
        bugs = self.storage.list_bugs()
        export_bugs(bugs, format, Path(output_path))

    def import_from_file(self, input_path: str):
        bugs = import_bugs(Path(input_path))
        for bug in bugs:
            self.storage.save_bug(bug)
        return len(bugs)

    def install_hooks(self):
        return install_git_hook(self.project_root)

    def scan_todos(self, auto_add=False):
        todos = scan_for_todos(self.project_root)
        if auto_add:
            for todo in todos:
                self.add_bug(
                    desc=f"[{todo['type']}] {todo['desc']}",
                    file=todo["file"],
                    line=todo["line"],
                    tags=[todo["type"].lower(), "auto-created"],
                    severity="minor"
                )
        return todos

    def get_stats(self):
        bugs = self.storage.list_bugs()
        return get_bug_stats(bugs)

    def get_ascii_report(self):
        stats = self.get_stats()
        reports = []
        reports.append(generate_ascii_chart(stats["status"], "Status Distribution"))
        reports.append(generate_ascii_chart(stats["severity"], "Severity Distribution"))
        return "\n\n".join(reports)

    def git_sync(self):
        # Basic git sync: pull then push the data file if it's in the repo
        data_dir = Path(self.config["data_dir"])
        if not (self.project_root / ".git").exists():
            return False, "Not a git repository."
        
        try:
            subprocess.run(["git", "pull"], cwd=self.project_root, check=True)
            # We don't auto-commit/push here as it might be intrusive, 
            # but we can provide the command or a flag.
            return True, "Git pull successful."
        except Exception as e:
            return False, f"Git sync failed: {e}"
