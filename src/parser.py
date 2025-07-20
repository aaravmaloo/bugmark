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

resolve_parser = subparsers.add_parser("resolve", help="Mark a bug as resolved")
resolve_parser.add_argument("--id", help="Resolve a specific bug by ID")
resolve_parser.add_argument("--tag", help="Resolve all bugs with a specific tag")
resolve_parser.add_argument("--file", help="Resolve all bugs in a specific file")



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
elif args.command == "resolve":
    if not os.path.exists("bugs.json"):
        print("No bugs to resolve.")
        exit()

    with open("bugs.json", "r") as f:
        bug_data = json.load(f)

    resolved_time = datetime.now().isoformat()
    found = False

    if args.id:
        if args.id in bug_data:
            bug_data[args.id]["status"] = "resolved"
            bug_data[args.id]["resolved"] = resolved_time
            found = True
        else:
            print("Bug ID not found.")

    elif args.tag:
        for bug in bug_data.values():
            if args.tag in bug["tags"]:
                bug["status"] = "resolved"
                bug["resolved"] = resolved_time
                found = True

    elif args.file:
        for bug in bug_data.values():
            if bug["file"] == args.file:
                bug["status"] = "resolved"
                bug["resolved"] = resolved_time
                found = True

    else:
        print("Provide --id or --tag or --file to resolve.")
        exit()

    if found:
        with open("bugs.json", "w") as f:
            json.dump(bug_data, f, indent=2)
        print("Resolved successfully.")
