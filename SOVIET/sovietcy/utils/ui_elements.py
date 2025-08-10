# sovietcy/utils/ui_elements.py
from textual.widgets import Static, Button, Input
from textual.containers import Container, VerticalScroll, Horizontal
from textual.app import ComposeResult

class InfoPanel(Static):
    """A reusable panel for displaying informational messages."""
    def compose(self) -> ComposeResult:
        yield Static("[bold green]Info:[/bold green] This is a general information panel.")

class ActionButtons(Horizontal):
    """A reusable container for common action buttons."""
    def compose(self) -> ComposeResult:
        yield Button("Go Back", id="back_btn", variant="primary")
        yield Button("Clear Log", id="clear_log_btn", variant="default")

# You can add more complex, reusable Textual widgets here as needed.
# For example, custom tables, input forms, progress bars, etc.
