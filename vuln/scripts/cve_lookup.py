#!/usr/bin/env python3
"""
CVE Lookup — Version-to-CVE mapper

Maps service/version combinations to known CVEs using the NVD API.
Can analyze individual services or batch-process enum JSON output.

Usage:
    python3 cve_lookup.py --service openssh --version "8.2p1"
    python3 cve_lookup.py --file loot/enum-<target>-<date>.json
    python3 cve_lookup.py --cve CVE-2024-6387
"""

import json
import sys
import argparse
import subprocess
import re
from datetime import datetime


# Common service name mappings (nmap → NVD keywords)
SERVICE_MAP = {
    "ssh": "openssh",
    "ftp": "vsftpd",
    "http": "apache http server",
    "https": "apache http server",
    "mysql": "mysql",
    "postgresql": "postgresql",
    "smtp": "postfix",
    "dns": "bind",
    "samba": "samba",
    "telnet": "telnet",
    "redis": "redis",
    "mongodb": "mongodb",
}


def query_nvd(service, version=None, cve_id=None, max_results=10):
    """Query NVD API for CVEs."""
    if cve_id:
        url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve_id}"
    else:
        keyword = f"{service}"
        if version:
            keyword += f" {version}"
        url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={keyword.replace(' ', '+')}&resultsPerPage={max_results}"

    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "15", url],
            capture_output=True, text=True, timeout=20
        )
        return json.loads(result.stdout)
    except (json.JSONDecodeError, subprocess.TimeoutExpired, Exception) as e:
        print(f"[!] NVD query failed: {e}", file=sys.stderr)
        return None


def parse_nvd_response(data):
    """Extract CVE details from NVD response."""
    vulns = []
    for item in data.get("vulnerabilities", []):
        cve = item.get("cve", {})
        cve_id = cve.get("id", "UNKNOWN")

        # Get CVSS score
        metrics = cve.get("metrics", {})
        cvss_score = None
        severity = "N/A"

        # Try CVSS v3.1 first, then v3.0, then v2
        for metric_key in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
            if metric_key in metrics and metrics[metric_key]:
                cvss = metrics[metric_key][0].get("cvssData", {})
                cvss_score = cvss.get("baseScore")
                severity = cvss.get("baseSeverity", "N/A")
                break

        # Get description
        descriptions = cve.get("descriptions", [])
        desc = ""
        for d in descriptions:
            if d.get("lang") == "en":
                desc = d.get("value", "")
                break

        # Get published date
        published = cve.get("published", "")[:10]

        # Check if any known exploit
        references = cve.get("references", [])
        has_exploit = any(
            "exploit" in ref.get("tags", []) or "exploit" in ref.get("url", "").lower()
            for ref in references
        )

        vulns.append({
            "id": cve_id,
            "cvss": cvss_score,
            "severity": severity,
            "description": desc[:200],
            "published": published,
            "has_exploit": has_exploit,
            "references_count": len(references)
        })

    return vulns


def searchsploit(service, version=None):
    """Query searchsploit for local exploit database."""
    query = f"{service}"
    if version:
        query += f" {version}"

    try:
        result = subprocess.run(
            ["searchsploit", "--json", query],
            capture_output=True, text=True, timeout=30
        )
        data = json.loads(result.stdout)
        return data.get("RESULTS_EXPLOIT", [])
    except (json.JSONDecodeError, subprocess.TimeoutExpired, FileNotFoundError):
        return []


def check_version_vulnerable(target_version, vulnerable_ranges):
    """Check if a version falls within a known vulnerable range."""
    # Simple version comparison — works for most cases
    try:
        target_parts = [int(x) for x in re.findall(r'\d+', target_version)]
        for range_start, range_end in vulnerable_ranges:
            start_parts = [int(x) for x in re.findall(r'\d+', range_start)]
            end_parts = [int(x) for x in re.findall(r'\d+', range_end)]

            if target_parts >= start_parts and target_parts <= end_parts:
                return True
    except (ValueError, TypeError):
        pass
    return False


