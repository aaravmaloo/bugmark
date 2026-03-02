from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static, Label
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from .core import BugmarkCore
from rich.text import Text

class BugmarkApp(App):
    """A Textual app to manage bugs."""

    TITLE = "Bugmark GUI"
    CSS = """
    DataTable {
        height: 1fr;
        border: solid green;
    }

    #bug-details {
        width: 50;
        border: solid blue;
        padding: 1;
        background: $panel;
    }

    #details-title {
        text-align: center;
        text-style: bold;
        background: $accent;
        color: $text;
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh_bugs", "Refresh", show=True),
        Binding("x", "resolve_bug", "Resolve", show=True),
        Binding("d", "delete_bug", "Delete", show=True),
    ]

    def __init__(self, core: BugmarkCore = None):
        super().__init__()
        self.core = core or BugmarkCore()
        self.selected_bug_id = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield DataTable()
            with Vertical(id="bug-details"):
                yield Label("BUG DETAILS", id="details-title")
                yield Static("Select a bug to see details", id="details-content")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Severity", "Status", "Description", "File")
        table.cursor_type = "row"
        self.action_refresh_bugs()

    def action_refresh_bugs(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        bugs = self.core.list_bugs(sort_by="date")
        for bug in bugs:
            # Colorize status
            status_text = Text(bug.status.value)
            if bug.status.value == "open":
                status_text.stylize("red")
            elif bug.status.value == "resolved":
                status_text.stylize("green")
            elif bug.status.value == "in-progress":
                status_text.stylize("yellow")

            # Colorize severity
            severity_text = Text(bug.severity.value)
            if bug.severity.value == "critical":
                severity_text.stylize("bold red")

            table.add_row(
                bug.bug_id,
                severity_text,
                status_text,
                bug.desc,
                f"{bug.file}:{bug.line}",
                key=bug.bug_id
            )
        if self.selected_bug_id:
            self.update_details(self.selected_bug_id)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.selected_bug_id = event.row_key.value
        self.update_details(self.selected_bug_id)

    def update_details(self, bug_id: str) -> None:
        bug = self.core.storage.get_bug(bug_id)
        content = self.query_one("#details-content", Static)
        if bug:
            detail_text = (
                f"[b]ID:[/b] {bug.bug_id}\n"
                f"[b]Status:[/b] {bug.status.value}\n"
                f"[b]Severity:[/b] {bug.severity.value}\n"
                f"[b]File:[/b] {bug.file}:{bug.line}\n"
                f"[b]Owner:[/b] {bug.owner or 'Unassigned'}\n"
                f"[b]Created:[/b] {bug.created}\n\n"
                f"[b]Description:[/b]\n{bug.desc}\n\n"
                f"[b]Tags:[/b] {', '.join(bug.tags)}\n"
            )
            if bug.comments:
                detail_text += "\n[b]Comments:[/b]\n"
                for c in bug.comments:
                    detail_text += f"- [{c.timestamp}] {c.author}: {c.text}\n"
            content.update(detail_text)
        else:
            content.update("Bug not found")

    def action_resolve_bug(self) -> None:
        if self.selected_bug_id:
            if self.core.resolve_bug(self.selected_bug_id):
                self.notify(f"Bug {self.selected_bug_id} resolved")
                self.action_refresh_bugs()
            else:
                self.notify("Failed to resolve bug", severity="error")

    def action_delete_bug(self) -> None:
        if self.selected_bug_id:
            if self.core.delete_bug(self.selected_bug_id):
                self.notify(f"Bug {self.selected_bug_id} deleted")
                self.selected_bug_id = None
                self.query_one("#details-content", Static).update("Select a bug to see details")
                self.action_refresh_bugs()
            else:
                self.notify("Failed to delete bug", severity="error")

if __name__ == "__main__":
    app = BugmarkApp()
    app.run()
