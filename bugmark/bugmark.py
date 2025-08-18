import argparse
import json
import uuid
import csv
from pathlib import Path
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description="A command-line tool for bug tracking.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    add_parser = subparsers.add_parser("add", help="Add a new bug")
    add_parser.add_argument("desc", help="Bug description")
    add_parser.add_argument("--file", required=True, help="File name")
    add_parser.add_argument("--line", required=True, type=int, help="Line number")
    add_parser.add_argument("--tag", required=True, action="append", help="Tags for the bug")

    export_parser = subparsers.add_parser("export", help="Export bugs of a file")
    export_parser.add_argument("--file", required=True, help="Name of the file")
    export_parser.add_argument("--format", choices=["json", "csv", "txt"], default="json", help="Export format")
    export_parser.add_argument("--out", help="Output file name")

    compare_parser = subparsers.add_parser("compare", help="Compare bugs across files")
    compare_parser.add_argument("--files", nargs="+", required=True, help="List of files to compare")

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

    try:
        BUG_FILE = Path.home() / ".bugmark" / "bugs.json"
        BUG_FILE.parent.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise PermissionError("permission denied")

    args = parser.parse_args()

    if BUG_FILE.exists():
        with BUG_FILE.open("r") as f:
            bugs = json.load(f)
    else:
        bugs = {}

    if args.command == "add":
        bug_id = str(uuid.uuid4().int)[:6]
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
        for bug_id, bug in bugs.items():
            if args.tag and args.tag not in bug["tags"]:
                continue
            if args.file and args.file != bug["file"]:
                continue
            if not args.resolved and bug["status"] == "resolved":
                continue
            filtered[bug_id] = bug
        if not filtered:
            print("No matching bugs found.")
        else:
            for bug_id, bug in filtered.items():
                print(f"[{bug_id}] {bug['desc']} ({bug['file']}:{bug['line']}) [{', '.join(bug['tags'])}] - {bug['status']}")

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

    elif args.command == "export":
        export_data = {bid: b for bid, b in bugs.items() if b["file"] == args.file}
        if not export_data:
            print("No bugs found for this file.")
            return
        out_file = args.out if args.out else f"{args.file}_bugs.{args.format}"
        if args.format == "json":
            with open(out_file, "w") as f:
                json.dump(export_data, f, indent=4)
        elif args.format == "csv":
            with open(out_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "File", "Line", "Description", "Tags", "Status", "Created", "Resolved"])
                for bid, b in export_data.items():
                    writer.writerow([bid, b["file"], b["line"], b["desc"], ";".join(b["tags"]), b["status"], b["created"], b["resolved"]])
        elif args.format == "txt":
            with open(out_file, "w") as f:
                for bid, b in export_data.items():
                    f.write(f"[{bid}] {b['desc']} ({b['file']}:{b['line']}) [{', '.join(b['tags'])}] - {b['status']}\n")
        print(f"Exported bugs to {out_file}")

    elif args.command == "compare":
        files = args.files
        grouped = {f: [] for f in files}
        for bug_id, bug in bugs.items():
            if bug["file"] in files:
                grouped[bug["file"]].append((bug_id, bug))
        common_desc = set.intersection(*(set(bug["desc"] for _, bug in grouped[f]) for f in files if grouped[f]))
        print("Common bugs across files:")
        for desc in common_desc:
            print(f"- {desc}")
        print("\nUnique bugs per file:")
        for f in files:
            unique = [bug["desc"] for _, bug in grouped[f] if bug["desc"] not in common_desc]
            print(f"{f}: {unique if unique else 'None'}")

if __name__ == "__main__":
    main()
