#!/usr/bin/env python3
"""
CVE Lookup — Reusable wrapper for vulnerability analysis.

Maps service/version combinations to known CVEs using the NVD API.
Can analyze individual services or batch-process enum JSON output.

This is a stable wrapper that delegates to the existing implementation
in vuln/scripts/cve_lookup.py.

Usage:
    # Direct service lookup
    python3 cve_lookup.py --service openssh --version "8.2p1"
    
    # Batch analyze enum JSON output
    python3 cve_lookup.py --file loot/enum-<target>-<date>.json
    
    # Specific CVE lookup
    python3 cve_lookup.py --cve CVE-2024-6387
    
    # Local exploit database only
    python3 cve_lookup.py --service apache --version "2.4.49" --searchsploit-only
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path


def load_core_module():
    """Load the core CVE lookup implementation from vuln/scripts."""
    # Find the workspace root
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "vuln" / "scripts" / "cve_lookup.py").exists():
            core_path = parent / "vuln" / "scripts" / "cve_lookup.py"
            break
    else:
        # Fallback to relative path from this file
        core_path = Path(__file__).resolve().parents[3] / "vuln" / "scripts" / "cve_lookup.py"
    
    if not core_path.exists():
        raise FileNotFoundError(f"Core CVE lookup module not found at {core_path}")
    
    spec = importlib.util.spec_from_file_location("cve_lookup_core", core_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module spec from {core_path}")
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Look up CVEs for service versions",
        epilog="This wrapper delegates to vuln/scripts/cve_lookup.py"
    )
    parser.add_argument("--service", help="Service name (e.g., openssh, apache)")
    parser.add_argument("--version", help="Service version (e.g., 8.2p1)")
    parser.add_argument("--cve", help="Look up a specific CVE ID")
    parser.add_argument("--file", help="Analyze enum JSON output file")
    parser.add_argument("--max-results", type=int, default=10, help="Max CVE results (default: 10)")
    parser.add_argument("--searchsploit-only", action="store_true", help="Only use searchsploit")
    parser.add_argument("--wrapper-info", action="store_true", help="Show wrapper information")
    
    args = parser.parse_args()
    
    if args.wrapper_info:
        print("CVE Lookup Wrapper")
        print("==================")
        print("Location: scripts/opencode/reusable/cve_lookup.py")
        print("Core implementation: vuln/scripts/cve_lookup.py")
        print("")
        print("This wrapper provides a stable entrypoint for CVE lookups.")
        print("It delegates all functionality to the existing implementation.")
        return 0
    
    # Load and run the core implementation
    try:
        core_module = load_core_module()
    except Exception as e:
        print(f"[ERROR] Failed to load core CVE lookup module: {e}", file=sys.stderr)
        return 1
    
    # Override sys.argv to pass through to the core module's main()
    # Remove --wrapper-info if present since core doesn't know about it
    original_argv = sys.argv.copy()
    sys.argv = [original_argv[0]] + [arg for arg in original_argv[1:] if arg != "--wrapper-info"]
    
    # Run the core module's main
    try:
        return core_module.main() or 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 0
    except Exception as e:
        print(f"[ERROR] CVE lookup failed: {e}", file=sys.stderr)
        return 1
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    raise SystemExit(main())
