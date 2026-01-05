import argparse
import sys
import json
from .core import BugmarkCore
from .constants import Severity, Status

def main():
    parser = argparse.ArgumentParser(description="A command-line tool for bug tracking.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add Bug
    add_parser = subparsers.add_parser("add", help="Add a new bug")
    add_parser.add_argument("desc", help="Bug description")
    add_parser.add_argument("--file", required=True, help="File name")
    add_parser.add_argument("--line", required=True, type=int, help="Line number")
    add_parser.add_argument("--tag", required=True, action="append", help="Tags for the bug")
    add_parser.add_argument("--severity", choices=[s.value for s in Severity], default=Severity.MAJOR.value, help="Bug severity")
    add_parser.add_argument("--owner", help="Bug owner/assignee")
    add_parser.add_argument("--due", help="Due date (YYYY-MM-DD)")

    # List Bugs
    list_parser = subparsers.add_parser("list", help="List all bugs")
    list_parser.add_argument("--tag", help="Filter bugs by tag")
    list_parser.add_argument("--file", help="Filter bugs by file")
    list_parser.add_argument("--status", choices=[s.value for s in Status], help="Filter by status")
    list_parser.add_argument("--severity", choices=[s.value for s in Severity], help="Filter by severity")
    list_parser.add_argument("--all", action="store_true", help="Include all statuses (default filters out closed)")
    list_parser.add_argument("--search", help="Fuzzy search in description")
    list_parser.add_argument("--sort", choices=["date", "severity", "status", "file"], default="date", help="Sort bugs")
    list_parser.add_argument("--filter", help="Use a saved filter")

    # Save Filter
    sf_parser = subparsers.add_parser("save-filter", help="Save current list filters")
    sf_parser.add_argument("name", help="Filter name")
    sf_parser.add_argument("--tag", help="Tag to save")
    sf_parser.add_argument("--file", help="File to save")
    sf_parser.add_argument("--status", help="Status to save")
    sf_parser.add_argument("--severity", help="Severity to save")

    # Resolve Bug
    resolve_parser = subparsers.add_parser("resolve", help="Mark a bug as resolved")
    resolve_parser.add_argument("id", help="Bug ID to resolve")

    # Delete Bug
    delete_parser = subparsers.add_parser("delete", help="Delete a bug by its ID")
    delete_parser.add_argument("bug_id", help="Bug ID to delete")

    # Add Comment
    comment_parser = subparsers.add_parser("comment", help="Add a comment to a bug")
    comment_parser.add_argument("id", help="Bug ID")
    comment_parser.add_argument("text", help="Comment text")
    comment_parser.add_argument("--author", default="user", help="Comment author")

    # Show Bug
    show_parser = subparsers.add_parser("show", help="Show details of a bug")
    show_parser.add_argument("id", help="Bug ID")

    # Export
    export_parser = subparsers.add_parser("export", help="Export bugs to a file")
    export_parser.add_argument("output", help="Output file path")
    export_parser.add_argument("--format", choices=["json", "csv", "markdown"], default="json", help="Export format")

    # Import
    import_parser = subparsers.add_parser("import", help="Import bugs from a file")
    import_parser.add_argument("input", help="Input file path (JSON only)")

    # Git Hooks
    subparsers.add_parser("install-hooks", help="Install Git hooks for bug linking")

    # Scan TODOs
    scan_parser = subparsers.add_parser("scan", help="Scan project for TODO/FIXME comments")
    scan_parser.add_argument("--add", action="store_true", help="Auto-add found TODOs as bugs")

    # Stats
    subparsers.add_parser("stats", help="Show bug statistics and ASCII charts")

    # CI Check
    ci_parser = subparsers.add_parser("ci-check", help="Fail if critical bugs are found")
    ci_parser.add_argument("--threshold", choices=[s.value for s in Severity], default=Severity.CRITICAL.value, help="Severity threshold")

    # Sync
    subparsers.add_parser("sync", help="Sync bugs with Git (pull)")

    args = parser.parse_args()
    core = BugmarkCore()

    if args.command == "add":
        bug_id = core.add_bug(
            desc=args.desc,
            file=args.file,
            line=args.line,
            tags=args.tag,
            severity=args.severity,
            owner=args.owner,
            due_date=args.due
        )
        print(f"Bug {bug_id} added.")

    elif args.command == "list":
        filters = {}
        if args.filter:
            saved = core.get_filter(args.filter)
            if saved:
                filters = saved
            else:
                print(f"Filter '{args.filter}' not found.")
        
        tag = args.tag or filters.get("tag")
        file = args.file or filters.get("file")
        status = args.status or filters.get("status")
        severity = args.severity or filters.get("severity")

        bugs = core.list_bugs(
            tag=tag, 
            file=file, 
            status=status, 
            severity=severity,
            search=args.search,
            sort_by=args.sort
        )
        
        if not bugs:
            print("No matching bugs found.")
        else:
            for bug in bugs:
                if not args.all and bug.status in [Status.CLOSED, Status.RESOLVED] and not status:
                    continue
                stale_tag = " [STALE]" if bug.is_stale else ""
                print(f"[{bug.bug_id}] {bug.desc} ({bug.file}:{bug.line}) [{', '.join(bug.tags)}] - {bug.status} ({bug.severity}){stale_tag}")

    elif args.command == "save-filter":
        filters = {
            "tag": args.tag,
            "file": args.file,
            "status": args.status,
            "severity": args.severity
        }
        filters = {k: v for k, v in filters.items() if v is not None}
        core.save_filter(args.name, filters)
        print(f"Filter '{args.name}' saved.")

    elif args.command == "resolve":
        if core.resolve_bug(args.id):
            print(f"Bug {args.id} marked as resolved.")
        else:
            print("Bug ID not found.")

    elif args.command == "delete":
        if core.delete_bug(args.bug_id):
            print(f"Bug {args.bug_id} deleted.")
        else:
            print("Bug ID not found.")

    elif args.command == "comment":
        if core.add_comment(args.id, args.author, args.text):
            print(f"Comment added to bug {args.id}.")
        else:
            print("Bug ID not found.")

    elif args.command == "show":
        bug = core.storage.get_bug(args.id)
        if not bug:
            print("Bug ID not found.")
        else:
            print(f"Bug ID:    {bug.bug_id}")
            print(f"Status:    {bug.status}")
            print(f"Severity:  {bug.severity}")
            print(f"File:      {bug.file}:{bug.line}")
            print(f"Owner:     {bug.owner or 'Unassigned'}")
            print(f"Due Date:  {bug.due_date or 'None'}")
            print(f"Created:   {bug.created}")
            print(f"Desc:      {bug.desc}")
            print(f"Tags:      {', '.join(bug.tags)}")
            
            if bug.comments:
                print("\nComments:")
                for c in bug.comments:
                    print(f"  - [{c.timestamp}] {c.author}: {c.text}")
            
            if bug.history:
                print("\nHistory:")
                for h in bug.history:
                    print(f"  - [{h.timestamp}] {h.user} changed {h.field}: {h.old_value} -> {h.new_value}")

    elif args.command == "export":
        core.export_all(args.format, args.output)
        print(f"Bugs exported to {args.output} ({args.format})")

    elif args.command == "import":
        count = core.import_from_file(args.input)
        print(f"Imported {count} bugs from {args.input}")

    elif args.command == "install-hooks":
        success, msg = core.install_hooks()
        print(msg)

    elif args.command == "scan":
        todos = core.scan_todos(auto_add=args.add)
        if not todos:
            print("No TODOs or FIXMEs found.")
        else:
            for todo in todos:
                prefix = "[ADDED] " if args.add else ""
                print(f"{prefix}{todo['type']}: {todo['desc']} ({todo['file']}:{todo['line']})")

    elif args.command == "stats":
        print(core.get_ascii_report())

    elif args.command == "ci-check":
        bugs = core.list_bugs(severity=args.threshold, status=Status.OPEN)
        if bugs:
            print(f"CI Check FAILED: Found {len(bugs)} {args.threshold} bugs.")
            sys.exit(1)
        else:
            print("CI Check PASSED.")

    elif args.command == "sync":
        success, msg = core.git_sync()
        print(msg)

    elif not args.command:
        parser.print_help()

if __name__ == "__main__":
    main()
