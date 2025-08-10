# sovietcy/network_scanner.py
import threading
import datetime
import collections
import logging

from textual.widgets import Static, Header, Footer, DataTable, Button, Input
from textual.containers import Container, VerticalScroll, Horizontal
from textual.app import ComposeResult
from textual.message import Message

# Import Scapy for packet sniffing
from scapy.all import sniff, IP, TCP, UDP, Raw, Ether, ARP, L2_ETHER, Packet
from scapy.layers.inet6 import IPv6

# Import the utility function for data display
from sovietcy.utils.data_display import format_packet_for_display

# Suppress Scapy warnings (e.g., about IPv6 being loaded)
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
logging.getLogger("scapy.loading").setLevel(logging.ERROR)

class PacketCaptured(Message):
    """Custom message to send captured packet data from the sniffing thread to the UI thread."""
    def __init__(self, packet_data: dict) -> None:
        self.packet_data = packet_data
        super().__init__()

class NetworkScanner(Static):
    """
    A Textual widget for real-time network packet sniffing and display,
    emulating Wireshark's basic packet list view.
    """
    BINDINGS = [
        ("s", "start_scan_action", "Start Scan"),
        ("x", "stop_scan_action", "Stop Scan"),
        ("c", "clear_packets", "Clear"),
        ("b", "back_to_main", "Back"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sniff_thread: threading.Thread | None = None
        self.stop_sniff_event = threading.Event()
        self.packet_count = 0
        # Buffer to hold packets before displaying them, useful for performance
        # or if you want to implement scrolling history.
        self.packet_buffer = collections.deque(maxlen=1000)

    def compose(self) -> ComposeResult:
        """Create child widgets for the NetworkScanner view."""
        yield Static("### Network Scanner Module ###", classes="module-header")
        
        with Horizontal():
            yield Button("Start Scan (S)", id="scanner_start_btn", variant="success")
            yield Button("Stop Scan (X)", id="scanner_stop_btn", variant="error")
            yield Button("Clear (C)", id="scanner_clear_btn", variant="default")
            yield Button("Back (B)", id="scanner_back_btn", variant="primary")
            
        yield Static("\n[bold]BPF Filter (e.g., tcp port 80 or host 192.168.1.1 or not arp):[/bold]")
        yield Input(placeholder="BPF Filter (optional)", id="bpf_filter_input")
        
        yield Static("\n[bold]Captured Packets:[/bold]")
        # DataTable to display packet summary information
        yield DataTable(id="packet_table", classes="packet-table")

    def on_mount(self) -> None:
        """Actions performed when the widget is mounted."""
        table = self.query_one("#packet_table", DataTable)
        # Define columns for the packet display
        table.add_columns("ID", "Time", "Source", "Destination", "Protocol", "Length", "Info")
        self.start_scan_initial_message()

    def start_scan_initial_message(self):
        """Displays an initial message in the table when the scanner view is opened."""
        self.query_one("#packet_table", DataTable).clear()
        self.query_one("#packet_table", DataTable).add_row("[bold yellow]Press 'S' to Start Scanning.[/bold yellow]")
        self.query_one("#packet_table", DataTable).add_row("Use BPF filters for targeted capture.")

    def _packet_callback(self, packet: Packet):
        """
        Callback function for Scapy's sniff. Processes each captured packet.
        This runs in a separate thread.
        """
        self.packet_count += 1
        # Use the utility function to format the packet data for display
        packet_data = format_packet_for_display(packet, self.packet_count)
        
        # Post a message to the Textual application to update the UI
        self.post_message(PacketCaptured(packet_data))

    def _sniff_packets(self, bpf_filter: str = ""):
        """
        Starts the Scapy sniffing process in a separate thread.
        """
        try:
            # `prn` is the callback function for each packet
            # `store=0` means packets are not stored in memory by Scapy itself
            # `stop_filter` allows stopping the sniff loop gracefully
            # `filter` applies a BPF (Berkeley Packet Filter) to capture specific traffic
            sniff(prn=self._packet_callback, store=0,
                  stop_filter=lambda p: self.stop_sniff_event.is_set(),
                  filter=bpf_filter,
                  iface=None) # Set iface=None to sniff on all available interfaces, or specify one
        except Exception as e:
            # Post an error message back to the UI thread
            self.post_message(Static(f"[bold red]Error during sniffing:[/bold red] {e}"))
            self.stop_sniff_event.set() # Ensure stop event is set on error

    def action_start_scan_action(self) -> None:
        """Textual action to start the network scan."""
        if self.sniff_thread and self.sniff_thread.is_alive():
            self.query_one("#packet_table").add_row("[bold yellow]Scanner already running.[/bold yellow]")
            return

        self.query_one("#packet_table", DataTable).clear()
        self.packet_count = 0
        self.stop_sniff_event.clear() # Clear event to allow sniffing to start
        
        bpf_filter = self.query_one("#bpf_filter_input", Input).value.strip()
        
        self.query_one("#packet_table").add_row(f"Starting scan with filter: '[bold green]{bpf_filter if bpf_filter else 'none'}[/bold green]'...")
        self.query_one("#packet_table").add_row("[bold yellow]Press Ctrl+C or 'X' to stop.[/bold yellow]")

        # Start sniffing in a new thread to keep the UI responsive
        self.sniff_thread = threading.Thread(target=self._sniff_packets, args=(bpf_filter,))
        self.sniff_thread.daemon = True # Allow main program to exit even if thread is running
        self.sniff_thread.start()

    def action_stop_scan_action(self) -> None:
        """Textual action to stop the network scan."""
        if self.sniff_thread and self.sniff_thread.is_alive():
            self.query_one("#packet_table").add_row("Stopping scanner...")
            self.stop_sniff_event.set() # Signal the sniffing thread to stop
            self.sniff_thread.join(timeout=2) # Wait for the thread to finish (max 2 seconds)
            if self.sniff_thread.is_alive():
                self.query_one("#packet_table").add_row("[bold red]Warning: Sniffing thread might not have stopped gracefully. You may need to restart Sovietcy.[/bold red]")
            else:
                self.query_one("#packet_table").add_row("[bold green]Scanner stopped.[/bold green]")
        else:
            self.query_one("#packet_table").add_row("[bold yellow]Scanner is not running.[/bold yellow]")

    def on_packet_captured(self, message: PacketCaptured) -> None:
        """
        Handler for the PacketCaptured message. Updates the DataTable with new packet data.
        This method runs in the Textual main (UI) thread.
        """
        self.packet_buffer.append(message.packet_data) # Add to buffer
        table = self.query_one("#packet_table", DataTable)
        
        # Add the packet data as a new row in the DataTable
        table.add_row(
            message.packet_data["id"],
            message.packet_data["time"],
            message.packet_data["src"],
            message.packet_data["dst"],
            message.packet_data["protocol"],
            message.packet_data["length"],
            message.packet_data["info"]
        )
        # Automatically scroll to show the latest captured packet
        table.scroll_end(animate=False)

    def action_clear_packets(self) -> None:
        """Textual action to clear the displayed packets and reset count."""
        self.query_one("#packet_table", DataTable).clear()
        self.packet_buffer.clear()
        self.packet_count = 0
        self.query_one("#packet_table", DataTable).add_row("Packet log cleared.")
        self.query_one("#packet_table", DataTable).add_row("[bold yellow]Press 'S' to Start Scanning.[/bold yellow]")


    def action_back_to_main(self) -> None:
        """Textual action to return to the main menu."""
        self.action_stop_scan_action() # Ensure scanner is stopped before exiting
        self.add_class("hidden") # Hide this scanner view
        self.app.query_one("#main-menu").remove_class("hidden") # Show main menu
        self.app.query_one("#main_log").remove_class("hidden") # Show main log
        self.app.query_one("#main_log").write("Returned to main menu.")

