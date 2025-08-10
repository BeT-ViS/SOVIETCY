# sovietcy/utils/data_display.py
import datetime
from scapy.all import IP, TCP, UDP, Raw, Ether, ARP

def format_packet_for_display(packet, packet_id: int):
    """
    Formats a Scapy packet into a dictionary suitable for DataTable display.
    This is a more robust version than the one directly in network_scanner.py
    for better reusability and clarity.
    """
    timestamp = datetime.datetime.fromtimestamp(packet.time).strftime('%H:%M:%S.%f')[:-3]
    src_addr = "N/A"
    dst_addr = "N/A"
    protocol = "N/A"
    length = len(packet)
    info = ""

    if IP in packet:
        src_addr = packet[IP].src
        dst_addr = packet[IP].dst
        protocol = packet[IP].proto
        if protocol == 6: # TCP
            protocol = "TCP"
            if TCP in packet:
                info = f"SrcPort:{packet[TCP].sport} DstPort:{packet[TCP].dport} Flags:{packet[TCP].flags}"
        elif protocol == 17: # UDP
            protocol = "UDP"
            if UDP in packet:
                info = f"SrcPort:{packet[UDP].sport} DstPort:{packet[UDP].dport}"
        elif protocol == 1: # ICMP
            protocol = "ICMP"
            info = f"Type:{packet[IP].type} Code:{packet[IP].code}"
        else:
            protocol = f"IP:{protocol}" # Display numeric protocol if unknown
            info = f"IP ID:{packet[IP].id}"
    elif ARP in packet:
        src_addr = packet[ARP].psrc
        dst_addr = packet[ARP].pdst
        protocol = "ARP"
        info = f"Who has {packet[ARP].pdst}? Tell {packet[ARP].psrc}"
    elif Ether in packet:
        src_addr = packet[Ether].src
        dst_addr = packet[Ether].dst
        protocol = "Ethernet"
        info = f"Type: {hex(packet[Ether].type)}"

    # Attempt to get payload info
    if Raw in packet:
        try:
            raw_load = packet[Raw].load
            if isinstance(raw_load, bytes):
                info += f" | Raw: {raw_load[:40].hex()}..." # Display up to 40 bytes of hex payload
            else:
                info += f" | Raw: {str(raw_load)[:40]}..."
        except Exception:
            pass

    # Fallback for packets without IP/ARP/Ether (e.g., higher layer protocols captured directly)
    if src_addr == "N/A" and dst_addr == "N/A":
        # Attempt to derive from higher layers if present
        if TCP in packet:
            src_addr = f"TCP:{packet[TCP].sport}"
            dst_addr = f"TCP:{packet[TCP].dport}"
        elif UDP in packet:
            src_addr = f"UDP:{packet[UDP].sport}"
            dst_addr = f"UDP:{packet[UDP].dport}"

    return {
        "id": packet_id,
        "time": timestamp,
        "src": src_addr,
        "dst": dst_addr,
        "protocol": protocol,
        "length": length,
        "info": info
    }

