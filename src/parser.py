import argparse

parser= argparse.ArgumentParser(description="A command-line tool for bug tracking.")
subparsers = parser.add_subparsers(dest="command", help="Available commands")



add_parser = subparsers.add_parser("add", help="Add a new bug")
list_parser = subparsers.add_parser("list", help="List all bugs")
delete_parser = subparsers.add_parser("delete", help="Delete a bug")


args = parser.parse_args()

if args.command == "add":
    print("Hello. I am a tester")