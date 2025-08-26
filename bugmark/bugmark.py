import argparse
import json
import uuid
import os
import sys
from datetime import datetime
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="A command-line tool for bug tracking.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    add_parser = subparsers.add_parser("add", help="Add a new bug")
    add_parser.add_argument("desc", help="Bug description")
    add_parser.add_argument("--file", required=True, help="File name")
    add_parser.add_argument("--line", required=True, type=int, help="Line number")
    add_parser.add_argument("--tag", required=True, action="append", help="Tags for the bug")

    export_parser = subparsers.add_parser("export", help="export all bugs of a file")
    export_parser.add_argument("--file", required=True, help="Name of the file")

    delete_parser = subparsers.add_parser("delete", help="Delete a bug by its ID")
    delete_parser.add_argument("bug_id", help="Bug ID to delete")

    list_parser = subparsers.add_parser("list", help="List all bugs")
    list_parser.add_argument("--tag", help="Filter bugs by tag")
    list_parser.add_argument("--file", help="Filter bugs by file")
    list_parser.add_argument("--resolved", action="store_true", help="Include resolved bugs in the output")

    resolve_parser = subparsers.add_parser("resolve", help="Mark a bug as resolved")
    resolve_parser.add_argument("--id", help="Resolve a specific bug by ID")
    resolve_parser.add_argument("--tag", help="Resolve all bugs with a specific tag")
    resolve_parser.add_argument("--file", help="Resolve all bugs in a specific file")

    BUG_DIR = Path.home() / "bugmark"
    BUG_FILE = BUG_DIR / "bugs.json"

    BUG_DIR.mkdir(parents=True, exist_ok=True)

    args = parser.parse_args()

    if BUG_FILE.exists():
        with BUG_FILE.open("r") as f:
            bugs = json.load(f)
    else:
        bugs = {}

    if args.command == "add":
        bug_id = str(uuid.uuid4().int)[:4]
        bugs[bug_id] = {
            "file": args.file,
            "line": args.line,
            "desc": args.desc,
            "tags": args.tag,
            "status": "open",
            "created": datetime.now().isoformat(),
            "resolved": None
        }
        with BUG_FILE.open("w") as f:
            json.dump(bugs, f, indent=4)
        print(f"Bug {bug_id} added.")

    elif args.command == "list":
        filtered = {}
        show_resolved = args.resolved

        for bug_id, bug in bugs.items():
            if args.tag and args.tag not in bug["tags"]:
                continue
            if args.file and args.file != bug["file"]:
                continue
            if not show_resolved and bug["status"] == "resolved":
                continue
            filtered[bug_id] = bug

        resolved_count = sum(1 for bug in bugs.values() if bug["status"] == "resolved")

        if not filtered:
            print("No matching bugs found.")
        else:
            for bug_id, bug in filtered.items():
                print(f"[{bug_id}] {bug['desc']} ({bug['file']}:{bug['line']}) [{', '.join(bug['tags'])}] - {bug['status']}")

        if not show_resolved and resolved_count > 0:
            print(f"({resolved_count} bugs resolved)")

    elif args.command == "resolve":
        resolved_time = datetime.now().isoformat()
        if args.id:
            if args.id in bugs:
                bugs[args.id]["status"] = "resolved"
                bugs[args.id]["resolved"] = resolved_time
                print(f"Bug {args.id} marked as resolved.")
        else:
            for bug_id, bug in bugs.items():
                if args.tag and args.tag not in bug["tags"]:
                    continue
                if args.file and args.file != bug["file"]:
                    continue
                bugs[bug_id]["status"] = "resolved"
                bugs[bug_id]["resolved"] = resolved_time
            print("Matching bugs marked as resolved.")
        with BUG_FILE.open("w") as f:
            json.dump(bugs, f, indent=4)

    elif args.command == "delete":
        if args.bug_id in bugs:
            del bugs[args.bug_id]
            with BUG_FILE.open("w") as f:
                json.dump(bugs, f, indent=4)
            print(f"Bug {args.bug_id} deleted.")
        else:
            print("Bug ID not found.")

if __name__ == "__main__":
    main()