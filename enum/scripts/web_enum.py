#!/usr/bin/env python3
"""
Web Enumeration — Directory busting and web service fingerprinting

Wraps gobuster, nikto, and whatweb for quick web target analysis.
Handles HTTP/HTTPS targets with optional authentication.

Usage:
    python3 web_enum.py <url> [--wordlist <path>] [--extensions php,html] [--auth "user:pass"]

Output: Discovered directories, files, and technology fingerprint.
"""

import subprocess
import argparse
import sys
import os
from datetime import datetime


def check_tool(tool):
    """Check if a tool is installed."""
    result = subprocess.run(["which", tool], capture_output=True, timeout=5)
    return result.returncode == 0


def run_gobuster(url, wordlist, extensions, output_dir, auth_header):
    """Run gobuster directory scan."""
    if not check_tool("gobuster"):
        print("[!] gobuster not found. Install: sudo apt install gobuster", file=sys.stderr)
        return

    cmd = ["gobuster", "dir", "-u", url, "-w", wordlist, "-o", f"{output_dir}/gobuster.txt", "-q"]
    if extensions:
        cmd.extend(["-x", extensions])
    if auth_header:
        cmd.extend(["-H", f"Authorization: {auth_header}"])

    print(f"[*] Running gobuster on {url}")
    try:
        subprocess.run(cmd, timeout=300)
    except subprocess.TimeoutExpired:
        print("[!] gobuster timed out")
    except FileNotFoundError:
        print("[!] gobuster execution failed")


def run_nikto(url, output_dir):
    """Run nikto web vulnerability scan."""
    if not check_tool("nikto"):
        print("[!] nikto not found. Install: sudo apt install nikto", file=sys.stderr)
        return

    print(f"[*] Running nikto on {url}")
    try:
        result = subprocess.run(
            ["nikto", "-h", url, "-o", f"{output_dir}/nikto.txt", "-Format", "txt"],
            capture_output=True, text=True, timeout=300
        )
        if result.stdout:
            print(result.stdout[:2000])
    except subprocess.TimeoutExpired:
        print("[!] nikto timed out")
    except FileNotFoundError:
        print("[!] nikto execution failed")


def run_whatweb(url):
    """Fingerprint web technology."""
    if not check_tool("whatweb"):
        print("[!] whatweb not found. Install: sudo apt install whatweb", file=sys.stderr)
        return

    print(f"[*] Fingerprinting {url} with whatweb")
    try:
        result = subprocess.run(
            ["whatweb", url],
            capture_output=True, text=True, timeout=60
        )
        if result.stdout:
            print(f"    {result.stdout.strip()}")
    except subprocess.TimeoutExpired:
        print("[!] whatweb timed out")


def check_robots(url, output_dir):
    """Check robots.txt for hidden paths."""
    print(f"[*] Checking robots.txt")
    try:
        result = subprocess.run(
            ["curl", "-s", f"{url}/robots.txt"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().splitlines()
            interesting = [l for l in lines if l.startswith(("Disallow:", "Allow:"))]
            if interesting:
                print(f"    Found {len(interesting)} entries in robots.txt")
                for line in interesting[:20]:
                    print(f"    {line.strip()}")
                with open(f"{output_dir}/robots.txt", "w") as f:
                    f.write(result.stdout)
    except (subprocess.TimeoutExpired, Exception):
        pass


def check_security_headers(url):
    """Check for security headers."""
    print(f"[*] Checking security headers")
    try:
        result = subprocess.run(
            ["curl", "-sI", url],
            capture_output=True, text=True, timeout=10
        )
        headers_lower = result.stdout.lower()
        expected = {
            "x-frame-options": "Clickjacking protection",
            "x-content-type-options": "MIME type sniffing protection",
            "strict-transport-security": "HTTPS enforcement",
            "content-security-policy": "XSS/injection protection",
            "x-xss-protection": "Legacy XSS filter",
        }
        missing = []
        for header, desc in expected.items():
            if header in headers_lower:
                print(f"    ✓ {header}: present")
            else:
                missing.append(header)
                print(f"    ✗ {header}: MISSING ({desc})")

        if missing:
            print(f"\n    [!] {len(missing)} security headers missing")
    except (subprocess.TimeoutExpired, Exception):
        pass


def main():
    parser = argparse.ArgumentParser(description="Web service enumeration")
    parser.add_argument("url", help="Target URL (e.g., http://192.168.1.105:8080)")
    parser.add_argument("--wordlist", default="/usr/share/wordlists/dirb/common.txt",
                        help="Wordlist for directory busting")
    parser.add_argument("--extensions", default="", help="File extensions (e.g., php,html,txt)")
    parser.add_argument("--auth", default="", help="Auth header value (e.g., 'Bearer token123')")
    parser.add_argument("--output-dir", default="loot", help="Output directory")
    parser.add_argument("--skip-nikto", action="store_true", help="Skip nikto scan")
    parser.add_argument("--skip-bust", action="store_true", help="Skip directory busting")
    args = parser.parse_args()

    url = args.url.rstrip("/")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = f"{args.output_dir}/web-enum-{timestamp}"
    os.makedirs(output_dir, exist_ok=True)

    print(f"[*] Web Enumeration: {url}")
    print(f"[*] Output: {output_dir}/\n")

    # Technology fingerprint
    run_whatweb(url)

    # Security headers
    check_security_headers(url)

    # robots.txt
    check_robots(url, output_dir)

    # Directory busting
    if not args.skip_bust:
        if os.path.exists(args.wordlist):
            run_gobuster(url, args.wordlist, args.extensions, output_dir, args.auth)
        else:
            print(f"[!] Wordlist not found: {args.wordlist}")

    # Nikto (can be slow, skip with --skip-nikto)
    if not args.skip_nikto:
        run_nikto(url, output_dir)

    print(f"\n[✓] Web enumeration complete. Results in: {output_dir}/")


if __name__ == "__main__":
    main()
