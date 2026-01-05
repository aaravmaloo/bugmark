from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid
from .constants import Severity, Status

class Comment:
    def __init__(self, author: str, text: str, timestamp: Optional[str] = None):
        self.author = author
        self.text = text
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, str]:
        return {
            "author": self.author,
            "text": self.text,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'Comment':
        return cls(data["author"], data["text"], data.get("timestamp"))

class HistoryItem:
    def __init__(self, user: str, field: str, old_value: Any, new_value: Any, timestamp: Optional[str] = None):
        self.user = user
        self.field = field
        self.old_value = old_value
        self.new_value = new_value
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user": self.user,
            "field": self.field,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoryItem':
        return cls(data["user"], data["field"], data["old_value"], data["new_value"], data.get("timestamp"))

class Bug:
    def __init__(self, 
                 desc: str, 
                 file: str, 
                 line: int, 
                 tags: List[str], 
                 severity: Severity = Severity.MAJOR,
                 status: Status = Status.OPEN,
                 owner: Optional[str] = None,
                 due_date: Optional[str] = None,
                 bug_id: Optional[str] = None,
                 created: Optional[str] = None,
                 resolved: Optional[str] = None,
                 comments: Optional[List[Comment]] = None,
                 history: Optional[List[HistoryItem]] = None):
        self.bug_id = bug_id or str(uuid.uuid4().int)[:4]
        self.desc = desc
        self.file = file
        self.line = line
        self.tags = tags
        self.severity = severity
        self.status = status
        self.owner = owner
        self.due_date = due_date
        self.created = created or datetime.now().isoformat()
        self.resolved = resolved
        self.comments = comments or []
        self.history = history or []

    @property
    def is_stale(self) -> bool:
        if self.status in [Status.RESOLVED, Status.CLOSED]:
            return False
        created_dt = datetime.fromisoformat(self.created)
        delta = datetime.now() - created_dt
        return delta.days > 30

    def add_comment(self, author: str, text: str):
        self.comments.append(Comment(author, text))

    def update_field(self, user: str, field: str, new_value: Any):
        old_value = getattr(self, field)
        if old_value != new_value:
            setattr(self, field, new_value)
            self.history.append(HistoryItem(user, field, old_value, new_value))
            if field == "status" and new_value == Status.RESOLVED:
                self.resolved = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bug_id": self.bug_id,
            "desc": self.desc,
            "file": self.file,
            "line": self.line,
            "tags": self.tags,
            "severity": self.severity,
            "status": self.status,
            "owner": self.owner,
            "due_date": self.due_date,
            "created": self.created,
            "resolved": self.resolved,
            "comments": [c.to_dict() for c in self.comments],
            "history": [h.to_dict() for h in self.history]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Bug':
        comments = [Comment.from_dict(c) for c in data.get("comments", [])]
        history = [HistoryItem.from_dict(h) for h in data.get("history", [])]
        return cls(
            desc=data["desc"],
            file=data["file"],
            line=data["line"],
            tags=data["tags"],
            severity=Severity(data.get("severity", Severity.MAJOR)),
            status=Status(data.get("status", Status.OPEN)),
            owner=data.get("owner"),
            due_date=data.get("due_date"),
            bug_id=data.get("bug_id"),
            created=data.get("created"),
            resolved=data.get("resolved"),
            comments=comments,
            history=history
        )
