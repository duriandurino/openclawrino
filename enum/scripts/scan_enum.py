#!/usr/bin/env python3
"""
Scan Orchestrator — Multi-phase nmap scanning

Runs a structured scan progression from discovery to full enumeration.
Outputs structured results for the vuln analysis phase.

Usage:
    python3 scan_enum.py <target> [--output-dir loot/] [--full]

Phases:
    1. Ping sweep / host discovery
    2. Quick scan (top 1000 ports)
    3. Full port scan (all 65535 ports)
    4. Service version detection on open ports
    5. Script scan on open ports
"""

import subprocess
import argparse
import sys
import os
import json
from datetime import datetime


def run_nmap(args, label):
    """Run an nmap command and return the output."""
    print(f"\n[*] Phase: {label}")
    print(f"    Command: {' '.join(args)}")
    try:
        result = subprocess.run(
            args,
            capture_output=True, text=True, timeout=600
        )
        if result.returncode != 0 and "deprecated" not in result.stderr.lower():
            print(f"    [!] nmap returned code {result.returncode}")
        return result.stdout
    except subprocess.TimeoutExpired:
        print(f"    [!] Timed out after 600s")
        return ""
    except FileNotFoundError:
        print(f"[ERROR] 'nmap' not found. Install with: sudo apt install nmap", file=sys.stderr)
        sys.exit(1)


def parse_open_ports(nmap_output):
    """Extract open ports from nmap grepable output."""
    open_ports = []
    for line in nmap_output.splitlines():
        if "/open/" in line:
            # Format: 22/open/tcp//ssh///
            parts = line.split("/")
            if len(parts) >= 4:
                port = parts[0]
                proto = parts[2]
                service = parts[4] if len(parts) > 4 else "unknown"
                open_ports.append({
                    "port": int(port),
                    "protocol": proto,
                    "service": service
                })
    return open_ports


def main():
    parser = argparse.ArgumentParser(description="Multi-phase nmap enumeration")
    parser.add_argument("target", help="Target IP or hostname")
    parser.add_argument("--output-dir", default="loot", help="Output directory (default: loot)")
    parser.add_argument("--full", action="store_true", help="Run full port scan (65535 ports)")
    parser.add_argument("--fast", action="store_true", help="Only run quick scan (top 1000)")
    parser.add_argument("--stealth", action="store_true", help="Use slower, stealthier scan timing")
    args = parser.parse_args()

    target = args.target
    output_dir = args.output_dir
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    os.makedirs(output_dir, exist_ok=True)

    # Common timing template
    stealth_timing = ["-T2", "--max-rate", "50"] if args.stealth else ["-T4"]

    results = {"target": target, "timestamp": timestamp, "phases": []}

    # Phase 1: Host discovery
    ping_output = run_nmap(["sudo", "nmap", "-sn", target, "-oG", "-"], "Host Discovery")
    if "Status: Down" in ping_output:
        print(f"[!] Target {target} appears down — continuing anyway")
    results["phases"].append({"phase": "discovery", "status": "done"})

    # Phase 2: Quick scan (top 1000)
    quick_file = f"{output_dir}/enum-{target}-quick-{timestamp}"
    quick_output = run_nmap(
        ["nmap", "-sV", "-sC", "--top-ports", "1000"] + stealth_timing +
        ["-oA", quick_file, target],
        "Quick Scan (Top 1000)"
    )
    open_ports = parse_open_ports(quick_output)
    results["open_ports"] = open_ports
    results["phases"].append({"phase": "quick_scan", "ports_found": len(open_ports)})

    port_list = [str(p["port"]) for p in open_ports]

    if args.fast:
        print(f"\n[✓] Fast scan complete. {len(open_ports)} open ports found.")
        if port_list:
            print(f"    Ports: {', '.join(port_list)}")
        return

    # Phase 3: Full port scan (if --full or no ports found in quick)
    if args.full or not open_ports:
        full_file = f"{output_dir}/enum-{target}-full-{timestamp}"
        full_output = run_nmap(
            ["nmap", "-p-", "-sV"] + stealth_timing +
            ["-oA", full_file, target],
            "Full Port Scan (1-65535)"
        )
        full_ports = parse_open_ports(full_output)
        # Merge with quick scan results
        existing = {p["port"] for p in open_ports}
        for p in full_ports:
            if p["port"] not in existing:
                open_ports.append(p)
        results["open_ports"] = open_ports
        port_list = [str(p["port"]) for p in open_ports]
        results["phases"].append({"phase": "full_scan", "ports_found": len(open_ports)})

    if not port_list:
        print(f"\n[!] No open ports found on {target}")
        return

    # Phase 4: Detailed service scan on discovered ports
    port_arg = ",".join(port_list)
    detail_file = f"{output_dir}/enum-{target}-detail-{timestamp}"
    detail_output = run_nmap(
        ["nmap", "-sV", "-sC", "-A", "-p", port_arg] + stealth_timing +
        ["-oA", detail_file, target],
        f"Service Detail (ports: {port_arg})"
    )
    results["phases"].append({"phase": "service_detail", "status": "done"})

    # Save structured results
    json_file = f"{output_dir}/enum-{target}-{timestamp}.json"
    with open(json_file, "w") as f:
        json.dump(results, f, indent=2)

    # Summary
    print(f"\n{'='*60}")
    print(f"[✓] Enumeration complete for {target}")
    print(f"    Open ports: {len(open_ports)}")
    for p in open_ports:
        print(f"      {p['port']}/{p['protocol']} — {p['service']}")
    print(f"    Results saved to: {output_dir}/")
    print(f"    JSON: {json_file}")


if __name__ == "__main__":
    main()
