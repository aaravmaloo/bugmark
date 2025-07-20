#  BugMark

**BugMark** is a blazing-fast, no-nonsense CLI bug tracker for developers. It lets you mark, tag, list, resolve, and delete bugs *directly from your terminal* — like `git`, but for bugs. 

No web dashboards, no bloated GUIs. Just `bugmark`.

---

##  Features

-  Add bugs by file and line number
-  Support for multiple tags per bug
-  Resolve bugs by ID, tag, or file
-  Delete bugs by ID, tag, or file
-  Filter by resolved/unresolved
-  Stores all data in a JSON file at `C:\Program Files\bugmark\bugs.json`
-  UUID-based unique bug IDs

---

##  Installation

### From source:

```bash
git clone https://github.com/yourname/bugmark
cd bugmark
pip install .