def main():
    parser = argparse.ArgumentParser(description="Look up CVEs for service versions")
    parser.add_argument("--service", help="Service name (e.g., openssh, apache)")
    parser.add_argument("--version", help="Service version (e.g., 8.2p1)")
    parser.add_argument("--cve", help="Look up a specific CVE ID")
    parser.add_argument("--file", help="Analyze enum JSON output file")
    parser.add_argument("--max-results", type=int, default=10, help="Max CVE results")
    parser.add_argument("--searchsploit-only", action="store_true", help="Only use searchsploit")
    args = parser.parse_args()

    if args.cve:
        # Specific CVE lookup
        print(f"[*] Looking up {args.cve}...")
        data = query_nvd(cve_id=args.cve)
        if data:
            vulns = parse_nvd_response(data)
            for v in vulns:
                print(f"\n  {v['id']} | CVSS: {v['cvss']} | {v['severity']}")
                print(f"  Published: {v['published']}")
                print(f"  {v['description']}")
                print(f"  Exploit available: {'YES' if v['has_exploit'] else 'No'}")
        sys.exit(0)

    if args.file:
        # Batch analyze enum output
        try:
            with open(args.file) as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] File not found: {args.file}", file=sys.stderr)
            sys.exit(1)

        services = data.get("open_ports", [])
        if not services:
            print("[!] No service data found in file")
            sys.exit(1)

        print(f"[*] Analyzing {len(services)} services from {args.file}\n")
        for svc in services:
            port = svc.get("port", "?")
            service = svc.get("service", "unknown")
            version = svc.get("version", "")

            print(f"{'='*60}")
            print(f"[*] {port} — {service} {version}")

            # Normalize service name
            svc_name = SERVICE_MAP.get(service.lower(), service)

            # searchsploit
            exploits = searchsploit(svc_name, version)
            if exploits:
                print(f"  searchsploit: {len(exploits)} results")
                for exp in exploits[:5]:
                    print(f"    • {exp.get('Title', 'N/A')}")
                    print(f"      {exp.get('EDB-ID', '?')} | {exp.get('Platform', '?')}")
            else:
                print(f"  searchsploit: no results")

            # NVD (skip if searchsploit-only)
            if not args.searchsploit_only:
                nvd_data = query_nvd(svc_name, version, max_results=3)
                if nvd_data:
                    vulns = parse_nvd_response(nvd_data)
                    if vulns:
                        print(f"  NVD: {len(vulns)} CVEs found")
                        for v in vulns[:3]:
                            exploit_tag = " [EXPLOIT]" if v['has_exploit'] else ""
                            print(f"    • {v['id']} | CVSS: {v['cvss']}{exploit_tag}")
                    else:
                        print(f"  NVD: no CVEs found")
            print()
        sys.exit(0)

    if args.service:
        # Single service lookup
        print(f"[*] Searching for CVEs: {args.service} {args.version or ''}\n")

        # searchsploit
        exploits = searchsploit(args.service, args.version)
        if exploits:
            print(f"searchsploit: {len(exploits)} results\n")
            for exp in exploits[:10]:
                print(f"  • {exp.get('Title', 'N/A')}")
                print(f"    EDB-ID: {exp.get('EDB-ID', '?')} | {exp.get('Platform', '?')}")
                print(f"    Path: {exp.get('Path', '?')}")
                print()
        else:
            print("searchsploit: no results\n")

        if not args.searchsploit_only:
            # NVD
            nvd_data = query_nvd(args.service, args.version, max_results=args.max_results)
            if nvd_data:
                vulns = parse_nvd_response(nvd_data)
                if vulns:
                    print(f"NVD: {len(vulns)} CVEs found\n")
                    for v in vulns:
                        exploit_tag = " [EXPLOIT AVAILABLE]" if v['has_exploit'] else ""
                        print(f"  {v['id']} | CVSS: {v['cvss']} | {v['severity']}{exploit_tag}")
                        print(f"  Published: {v['published']}")
                        print(f"  {v['description']}\n")
                else:
                    print("NVD: no CVEs found")
        sys.exit(0)

    parser.print_help()


if __name__ == "__main__":
    main()
