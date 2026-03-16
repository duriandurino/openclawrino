#!/usr/bin/env python3
"""
Shodan Query Tool

Search Shodan for information about a target IP or hostname.
Requires SHODAN_API_KEY environment variable.

Usage:
    SHODAN_API_KEY=xxx python3 shodan_query.py <ip|hostname>

Output: Open ports, services, banners, and host details.
"""

import os
import sys
import json
import subprocess
import argparse


def query_shodan_curl(target, api_key):
    """Query Shodan API via curl (no pip dependency required)."""
    # Host lookup
    result = subprocess.run(
        ["curl", "-s", f"https://api.shodan.io/shodan/host/{target}?key={api_key}"],
        capture_output=True, text=True, timeout=30
    )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print(f"[ERROR] Failed to parse Shodan response", file=sys.stderr)
        print(result.stdout, file=sys.stderr)
        return None


def display_results(data, target):
    """Display Shodan host data in readable format."""
    if not data or "error" in data:
        error_msg = data.get("error", "No data returned") if data else "No response"
        print(f"[-] {error_msg}")
        return

    print(f"[*] Shodan Results for: {target}")
    print(f"[*] Last Updated: {data.get('last_update', 'unknown')}")
    print(f"[*] Ports: {', '.join(str(p) for p in data.get('ports', []))}")
    print()

    # Organization and location
    if data.get("org"):
        print(f"  Org: {data['org']}")
    if data.get("isp"):
        print(f"  ISP: {data['isp']}")
    if data.get("country_name"):
        location = data["country_name"]
        if data.get("city"):
            location += f", {data['city']}"
        if data.get("asn"):
            location += f" (ASN: {data['asn']})"
        print(f"  Location: {location}")
    print()

    # Services
    for service in data.get("data", []):
        port = service.get("port", "?")
        proto = service.get("transport", "tcp")
        product = service.get("product", "unknown")
        version = service.get("version", "")
        banner = service.get("data", "").strip()

        svc_str = f"  [{port}/{proto}] {product}"
        if version:
            svc_str += f" {version}"
        print(svc_str)

        if banner:
            # Show first 2 lines of banner
            banner_lines = banner.split("\n")[:2]
            for line in banner_lines:
                print(f"         {line[:120]}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Query Shodan for host information")
    parser.add_argument("target", help="IP address or hostname to look up")
    args = parser.parse_args()

    api_key = os.environ.get("SHODAN_API_KEY")
    if not api_key:
        print("[!] SHODAN_API_KEY not set. Get one at https://shodan.io/", file=sys.stderr)
        print("    Usage: SHODAN_API_KEY=your_key python3 shodan_query.py <target>", file=sys.stderr)
        sys.exit(1)

    data = query_shodan_curl(args.target, api_key)
    display_results(data, args.target)


if __name__ == "__main__":
    main()
