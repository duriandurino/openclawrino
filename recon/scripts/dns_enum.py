#!/usr/bin/env python3
"""
DNS Subdomain Enumerator

Uses common wordlists and DNS brute-force to discover subdomains.
No direct target probing beyond DNS queries (passive).

Usage:
    python3 dns_enum.py <domain> [--wordlist <path>]

Output: Discovered subdomains with their resolved IPs.
"""

import sys
import subprocess
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Common subdomain prefixes for quick recon
DEFAULT_WORDLIST = [
    "www", "mail", "ftp", "admin", "test", "dev", "staging", "api",
    "cdn", "db", "database", "backup", "vpn", "remote", "portal",
    "webmail", "mx", "ns1", "ns2", "smtp", "pop", "imap",
    "git", "gitlab", "github", "jenkins", "ci", "cd",
    "monitor", "grafana", "kibana", "elastic", "prometheus",
    "docker", "k8s", "kubernetes", "registry",
    "blog", "forum", "wiki", "docs", "support", "help",
    "shop", "store", "pay", "billing", "invoice",
    "login", "sso", "auth", "oauth", "id",
    "file", "share", "cloud", "drive", "s3", "minio",
    "app", "mobile", "m", "wap",
    "intranet", "internal", "corp", "office", "hr", "it",
    "proxy", "gateway", "lb", "loadbalancer", "haproxy", "nginx",
]


def resolve_host(subdomain, domain):
    """Attempt to resolve a subdomain via dig."""
    target = f"{subdomain}.{domain}"
    try:
        result = subprocess.run(
            ["dig", "+short", "+time=2", "+tries=1", target],
            capture_output=True, text=True, timeout=5
        )
        ips = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
        if ips:
            return target, ips
    except FileNotFoundError:
        print("[ERROR] 'dig' not found. Install with: sudo apt install dnsutils", file=sys.stderr)
        sys.exit(1)
    except (subprocess.TimeoutExpired, Exception):
        pass
    return None, None


def main():
    parser = argparse.ArgumentParser(description="Enumerate subdomains via DNS brute-force")
    parser.add_argument("domain", help="Target domain (e.g., example.com)")
    parser.add_argument("--wordlist", help="Path to custom wordlist file (one per line)")
    parser.add_argument("--threads", type=int, default=10, help="Concurrent threads (default: 10)")
    args = parser.parse_args()

    domain = args.domain.strip().lower()
    if domain.startswith("http://") or domain.startswith("https://"):
        domain = domain.split("//")[1].split("/")[0]

    # Load wordlist
    words = DEFAULT_WORDLIST
    if args.wordlist:
        try:
            with open(args.wordlist) as f:
                words = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        except FileNotFoundError:
            print(f"[ERROR] Wordlist not found: {args.wordlist}", file=sys.stderr)
            sys.exit(1)

    print(f"[*] Enumerating subdomains for: {domain}")
    print(f"[*] Testing {len(words)} prefixes with {args.threads} threads\n")

    found = []
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(resolve_host, word, domain): word for word in words}
        for future in as_completed(futures):
            subdomain, ips = future.result()
            if subdomain and ips:
                ip_str = ", ".join(ips)
                print(f"  [+] {subdomain} -> {ip_str}")
                found.append((subdomain, ips))

    print(f"\n[*] Found {len(found)} subdomains for {domain}")
    if not found:
        print("[*] No subdomains discovered — try a larger wordlist or CT log lookup")


if __name__ == "__main__":
    main()
