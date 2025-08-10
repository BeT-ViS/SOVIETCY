# sovietcy/main.py
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, RichLog, Input, Static
from textual.containers import Container, VerticalScroll, Horizontal

from sovietcy.network_scanner import NetworkScanner
from sovietcy.phishing_tool import PhishingTool

class SovietcyApp(App):
    BINDINGS = [
        ("n", "show_scanner", "Network Scanner"),
        ("p", "show_phishing", "Phishing Tool"),
        ("q", "quit", "Quit"),
    ]

    CSS_PATH = "sovietcy_app.css" # We'll define this later for styling

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with Container():
            with Horizontal(id="main-menu"):
                yield Button("Network Scanner (N)", id="btn_scanner", variant="primary")
                yield Button("Phishing Tool (P)", id="btn_phishing", variant="warning")
            yield RichLog(id="main_log", auto_scroll=True)

            # Modals or dynamic content areas for tools
            yield NetworkScanner(id="scanner_view", classes="hidden")
            yield PhishingTool(id="phishing_view", classes="hidden")

    def on_mount(self) -> None:
        self.query_one("#main_log").write("Decoding CypherSpeak... Decryption complete.")
        self.query_one("#main_log").write("Welcome to Sovietcy: The Red Scythe of the Network.")

    def action_show_scanner(self) -> None:
        self.query_one("#main-menu").add_class("hidden")
        self.query_one("#main_log").add_class("hidden")
        self.query_one("#scanner_view").remove_class("hidden")
        self.query_one("#phishing_view").add_class("hidden")
        self.query_one("#scanner_view").start_scan_initial_message() # Custom method for scanner start

    def action_show_phishing(self) -> None:
        self.query_one("#main-menu").add_class("hidden")
        self.query_one("#main_log").add_class("hidden")
        self.query_one("#scanner_view").add_class("hidden")
        self.query_one("#phishing_view").remove_class("hidden")
        self.query_one("#phishing_view").display_initial_options() # Custom method for phishing start

    def action_quit(self) -> None:
        self.exit("Exiting Sovietcy.")

def run_sovietcy():
    app = SovietcyApp()
    app.run()

