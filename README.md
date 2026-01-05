# <center> Bugmark

A powerful, command-line bug tracking utility designed for speed and developer workflow integration.

## Features

- **Severity Levels**: Categorize bugs as `critical`, `major`, or `minor`.
- **Status Lifecycle**: Track bugs from `open` → `in-progress` → `resolved` → `closed`.
- **Bug Age Tracking**: Automatic warnings for [STALE] bugs (older than 30 days).
- **Owner & Deadlines**: Assign bugs to owners and set due dates.
- **Comments & History**: Full audit log of who changed what and when.
- **Advanced Search**:
  - Filter by tag, file, status, or severity.
  - Regex & fuzzy text search in descriptions.
  - Sort by date, severity, status, or file.
- **Saved Filters**: Create quick views for common queries.
- **Storage Options**: Use `JSON` for simplicity or `SQLite` for performance.
- **Git Integration**:
  - Link bugs to commits via Git hooks.
  - Reference bugs in commit messages.
  - Scan codebase for `TODO` and `FIXME` to auto-create bugs.
- **Analytics**:
  - ASCII charts for status and severity distribution.
  - CI/CD integration: fail builds if critical bugs exist.
- **Import/Export**: Support for `JSON`, `CSV`, and `Markdown`.

## Installation

```bash
pip install bugmark
```

## 🛠 Usage

### Adding a Bug
```bash
bugmark add "Fix the memory leak" --file main.py --line 42 --tag performance --severity critical --owner aarav
```

### Listing Bugs
```bash
# List all open bugs
bugmark list

# List critical bugs in a specific file
bugmark list --file main.py --severity critical

# Search for bugs using regex
bugmark list --search "memory.*leak"
```

### Managing Bugs
```bash
# Show details, comments, and history
bugmark show [id]

# Add a comment
bugmark comment [id] "I've identified the root cause in the allocator."

# Mark as resolved
bugmark resolve [id]
```

### Advanced Features
```bash
# Scan for TODOs and auto-add them
bugmark scan --add

# Show bug statistics
bugmark stats

# CI Check (fails if critical bugs exist)
bugmark ci-check --threshold critical
```

## Configuration

Create a `.bugmark.json` in your project root to customize storage:

```json
{
    "storage_type": "sqlite",
    "data_dir": "./.bugmark",
    "saved_filters": {
        "urgent": {"severity": "critical", "status": "open"}
    }
}
```

## 📄 License

MIT
