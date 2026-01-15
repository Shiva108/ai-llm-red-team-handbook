#!/usr/bin/env python3
"""
44.1.2 Tooling: The `Shadow_AI_Scanner`

Source: Chapter_44_Emerging_Threats
Category: utils
"""

import socket
import threading
from typing import List

import argparse
import sys

class ShadowAIScanner:
    """
    Scans the internal network for unauthorized Local LLM servers.
    """
    def __init__(self, subnet: str):
        self.subnet = subnet
        self.targets = self._expand_subnet(subnet)
        self.signatures = {
            11434: "Ollama",
            8080: "Llama.cpp / LocalAI",
            7860: "Text-Generation-WebUI (Gradio)",
            3000: "Open WebUI"
        }

    def _expand_subnet(self, subnet):
        # Demo stub: returns a few IPs
        base = ".".join(subnet.split(".")[:3])
        return [f"{base}.{i}" for i in range(1, 20)]

    def scan_ip(self, ip: str):
        for port, service in self.signatures.items():
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(0.5)
                    result = sock.connect_ex((ip, port))
                if result == 0:
                    print(f"[!] SHADOW AI DETECTED: {ip}:{port} ({service})")
                    # Further recon: Grab the banner
                    sock.send(b"GET / HTTP/1.1\r\n\r\n")
                    banner = sock.recv(1024).decode('utf-8', errors='ignore')
                    if "Ollama" in banner or "gradio" in banner:
                        print(f"    [+] Banner Confirmed: {banner[:50]}...")
            except Exception:
                pass

    def run(self):
        print(f"[*] Scanning {len(self.targets)} hosts for Shadow AI services...")
        threads = []
        for ip in self.targets:
            t = threading.Thread(target=self.scan_ip, args=(ip,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

# Usage
# scanner = ShadowAIScanner("192.168.1.0/24")
# scanner.run()


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    # TODO: Add main execution logic
    pass

if __name__ == "__main__":
    main()