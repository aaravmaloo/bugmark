import argparse
import json
import uuid
import os
from datetime import datetime

parser = argparse.ArgumentParser(description="A command-line tool for bug tracking.")
subparsers = parser.add_subparsers(dest="command", help="Available commands")

add_parser = subparsers.add_parser("add", help="Add a new bug")
add_parser.add_argument("desc", help="Bug description")
add_parser.add_argument("--file", required=True, help="File name")
add_parser.add_argument("--line", required=True, type=int, help="Line number")
add_parser.add_argument("--tag", required=True, action="append", help="Tags for the bug")


list_parser = subparsers.add_parser("list", help="List all bugs")
list_parser.add_argument("--tags", help="Filter bugs by tag")
list_parser.add_argument("--file", help="Filter bugs by file")





delete_parser = subparsers.add_parser("delete", help="Delete a bug")

BUG_FILE = "bugs.json"
args = parser.parse_args()

if os.path.exists(BUG_FILE):
    with open(BUG_FILE, "r") as f:
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
    with open(BUG_FILE, "w") as f:
        json.dump(bugs, f, indent=4)
    print(f"Bug {bug_id} added.")


elif args.command == "list":
    with open("bugs.json", "r") as f:
        bugs = json.load(f)

    for bug_id, bug in bugs.items():
        if args.tags and args.tags not in bug["tags"]:
            continue
        if args.file and args.file != bug["file"]:
            continue

        print(f"[{bug_id}] {bug['desc']} (File: {bug['file']}:{bug['line']}, Tags: {', '.join(bug['tags'])}, Status: {bug['status']})")
