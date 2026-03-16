#!/usr/bin/env python3
"""
Certificate Transparency Log Subdomain Finder

Queries crt.sh for subdomains discovered via certificate transparency logs.
Free, no API key required.

Usage:
    python3 ct_lookup.py <domain>

Output: List of unique subdomains found in CT logs.
"""

import sys
import json
import argparse
import subprocess


def query_crtsh(domain):
    """Query crt.sh for certificates matching the domain."""
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    result = subprocess.run(
        ["curl", "-s", url],
        capture_output=True, text=True, timeout=30
    )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []

    names = set()
    for entry in data:
        name_value = entry.get("name_value", "")
        for name in name_value.split("\n"):
            name = name.strip().lower()
            if name and name.startswith("*."):
                name = name[2:]  # Strip wildcard prefix
            if name:
                names.add(name)

    return sorted(names)


def main():
    parser = argparse.ArgumentParser(description="Find subdomains via CT logs")
    parser.add_argument("domain", help="Target domain (e.g., example.com)")
    args = parser.parse_args()

    domain = args.domain.strip().lower()
    if domain.startswith("http://") or domain.startswith("https://"):
        domain = domain.split("//")[1].split("/")[0]

    print(f"[*] Querying CT logs for: {domain}")
    subdomains = query_crtsh(domain)

    if subdomains:
        print(f"[*] Found {len(subdomains)} subdomains:\n")
        for s in subdomains:
            print(f"  {s}")
    else:
        print("[*] No subdomains found in CT logs")


if __name__ == "__main__":
    main()
