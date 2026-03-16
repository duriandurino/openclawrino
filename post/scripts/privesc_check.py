#!/usr/bin/env python3
"""
Privesc Checker — Quick privilege escalation enumeration

Runs common privilege escalation checks and outputs findings.
Designed to be lightweight and fast — no external dependencies.

Usage:
    python3 privesc_check.py
    python3 privesc_check.py --output loot/privesc.txt
"""

import subprocess
import argparse
import os
import sys
import re


def run_cmd(cmd, timeout=10):
    """Run a command and return output."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, Exception):
        return ""


def check_user_info():
    """Check current user context."""
    print("\n" + "="*60)
    print("[*] USER INFORMATION")
    print("="*60)
    print(f"  whoami: {run_cmd('whoami')}")
    print(f"  id: {run_cmd('id')}")
    print(f"  groups: {run_cmd('groups')}")


def check_suid():
    """Find SUID binaries."""
    print("\n" + "="*60)
    print("[*] SUID BINARIES")
    print("="*60)
    suid = run_cmd("find / -perm -4000 -type f 2>/dev/null")
    if suid:
        bins = suid.splitlines()
        # Known safe SUID binaries
        safe = {"passwd", "su", "sudo", "mount", "umount", "ping", "pkexec",
                "newgrp", "gpasswd", "chsh", "chfn", "at"}
        unusual = []
        for b in bins:
            name = os.path.basename(b)
            if name not in safe:
                unusual.append(b)
        if unusual:
            print("  [!] Unusual SUID binaries found:")
            for b in unusual[:20]:
                print(f"      {b}")
        else:
            print("  No unusual SUID binaries found")
    else:
        print("  None found")


def check_sudo():
    """Check sudo rights."""
    print("\n" + "="*60)
    print("[*] SUDO RIGHTS")
    print("="*60)
    sudo_l = run_cmd("sudo -l 2>/dev/null")
    if sudo_l:
        print(f"  {sudo_l}")
        if "NOPASSWD" in sudo_l:
            print("  [!] NOPASSWD entries found — potential privesc!")
    else:
        print("  No sudo rights or sudo not available")


def check_capabilities():
    """Check file capabilities."""
    print("\n" + "="*60)
    print("[*] FILE CAPABILITIES")
    print("="*60)
    caps = run_cmd("getcap -r / 2>/dev/null")
    if caps:
        for line in caps.splitlines()[:15]:
            print(f"  {line}")
        dangerous = [l for l in caps.splitlines()
                     if any(d in l.lower() for d in ["setuid", "dac_override", "sys_admin", "setgid"])]
        if dangerous:
            print("\n  [!] Dangerous capabilities:")
            for d in dangerous:
                print(f"      {d}")
    else:
        print("  No capabilities set")


def check_cron():
    """Check for writable cron jobs."""
    print("\n" + "="*60)
    print("[*] CRON JOBS")
    print("="*60)
    crontab = run_cmd("cat /etc/crontab 2>/dev/null")
    if crontab:
        for line in crontab.splitlines():
            if not line.startswith("#") and line.strip():
                print(f"  {line}")
    cron_dir = run_cmd("ls -la /etc/cron.*/ 2>/dev/null")
    if cron_dir:
        print(f"\n  Cron directories:\n{cron_dir[:500]}")

    # Check for writable cron scripts
    writable = run_cmd("find /etc/cron* -writable 2>/dev/null")
    if writable:
        print(f"\n  [!] WRITABLE CRON FILES:")
        for w in writable.splitlines():
            print(f"      {w}")


def check_kernel():
    """Check kernel version for known exploits."""
    print("\n" + "="*60)
    print("[*] KERNEL VERSION")
    print("="*60)
    kernel = run_cmd("uname -r")
    print(f"  Version: {kernel}")

    # Flag known vulnerable kernels
    try:
        parts = kernel.split('.')
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0

        vulns = []
        if major < 5 or (major == 5 and minor < 15):
            vulns.append("DirtyPipe (CVE-2022-0847) — kernels <5.15.25")
        if major < 6 or (major == 6 and minor < 1):
            vulns.append("DirtyCow-like (CVE-2016-5195) — kernels <4.8.3")
        if major < 5 or (major == 5 and minor < 6):
            vulns.append("PwnKit (CVE-2021-4034) — polkit, most kernels")

        if vulns:
            print("\n  [!] Potentially vulnerable to:")
            for v in vulns:
                print(f"      {v}")
    except (ValueError, IndexError):
        pass


def check_network():
    """Check network position."""
    print("\n" + "="*60)
    print("[*] NETWORK")
    print("="*60)
    print(f"  Interfaces:\n{run_cmd('ip addr 2>/dev/null || ifconfig 2>/dev/null')[:600]}")
    print(f"\n  Routes:\n{run_cmd('ip route 2>/dev/null || route -n 2>/dev/null')[:300]}")

    # Listen ports
    ports = run_cmd("ss -tulpn 2>/dev/null || netstat -tulpn 2>/dev/null")
    if ports:
        print(f"\n  Listening ports:\n{ports[:500]}")


def check_interesting_files():
    """Find interesting files."""
    print("\n" + "="*60)
    print("[*] INTERESTING FILES")
    print("="*60)

    checks = {
        "SSH Keys": "find /home /root -name 'id_rsa' -o -name 'id_ed25519' 2>/dev/null",
        "Config passwords": "grep -rli 'password\\|passwd\\|secret' /etc/ 2>/dev/null | head -10",
        "Web configs": "find /var/www -name 'wp-config.php' -o -name '.env' -o -name 'config.php' 2>/dev/null",
        "Writable /etc/passwd": "ls -la /etc/passwd 2>/dev/null | grep -q 'w' && echo 'WRITABLE!' || echo 'OK'",
        "Docker socket": "ls -la /var/run/docker.sock 2>/dev/null",
    }

    for label, cmd in checks.items():
        result = run_cmd(cmd)
        if result:
            print(f"  {label}:")
            for line in result.splitlines()[:5]:
                print(f"      {line}")


def check_writable_dirs():
    """Check for writable system directories."""
    print("\n" + "="*60)
    print("[*] WRITABLE SYSTEM PATHS")
    print("="*60)

    paths = ["/etc/cron*", "/etc/systemd/*", "/etc/init.d/*",
             "/tmp", "/var/tmp", "/dev/shm", "/etc/passwd"]
    for pattern in paths:
        writable = run_cmd(f"find {pattern} -writable 2>/dev/null | head -5")
        if writable:
            for w in writable.splitlines():
                print(f"  [!] {w}")


def main():
    parser = argparse.ArgumentParser(description="Quick privilege escalation checks")
    parser.add_argument("--output", help="Save output to file")
    args = parser.parse_args()

    if args.output:
        sys.stdout = open(args.output, "w")

    print("="*60)
    print("  PRIVILEGE ESCALATION ENUMERATION")
    print("="*60)

    check_user_info()
    check_suid()
    check_sudo()
    check_capabilities()
    check_cron()
    check_kernel()
    check_network()
    check_interesting_files()
    check_writable_dirs()

    print("\n" + "="*60)
    print("  [✓] Enumeration complete")
    print("="*60)

    if args.output:
        sys.stdout.close()
        print(f"Output saved to: {args.output}")


if __name__ == "__main__":
    main()
