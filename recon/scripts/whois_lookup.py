#!/usr/bin/env python3
"""
WHOIS Lookup Tool

Extract key fields from WHOIS data for a domain or IP.
Wraps the system `whois` command and parses common fields.

Usage:
    python3 whois_lookup.py <domain|ip>
    python3 whois_lookup.py <domain> --json
"""

import sys
import json
import argparse
import subprocess
import re

# Fields to extract (case-insensitive match)
RELEVANT_FIELDS = [
    "registrar", "registrant", "registrant name", "registrant organization",
    "registrant country", "registrant state", "registrant city",
    "creation date", "created", "registered",
    "updated date", "last modified",
    "expiration date", "expires",
    "name server", "nameserver", "nserver",
    "status", "domain status",
    "dnssec",
    "organization", "org", "descr", "description",
    "country", "netrange", "cidr", "role",
    "admin-c", "tech-c", "abuse-c",
    "source", "mnt-by",
]


def run_whois(target):
    """Run whois command and return raw output."""
    try:
        result = subprocess.run(
            ["whois", target],
            capture_output=True, text=True, timeout=15
        )
        return result.stdout
    except FileNotFoundError:
        print("[ERROR] 'whois' command not found. Install with: sudo apt install whois", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print(f"[ERROR] WHOIS lookup timed out for {target}", file=sys.stderr)
        sys.exit(1)


def parse_whois(raw_output):
    """Extract relevant fields from raw WHOIS text."""
    parsed = {}
    for line in raw_output.splitlines():
        line = line.strip()
        if not line or line.startswith("%") or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key_lower = key.strip().lower()
            if key_lower in RELEVANT_FIELDS:
                clean_key = key.strip()
                clean_value = value.strip()
                if clean_key in parsed:
                    # Append multiple values (e.g., nameservers)
                    if isinstance(parsed[clean_key], list):
                        parsed[clean_key].append(clean_value)
                    else:
                        parsed[clean_key] = [parsed[clean_key], clean_value]
                else:
                    parsed[clean_key] = clean_value
    return parsed


def redact_sensitive(parsed):
    """Redact personal information from WHOIS data for reporting."""
    sensitive_keys = {"registrant name", "registrant", "admin-c", "tech-c", "phone", "email"}
    redacted = {}
    for key, value in parsed.items():
        if key.lower() in sensitive_keys:
            redacted[key] = "[REDACTED]"
        else:
            redacted[key] = value
    return redacted


def display(parsed, target, as_json=False):
    """Display parsed WHOIS data."""
    if as_json:
        print(json.dumps(parsed, indent=2))
        return

    print(f"[*] WHOIS Results for: {target}")
    print()

    # Group by category
    sections = {
        "Registration": ["registrar", "registrant organization", "registrant country",
                         "registrant state", "registrant city"],
        "Dates": ["creation date", "created", "registered", "updated date",
                  "last modified", "expiration date", "expires"],
        "Name Servers": ["name server", "nameserver", "nserver"],
        "Status": ["status", "domain status", "dnssec"],
        "Network": ["organization", "org", "descr", "description",
                    "country", "netrange", "cidr"],
    }

    displayed = set()
    for section, keys in sections.items():
        section_data = {}
        for key in keys:
            for k, v in parsed.items():
                if k.lower() == key and k not in displayed:
                    section_data[k] = v
                    displayed.add(k)
        if section_data:
            print(f"  {section}:")
            for k, v in section_data.items():
                if isinstance(v, list):
                    for item in v:
                        print(f"    {k}: {item}")
                else:
                    print(f"    {k}: {v}")
            print()

    # Any remaining fields
    remaining = {k: v for k, v in parsed.items() if k not in displayed}
    if remaining:
        print(f"  Other:")
        for k, v in remaining.items():
            print(f"    {k}: {v}")


def main():
    parser = argparse.ArgumentParser(description="WHOIS lookup with field extraction")
    parser.add_argument("target", help="Domain or IP to look up")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--no-redact", action="store_true", help="Don't redact personal info")
    args = parser.parse_args()

    raw = run_whois(args.target)
    parsed = parse_whois(raw)

    if not parsed:
        print("[!] No structured data parsed from WHOIS output")
        print("[*] Raw output:")
        print(raw[:2000])
        sys.exit(0)

    if not args.no_redact:
        parsed = redact_sensitive(parsed)

    display(parsed, args.target, args.json)


if __name__ == "__main__":
    main()
