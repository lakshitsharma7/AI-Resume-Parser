import ipaddress
import socket
import logging
from urllib.parse import urlparse
from typing import Tuple

logger = logging.getLogger(__name__)

# List of blocked IP networks (Private, Loopback, Link-Local, Cloud Metadata)
BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),          # Current network
    ipaddress.ip_network("10.0.0.0/8"),         # RFC 1918 Private
    ipaddress.ip_network("100.64.0.0/10"),      # Shared Address Space (Carrier-grade NAT)
    ipaddress.ip_network("127.0.0.0/8"),        # Loopback
    ipaddress.ip_network("169.254.0.0/16"),     # Link-Local (includes Cloud Metadata 169.254.169.254)
    ipaddress.ip_network("172.16.0.0/12"),      # RFC 1918 Private
    ipaddress.ip_network("192.0.0.0/24"),       # IETF Protocol Assignments
    ipaddress.ip_network("192.0.2.0/24"),       # TEST-NET-1
    ipaddress.ip_network("192.168.0.0/16"),     # RFC 1918 Private
    ipaddress.ip_network("198.18.0.0/15"),      # Network benchmark tests
    ipaddress.ip_network("198.51.100.0/24"),    # TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),     # TEST-NET-3
    ipaddress.ip_network("224.0.0.0/4"),        # Multicast
    ipaddress.ip_network("240.0.0.0/4"),        # Reserved
    ipaddress.ip_network("255.255.255.255/32"), # Broadcast
    # IPv6 Blocked
    ipaddress.ip_network("::1/128"),            # Loopback
    ipaddress.ip_network("fc00::/7"),           # Unique Local (Private)
    ipaddress.ip_network("fe80::/10"),          # Link-Local
]

BLOCKED_HOSTNAMES = {
    "localhost",
    "metadata.google.internal",
    "metadata",
    "instance-data",
    "169.254.169.254"
}

def validate_destination_url(url: str, allow_local: bool = False) -> Tuple[bool, str]:
    """
    Validates a destination URL to prevent Server-Side Request Forgery (SSRF).
    Blocks private IP addresses, loopback, link-local, and cloud metadata endpoints.
    
    Returns:
        (is_valid, error_message_or_empty)
    """
    if not url or not isinstance(url, str):
        return False, "Destination URL is required."

    url = url.strip()
    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"Invalid URL structure: {str(e)}"

    # 1. Scheme must be HTTP or HTTPS
    if parsed.scheme.lower() not in ["http", "https"]:
        return False, f"Invalid URL scheme '{parsed.scheme}'. Only 'http' and 'https' are permitted."

    hostname = parsed.hostname
    if not hostname:
        return False, "Destination URL missing hostname."

    # 2. Check explicitly blocked hostnames
    if not allow_local:
        if hostname.lower() in BLOCKED_HOSTNAMES or hostname.endswith(".local") or hostname.endswith(".internal"):
            return False, f"Access to internal/private destination '{hostname}' is forbidden (SSRF protection)."

    # 3. Resolve hostname to IP addresses and check against blocked subnets
    try:
        # Resolve all IPv4 and IPv6 addresses for the host
        addr_info = socket.getaddrinfo(hostname, parsed.port or (443 if parsed.scheme == "https" else 80))
    except socket.gaierror:
        return False, f"Cannot resolve destination hostname '{hostname}'. Domain does not exist or DNS failed."
    except Exception as e:
        return False, f"DNS resolution failed for '{hostname}': {str(e)}"

    if not addr_info:
        return False, f"No IP address found for hostname '{hostname}'."

    if not allow_local:
        for item in addr_info:
            sockaddr = item[4]
            ip_str = sockaddr[0]
            try:
                ip_obj = ipaddress.ip_address(ip_str)
                # Check standard Python flags
                if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast or ip_obj.is_reserved:
                    return False, f"Destination resolves to forbidden private or loopback IP ({ip_str}). SSRF protection triggered."

                # Check custom network ranges (including cloud metadata 169.254.169.254)
                for net in BLOCKED_NETWORKS:
                    if ip_obj in net:
                        return False, f"Destination IP {ip_str} falls within restricted network range {net}."
            except ValueError:
                return False, f"Invalid IP address format resolved: {ip_str}"

    return True, ""

