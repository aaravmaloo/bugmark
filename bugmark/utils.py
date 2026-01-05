import json
import csv
import re
import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from .models import Bug
from .constants import Status, Severity
from datetime import datetime, timedelta

def export_bugs(bugs: List[Bug], format: str, output_path: Path):
    if format == "json":
        data = [b.to_dict() for b in bugs]
        with open(output_path, "w") as f:
            json.dump(data, f, indent=4)
    elif format == "csv":
        if not bugs:
            return
        fields = ["bug_id", "desc", "file", "line", "tags", "severity", "status", "owner", "due_date", "created", "resolved"]
        with open(output_path, "w", newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for b in bugs:
                d = b.to_dict()
                d["tags"] = ",".join(d["tags"])
                d_filtered = {k: v for k, v in d.items() if k in fields}
                writer.writerow(d_filtered)
    elif format == "markdown":
        with open(output_path, "w") as f:
            f.write("# Bug Report\n\n")
            for b in bugs:
                f.write(f"## [{b.bug_id}] {b.desc}\n")
                f.write(f"- **Status**: {b.status}\n")
                f.write(f"- **Severity**: {b.severity}\n")
                f.write(f"- **File**: {b.file}:{b.line}\n")
                f.write(f"- **Tags**: {', '.join(b.tags)}\n\n")

def import_bugs(input_path: Path) -> List[Bug]:
    with open(input_path, "r") as f:
        data = json.load(f)
    if isinstance(data, list):
        return [Bug.from_dict(d) for d in data]
    return []

def create_backup(data_dir: Path):
    backup_dir = data_dir / "backups"
    backup_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for ext in ["json", "db"]:
        src = data_dir / f"bugs.{ext}"
        if src.exists():
            shutil.copy(src, backup_dir / f"bugs_{timestamp}.{ext}")
    all_backups = sorted(backup_dir.glob("bugs_*.*"), key=lambda p: p.stat().st_mtime)
    while len(all_backups) > 10:
        all_backups.pop(0).unlink()

def install_git_hook(project_root: Path):
    git_dir = project_root / ".git"
    if not git_dir.exists():
        return False, "Not a git repository."
    hooks_dir = git_dir / "hooks"
    hook_path = hooks_dir / "prepare-commit-msg"
    hook_content = """#!/bin/sh
# Bugmark hook to auto-link bugs to commits
COMMIT_MSG_FILE=$1
"""
    with open(hook_path, "w") as f:
        f.write(hook_content)
    if os.name != 'nt':
        os.chmod(hook_path, 0o755)
    return True, "Hook installed."

def scan_for_todos(project_root: Path) -> List[Dict[str, Any]]:
    todos = []
    patterns = [r"TODO[:\s]+(.*)", r"FIXME[:\s]+(.*)"]
    for root, dirs, files in os.walk(project_root):
        if ".git" in dirs:
            dirs.remove(".git")
        for file in files:
            if file.endswith((".py", ".js", ".go", ".c", ".cpp", ".java")):
                path = Path(root) / file
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        for i, line in enumerate(f, 1):
                            for pattern in patterns:
                                match = re.search(pattern, line)
                                if match:
                                    todos.append({
                                        "desc": match.group(1).strip(),
                                        "file": str(path.relative_to(project_root)),
                                        "line": i,
                                        "type": "FIXME" if "FIXME" in line else "TODO"
                                    })
                except Exception:
                    continue
    return todos

def get_bug_stats(bugs: List[Bug]):
    stats = {
        "total": len(bugs),
        "status": {s: 0 for s in Status},
        "severity": {s: 0 for s in Severity},
        "stale": 0,
        "trends": {} # By date
    }
    
    for bug in bugs:
        stats["status"][bug.status] += 1
        stats["severity"][bug.severity] += 1
        if bug.is_stale:
            stats["stale"] += 1
            
        created_date = bug.created.split("T")[0]
        stats["trends"][created_date] = stats["trends"].get(created_date, 0) + 1
        
    return stats

def generate_ascii_chart(data: Dict[str, int], title: str):
    if not data:
        return f"{title}: No data"
    
    max_val = max(data.values())
    chart = [f"{title}:"]
    width = 40
    
    for label, val in sorted(data.items()):
        bar_len = int((val / max_val) * width) if max_val > 0 else 0
        bar = "#" * bar_len
        chart.append(f"{label:12} | {bar} ({val})")
        
    return "\n".join(chart)
