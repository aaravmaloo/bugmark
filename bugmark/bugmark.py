import argparse
import json
import uuid
import os
from datetime import datetime
import sys 
import os 

def main():
    parser = argparse.ArgumentParser(description="A command-line tool for bug tracking.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    add_parser = subparsers.add_parser("add", help="Add a new bug")
    add_parser.add_argument("desc", help="Bug description")
    add_parser.add_argument("--file", required=True, help="File name")
    add_parser.add_argument("--line", required=True, type=int, help="Line number")
    add_parser.add_argument("--tag", required=True, action="append", help="Tags for the bug")


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



    delete_parser = subparsers.add_parser("delete", help="Delete a bug")

    BUG_DIR = r"C:\Program Files\bugmark"
    BUG_FILE = os.path.join(BUG_DIR, "bugs.json")

    if not os.path.exists(BUG_DIR):
        try:
            os.makedirs(BUG_DIR)
        except PermissionError:
            print("Permission denied: Run this script as administrator to create files in Program Files.")
            sys.exit(1)
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
        if not os.path.exists(BUG_FILE):
            print("No bugs recorded yet.")
            sys.exit()

        with open(BUG_FILE, "r") as f:
            bugs = json.load(f)

        show_resolved = args.resolved
        filtered = {}

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
    elif args.command == "delete":
        if not os.path.exists("bugs.json"):
            print("No bugs found.")
            sys.exit(0)

        with open("bugs.json", "r") as f:
            bugs = json.load(f)

        if args.bug_id not in bugs:
            print(f"No bug with ID {args.bug_id} found.")
            sys.exit(0)

        del bugs[args.bug_id]

        with open("bugs.json", "w") as f:
            json.dump(bugs, f, indent=4)

        print(f"Bug {args.bug_id} deleted successfully.")



if __name__ == "__main__":
    main()