# Quick-Scan Framework Refactoring Plan

## Executive Summary

The quick-scan framework needs structural improvements to address error handling gaps, code duplication, fragile parsing, and maintainability issues while preserving backward compatibility.

## Pain Points Analysis

### 1. Critical: Fragile YAML Parsing
**File:** `run_quick_scan.py:load_quick_manifest()`

Current implementation hand-rolls YAML parsing with string manipulation instead of using a proper YAML parser. This is brittle and will break on valid YAML structures (quoted strings, multiline, nested objects).

```python
# Current (fragile)
def load_quick_manifest(path: Path) -> dict:
    for raw_line in path.read_text(...).splitlines():
        line = raw_line.rstrip()
        # manual parsing with string operations...
```

**Fix:** Use PyYAML or ruamel.yaml for robust parsing.

### 2. Error Handling Gaps

- **No pre-flight validation:** Scripts are executed without checking existence first
- **No step rollback:** Failed steps leave partial state
- **Subprocess without timeout:** `subprocess.run()` can hang indefinitely
- **Silent failures:** Many `check=False` calls ignore errors

### 3. Code Duplication

| Function | Locations |
|----------|-----------|
| `latest_file()` | generate_quick_report.py, export_quick_report.py, publish_quick_report.py |
| `ROOT` resolution | All 6 Python files |
| Subprocess patterns | Repeated across files |
| Path construction | Hardcoded in multiple places |

### 4. Hardcoded Configuration

- `ROOT = Path(__file__).resolve().parents[2]` breaks if file moves
- Script paths: `"scripts/orchestration/run_recon_profile.py"`
- Magic strings for phase names
- No centralized config for paths, timeouts, defaults

### 5. Missing Abstractions

- No shared library module
- Each script is isolated
- No base class for report generators
- No plugin framework for steps

---

## Refactoring Strategy

### Phase 1: Create Shared Library (`quickscan_lib.py`)

Create a comprehensive utility module to eliminate duplication:

```
scripts/quick-scan/quickscan_lib.py
├── Path Utilities
│   ├── get_workspace_root() - Robust root detection
│   ├── get_profiles_dir() - Profile path resolution
│   ├── get_scripts_dir() - Script path resolution
│   └── validate_script_exists() - Pre-flight check
├── File Utilities
│   ├── latest_file() - Consolidated implementation
│   ├── safe_read_text() - Error-handled reading
│   └── safe_write_text() - Atomic writes with backup
├── YAML Utilities
│   ├── load_manifest() - Proper YAML parsing
│   └── validate_manifest() - Schema validation
├── Subprocess Utilities
│   ├── run_step() - Timeout, retry, error handling
│   └── StepResult - Structured result type
└── Configuration
    ├── QuickScanConfig - Centralized settings
    └── get_default_config() - Sensible defaults
```

### Phase 2: Manifest Loading Refactor

Replace fragile string parsing with proper YAML:

```python
# Before (fragile)
def load_quick_manifest(path: Path) -> dict:
    data = {"steps": []}
    current = None
    for raw_line in path.read_text(...).splitlines():
        # 50+ lines of manual parsing

# After (robust)
def load_manifest(path: Path) -> dict:
    import yaml
    with open(path) as f:
        data = yaml.safe_load(f)
    validate_manifest(data)  # Schema check
    return data
```

### Phase 3: Step Execution Framework

Create a robust step runner with rollback:

```python
@dataclass
class StepResult:
    success: bool
    returncode: int
    stdout: str
    stderr: str
    duration_ms: int
    rollback_actions: List[Callable]

class StepExecutor:
    def __init__(self, config: QuickScanConfig):
        self.config = config
        self.executed_steps: List[ExecutedStep] = []

    def run(self, step: dict, context: dict) -> StepResult:
        # Pre-validate
        # Execute with timeout
        # Capture output
        # Track for rollback
        # Return structured result

    def rollback(self) -> None:
        # Reverse executed_steps and run cleanup
```

### Phase 4: Centralized Configuration

Move scattered config to `quickscan_config.yaml`:

```yaml
paths:
  workspace_root: auto-detect  # or explicit path
  profiles_dir: "{workspace}/scripts/quick-scan/profiles"
  scripts_dir: "{workspace}/scripts"
  engagements_dir: "{workspace}/engagements"

defaults:
  mode: "safe"
  account: "hatlesswhite@gmail.com"
  timeout_seconds: 300
  max_retries: 1

execution:
  subprocess_timeout: 300
  capture_output: true
  check_exists_before_run: true

reporting:
  severity_order: ["Critical", "High", "Medium", "Low", "Info"]
  max_findings_in_report: 30
```

### Phase 5: Refactored Script Structure

New organization:

```
scripts/quick-scan/
├── quickscan_lib.py       # NEW: Shared utilities
├── quickscan_config.yaml  # NEW: Centralized config
├── run_quick_scan.py      # REFACTORED: Uses lib
├── recommend_profile.py   # REFACTORED: Uses lib
├── validate_target.py     # REFACTORED: Uses lib
├── generate_quick_report.py  # REFACTORED: Uses lib
├── export_quick_report.py    # REFACTORED: Uses lib
├── publish_quick_report.py   # REFACTORED: Uses lib
└── profiles/
    └── (unchanged - backward compatible)
```

---

## Implementation Details

### Module: quickscan_lib.py

```python
"""Shared utilities for quick-scan framework."""
from __future__ import annotations

import functools
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional, Dict, Any
from datetime import datetime
import yaml

# Module-level cache for workspace root
_WORKSPACE_ROOT: Optional[Path] = None

class QuickScanError(Exception):
    """Base exception for quick-scan errors."""
    pass

class ManifestError(QuickScanError):
    """Invalid manifest file."""
    pass

class StepExecutionError(QuickScanError):
    """Step execution failed."""
    pass


@functools.lru_cache(maxsize=1)
def get_workspace_root() -> Path:
    """Find workspace root using marker files.
    
    Searches upward from current file for:
    - .git directory
    - AGENTS.md file
    - workspace/ directory structure
    """
    global _WORKSPACE_ROOT
    if _WORKSPACE_ROOT:
        return _WORKSPACE_ROOT
    
    # Start from this file's location
    current = Path(__file__).resolve()
    
    for parent in [current] + list(current.parents):
        markers = [
            parent / ".git",
            parent / "AGENTS.md",
            parent / "SOUL.md",
        ]
        if any(m.exists() for m in markers):
            _WORKSPACE_ROOT = parent
            return parent
    
    # Fallback: assume 2 levels up from quick-scan/scripts
    fallback = current.parents[2]
    _WORKSPACE_ROOT = fallback
    return fallback


def get_quickscan_dir() -> Path:
    """Get quick-scan directory."""
    return get_workspace_root() / "scripts" / "quick-scan"


def get_profiles_dir() -> Path:
    """Get profiles directory."""
    return get_quickscan_dir() / "profiles"


def get_engagements_dir() -> Path:
    """Get engagements directory."""
    return get_workspace_root() / "engagements"


def validate_script_exists(script_path: Path) -> None:
    """Validate that a script exists and is executable."""
    if not script_path.exists():
        raise StepExecutionError(f"Script not found: {script_path}")
    if not os.access(script_path, os.X_OK) and script_path.suffix not in ('.py', '.sh'):
        # Python and shell scripts don't need +x for our usage
        pass


def latest_file(directory: Path, pattern: str) -> Optional[Path]:
    """Find most recently modified file matching pattern.
    
    Args:
        directory: Directory to search
        pattern: Glob pattern (e.g., "RECON_SUMMARY_*.md")
    
    Returns:
        Path to latest file or None if no matches
    """
    if not directory.exists():
        return None
    
    matches = sorted(directory.glob(pattern), key=lambda p: p.stat().st_mtime)
    return matches[-1] if matches else None


def safe_read_text(path: Path, default: str = "") -> str:
    """Read file with error handling."""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except (IOError, OSError) as e:
        return default


def safe_write_text(path: Path, content: str, backup: bool = True) -> None:
    """Write file atomically with optional backup."""
    path.parent.mkdir(parents=True, exist_ok=True)
    
    if backup and path.exists():
        backup_path = path.with_suffix(f".backup.{datetime.now():%Y%m%d_%H%M%S}{path.suffix}")
        path.rename(backup_path)
    
    # Atomic write using temp file + rename
    temp = tempfile.NamedTemporaryFile(
        mode='w',
        encoding='utf-8',
        delete=False,
        dir=path.parent,
        prefix=f".tmp_{path.stem}_"
    )
    try:
        temp.write(content)
        temp.close()
        os.rename(temp.name, path)
    except Exception:
        os.unlink(temp.name)
        raise


@dataclass
class ManifestStep:
    """Typed representation of a manifest step."""
    phase: str
    script: str
    args: List[str] = field(default_factory=list)
    optional: bool = False


@dataclass 
class Manifest:
    """Typed quick-scan manifest."""
    name: str
    kind: str
    description: str
    steps: List[ManifestStep]


def load_manifest(path: Path) -> Manifest:
    """Load and validate a quick-scan manifest.
    
    Uses PyYAML for robust parsing with schema validation.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ManifestError(f"Invalid YAML in {path}: {e}")
    except IOError as e:
        raise ManifestError(f"Cannot read manifest {path}: {e}")
    
    # Validate required fields
    if not isinstance(data, dict):
        raise ManifestError(f"Manifest must be a YAML object: {path}")
    
    required = ['name', 'kind', 'steps']
    missing = [f for f in required if f not in data]
    if missing:
        raise ManifestError(f"Missing required fields {missing} in {path}")
    
    if data.get('kind') != 'quick-scan':
        raise ManifestError(f"Invalid kind '{data.get('kind')}', expected 'quick-scan': {path}")
    
    # Parse steps with validation
    steps = []
    for i, step_data in enumerate(data.get('steps', [])):
        if not isinstance(step_data, dict):
            raise ManifestError(f"Step {i} must be an object in {path}")
        
        if 'script' not in step_data:
            raise ManifestError(f"Step {i} missing required 'script' field in {path}")
        
        steps.append(ManifestStep(
            phase=step_data.get('phase', 'unknown'),
            script=step_data['script'],
            args=step_data.get('args', []),
            optional=step_data.get('optional', False)
        ))
    
    return Manifest(
        name=data['name'],
        kind=data['kind'],
        description=data.get('description', ''),
        steps=steps
    )


def resolve_profile(profile: str) -> Path:
    """Resolve profile name or path to full path.
    
    Args:
        profile: Profile name (e.g., "webapp") or path
    
    Returns:
        Path to profile YAML file
    
    Raises:
        FileNotFoundError: If profile cannot be found
    """
    candidate = Path(profile)
    if candidate.exists() and candidate.suffix == '.yaml':
        return candidate
    
    # Try profiles directory
    profiles_dir = get_profiles_dir()
    candidate = profiles_dir / f"{profile}.yaml"
    if candidate.exists():
        return candidate
    
    raise FileNotFoundError(f"Profile not found: {profile}")


@dataclass
class StepResult:
    """Result of step execution."""
    success: bool
    returncode: int
    stdout: str
    stderr: str
    duration_ms: int
    command: List[str]
    step_index: int


class StepExecutor:
    """Execute quick-scan steps with proper error handling."""
    
    def __init__(self, timeout: int = 300, dry_run: bool = False):
        self.timeout = timeout
        self.dry_run = dry_run
        self.results: List[StepResult] = []
    
    def substitute_args(self, args: List[str], context: dict) -> List[str]:
        """Substitute template variables in arguments.
        
        Supports {{variable}} syntax for compatibility.
        """
        result = []
        for arg in args:
            substituted = arg
            for key, value in context.items():
                placeholder = f"{{{{{key}}}}}"
                if placeholder in substituted:
                    substituted = substituted.replace(placeholder, str(value))
            result.append(substituted)
        return result
    
    def run_step(self, step: ManifestStep, context: dict, index: int) -> StepResult:
        """Execute a single step.
        
        Args:
            step: The step to execute
            context: Variable substitution context
            index: Step index for reporting
        
        Returns:
            StepResult with execution details
        """
        # Resolve script path
        script_path = get_workspace_root() / "scripts" / step.script
        
        # Pre-flight validation
        validate_script_exists(script_path)
        
        # Build command
        args = self.substitute_args(step.args, context)
        cmd = [str(script_path)] + args
        
        if self.dry_run:
            print(f"[DRY-RUN] Would execute: {' '.join(cmd)}")
            return StepResult(
                success=True,
                returncode=0,
                stdout="",
                stderr="",
                duration_ms=0,
                command=cmd,
                step_index=index
            )
        
        # Execute with timing and timeout
        import time
        start = time.time()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=get_workspace_root()
            )
        except subprocess.TimeoutExpired as e:
            duration_ms = int((time.time() - start) * 1000)
            return StepResult(
                success=False,
                returncode=-1,
                stdout=e.stdout or "",
                stderr=f"Timeout after {self.timeout}s",
                duration_ms=duration_ms,
                command=cmd,
                step_index=index
            )
        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            return StepResult(
                success=False,
                returncode=-1,
                stdout="",
                stderr=str(e),
                duration_ms=duration_ms,
                command=cmd,
                step_index=index
            )
        
        duration_ms = int((time.time() - start) * 1000)
        
        step_result = StepResult(
            success=result.returncode == 0,
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
            duration_ms=duration_ms,
            command=cmd,
            step_index=index
        )
        
        self.results.append(step_result)
        return step_result


# Legacy compatibility aliases
load_quick_manifest = load_manifest  # For backward compatibility
```

### Refactored: run_quick_scan.py

```python
#!/usr/bin/env python3
"""Refactored quick-scan runner using shared library."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Import shared library
from quickscan_lib import (
    get_workspace_root,
    get_engagements_dir,
    load_manifest,
    resolve_profile,
    StepExecutor,
    ManifestStep,
    QuickScanError,
)

MODE_DEFAULTS = {
    "safe": {
        "safe_flag": "--safe",
        "fast_flag": "",
        "skip_optional_recon": "false",
        "skip_optional_vuln": "false",
    },
    "fast": {
        "safe_flag": "--safe",
        "fast_flag": "--fast",
        "skip_optional_recon": "true",
        "skip_optional_vuln": "false",
    },
}


def load_recommender():
    """Dynamically load recommender module."""
    import importlib.util
    module_path = get_workspace_root() / "scripts" / "quick-scan" / "recommend_profile.py"
    spec = importlib.util.spec_from_file_location("recommender", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load recommender from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def latest_enum_json(engagement: str) -> str:
    """Find latest enumeration JSON."""
    from quickscan_lib import latest_file
    parsed_dir = get_engagements_dir() / engagement / "enum" / "parsed"
    
    patterns = [
        "nmap-service-*.json",
        "nmap-fast-*.json",
        "web-basic-*.json",
        "smb-basic-*.json",
        "*.json",
    ]
    
    for pattern in patterns:
        match = latest_file(parsed_dir, pattern)
        if match:
            return str(match)
    return ""


def ensure_reporting_dir(engagement: str) -> Path:
    """Create reporting directory for engagement."""
    path = get_engagements_dir() / engagement / "quick-scan" / "reporting"
    path.mkdir(parents=True, exist_ok=True)
    return path


def should_skip_step(step: ManifestStep, mode: str) -> bool:
    """Determine if step should be skipped based on mode."""
    return mode == "fast" and step.optional


def choose_profile(profile: str | None, hint: str | None) -> tuple[str, dict | None]:
    """Select profile from explicit name or hint."""
    if profile:
        return profile, None
    if hint:
        recommender = load_recommender()
        recommendation = recommender.recommend(hint)
        return recommendation["profile"], recommendation
    raise ValueError("Either --profile or --hint is required")


def run_phase_summary(engagement: str, phase: str) -> None:
    """Generate phase summary if data exists."""
    from quickscan_lib import latest_file
    import subprocess
    
    phase_dir = get_engagements_dir() / engagement / phase / "parsed"
    if not phase_dir.exists():
        return
    
    if not any(phase_dir.glob("*.json")):
        return
    
    subprocess.run([
        "python3",
        str(get_workspace_root() / "scripts" / "orchestration" / "generate_phase_summary.py"),
        "--engagement", engagement,
        "--phase", phase,
    ], cwd=get_workspace_root(), check=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run quick security scan profile")
    parser.add_argument("--profile", default="", help="Quick-scan profile name or path")
    parser.add_argument("--hint", default="", help="Free-text target description")
    parser.add_argument("--target", required=True, help="Target host, URL, or domain")
    parser.add_argument("--engagement", default="", help="Engagement folder name")
    parser.add_argument("--mode", choices=["safe", "fast"], default="safe")
    parser.add_argument("--account", default="hatlesswhite@gmail.com")
    parser.add_argument("--no-publish", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Show what would run without executing")
    parser.add_argument("--timeout", type=int, default=300, help="Step timeout in seconds")
    args = parser.parse_args()

    try:
        chosen_profile, recommendation = choose_profile(
            args.profile or None,
            args.hint or None
        )
    except ValueError as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        return 1

    try:
        manifest_path = resolve_profile(chosen_profile)
        manifest = load_manifest(manifest_path)
    except (FileNotFoundError, QuickScanError) as e:
        print(f"[!] Error loading profile: {e}", file=sys.stderr)
        return 1

    engagement = args.engagement or f"quick-{manifest.name}-{datetime.now():%Y-%m-%d_%H%M}"
    ensure_reporting_dir(engagement)

    print(f"[*] Profile: {manifest.name}")
    if recommendation:
        print(f"[*] Auto-selected from hint: {args.hint}")
        print(f"[*] Reason: {recommendation['reason']}")
    print(f"[*] Engagement: {engagement}")
    print(f"[*] Mode: {args.mode}")
    print(f"[*] Description: {manifest.description}")

    # Build execution context
    context = {
        "target": args.target,
        "engagement": engagement,
        "latest_enum_json": latest_enum_json(engagement),
        "mode": args.mode,
        **MODE_DEFAULTS[args.mode],
    }

    # Execute steps
    executor = StepExecutor(timeout=args.timeout, dry_run=args.dry_run)
    executed = 0
    failed = 0

    for i, step in enumerate(manifest.steps, start=1):
        if should_skip_step(step, args.mode):
            print(f"[{i}/{len(manifest.steps)}] SKIP (optional in {args.mode} mode): {step.script}")
            continue

        print(f"[{i}/{len(manifest.steps)}] RUN: {step.script}")
        result = executor.run_step(step, context, i)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr and not result.success:
            print(f"[!] stderr: {result.stderr}")
        
        if not result.success:
            failed += 1
            print(f"[!] Step {i} failed with code {result.returncode}")
            if not step.optional:
                print("[!] Non-optional step failed, aborting")
                return result.returncode
        else:
            executed += 1
            print(f"[✓] Completed in {result.duration_ms}ms")

    # Generate phase summaries
    for phase in ["recon", "enum", "vuln"]:
        run_phase_summary(engagement, phase)

    # Generate quick report
    report_script = get_workspace_root() / "scripts" / "quick-scan" / "generate_quick_report.py"
    if report_script.exists():
        import subprocess
        subprocess.run([
            "python3", str(report_script),
            "--engagement", engagement,
            "--profile", manifest.name,
            "--target", args.target,
            "--mode", args.mode,
            "--steps", str(executed),
        ], cwd=get_workspace_root(), check=False)

    # Export/Publish
    if not args.no_publish and not args.dry_run:
        for script_name in ["export_quick_report.py", "publish_quick_report.py"]:
            script = get_workspace_root() / "scripts" / "quick-scan" / script_name
            if script.exists():
                import subprocess
                subprocess.run([
                    "python3", str(script),
                    "--engagement", engagement,
                    *("--account", args.account) if "publish" in script_name else []
                ], cwd=get_workspace_root(), check=False)

    print(f"\n[✓] Quick scan complete: engagements/{engagement}/")
    print(f"    Steps executed: {executed}, Failed: {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

### Refactored: recommend_profile.py

```python
#!/usr/bin/env python3
"""Profile recommender with shared library integration."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import List, Dict, Any

from quickscan_lib import get_profiles_dir

PROFILE_RULES = [
    {
        "profile": "player-pulselink",
        "score": 100,
        "tokens": ["pulselink", "n-compass", "nctv", "player"],
        "reason": "Target hints strongly match a PulseLink / player environment.",
    },
    {
        "profile": "iot-mqtt",
        "score": 95,
        "tokens": ["mqtt", "broker", "iot", "telemetry"],
        "reason": "Target hints suggest MQTT or IoT messaging exposure.",
    },
    {
        "profile": "nestjs-api",
        "score": 96,
        "tokens": ["nestjs", "nest.js", "swagger", "openapi", "controller", "guard", "decorator"],
        "reason": "Target hints suggest a NestJS API with framework/docs surface to triage.",
    },
    {
        "profile": "graphql",
        "score": 94,
        "tokens": ["graphql", "graphiql", "apollo", "schema", "introspection", "mutation"],
        "reason": "Target hints suggest a GraphQL surface that should be triaged directly.",
    },
    {
        "profile": "webhook",
        "score": 92,
        "tokens": ["webhook", "callback", "signature", "signing secret", "x-hub-signature", "stripe-signature"],
        "reason": "Target hints suggest webhook/callback handling that should be triaged directly.",
    },
    {
        "profile": "api-auth",
        "score": 90,
        "tokens": ["api auth", "api-auth", "swagger", "openapi", "token", "bearer", "jwt", "auth"],
        "reason": "Target hints suggest API authentication and docs surface concerns.",
    },
    {
        "profile": "api",
        "score": 80,
        "tokens": ["api", "/v1", "endpoint", "rest"],
        "reason": "Target hints suggest an API surface.",
    },
    {
        "profile": "webapp-deep",
        "score": 78,
        "tokens": ["deep web", "deeper web", "webapp deep", "active paths"],
        "reason": "Target hints request deeper web triage.",
    },
    {
        "profile": "webapp",
        "score": 70,
        "tokens": ["webapp", "website", "http", "https", "frontend", "landing page"],
        "reason": "Target hints suggest a web application.",
    },
    {
        "profile": "windows-host",
        "score": 75,
        "tokens": ["windows", "rdp", "winrm", "smb", "workstation", "desktop"],
        "reason": "Target hints suggest a Windows host or workstation.",
    },
    {
        "profile": "linux-host",
        "score": 75,
        "tokens": ["linux", "ssh", "ubuntu", "debian", "centos", "server"],
        "reason": "Target hints suggest a Linux host.",
    },
    {
        "profile": "host",
        "score": 50,
        "tokens": ["host", "ip", "server", "machine", "device"],
        "reason": "Target hints suggest a generic host/service surface.",
    },
]


def normalize(text: str) -> str:
    """Normalize text for matching."""
    return re.sub(r"\s+", " ", (text or "").strip().lower())


def get_available_profiles() -> List[str]:
    """Get list of available profile names from filesystem."""
    profiles_dir = get_profiles_dir()
    if not profiles_dir.exists():
        return []
    
    profiles = []
    for f in profiles_dir.glob("*.yaml"):
        if not f.name.startswith("validation-"):  # Skip validation profiles
            profiles.append(f.stem)
    return sorted(profiles)


def recommend(text: str) -> Dict[str, Any]:
    """Recommend profile based on target hint.
    
    Returns dict with profile, score, reason, matched tokens, and alternatives.
    """
    normalized = normalize(text)
    available = set(get_available_profiles())
    
    scored = []
    for rule in PROFILE_RULES:
        # Skip if profile doesn't exist
        if rule["profile"] not in available:
            continue
            
        matched = [token for token in rule["tokens"] if token in normalized]
        if matched:
            scored.append({
                "profile": rule["profile"],
                "score": rule["score"] + len(matched),
                "reason": rule["reason"],
                "matched": matched,
            })
    
    if not scored:
        # Return default with available alternatives
        return {
            "profile": "host",
            "score": 0,
            "reason": "No strong target-type hints matched; defaulting to generic host triage.",
            "matched": [],
            "alternatives": [p for p in ["webapp", "api", "windows-host", "linux-host"] 
                            if p in available][:4],
        }
    
    scored.sort(key=lambda item: item["score"], reverse=True)
    best = scored[0].copy()
    best["alternatives"] = [item["profile"] for item in scored[1:4] 
                           if item["profile"] != best["profile"]]
    return best


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Recommend a quick-scan profile from target hints"
    )
    parser.add_argument("--hint", required=True, help="Free-text description of target")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--list", action="store_true", help="List available profiles")
    args = parser.parse_args()
    
    if args.list:
        profiles = get_available_profiles()
        print("Available profiles:")
        for p in profiles:
            print(f"  - {p}")
        return 0
    
    result = recommend(args.hint)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Recommended profile: {result['profile']}")
        print(f"Reason: {result['reason']}")
        if result.get("matched"):
            print(f"Matched hints: {', '.join(result['matched'])}")
        if result.get("alternatives"):
            print(f"Alternatives: {', '.join(result['alternatives'])}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

### Refactored: generate_quick_report.py

```python
#!/usr/bin/env python3
"""Generate quick-scan reports using shared library."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from quickscan_lib import (
    get_workspace_root,
    get_engagements_dir,
    latest_file,
    safe_read_text,
    safe_write_text,
)

# Severity detection patterns
POSITIVE_SIGNALS = (
    "cve-",
    "missing ",
    "exposed",
    "subdomain:",
    "title:",
    "whatweb:",
    "server banner",
    "banner:",
    "unauthenticated",
    "auth bypass",
    "weak credential",
    "open ",
)

MANAGEMENT_EXPOSURES: Tuple[Tuple[str, str, str, str], ...] = (
    ("3389/tcp", "RDP exposed", "High", "observed"),
    ("445/tcp", "SMB exposed", "High", "observed"),
    ("5985/tcp", "WinRM/HTTP management surface exposed", "High", "observed"),
    ("3306/tcp", "MySQL service exposed", "Medium", "observed"),
)


def severity_for_line(line: str) -> str:
    """Determine severity from line content."""
    text = line.lower()
    
    critical_terms = ["rce", "critical", "exploit available", "unauthenticated"]
    if any(t in text for t in critical_terms):
        return "Critical"
    
    high_terms = ["cve-", "missing hsts", "missing csp"]
    if any(t in text for t in high_terms):
        return "High"
    
    if any(t in text for t in ["smb", "rdp", "winrm"]):
        return "High"
    
    medium_terms = ["banner exposed", "server banner", "title:", "whatweb:", "subdomain:"]
    if any(t in text for t in medium_terms):
        return "Medium"
    
    low_terms = ["info", "observed", "header", "robots"]
    if any(t in text for t in low_terms):
        return "Low"
    
    return "Info"


def is_candidate_line(content: str) -> bool:
    """Check if line contains a candidate finding."""
    text = content.strip().lower()
    if not text:
        return False
    
    ignored_prefixes = (
        "engagement:", "target:", "status:", "generated:",
        "profile:", "mode:", "steps executed:",
        "**next phase:**", "**vector:**", "**reason:**",
    )
    if text.startswith(ignored_prefixes):
        return False
    
    return any(signal in text for signal in POSITIVE_SIGNALS)


def extract_candidate_lines(path: Optional[Path]) -> List[Dict]:
    """Extract candidate findings from summary file."""
    if not path or not path.exists():
        return []
    
    candidates = []
    for line in safe_read_text(path).splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        
        content = line.lstrip("- ").strip()
        if not is_candidate_line(content):
            continue
        
        severity = severity_for_line(content)
        candidates.append({
            "finding": content,
            "severity": severity,
            "confidence": "candidate",
        })
    
    return candidates


def extract_management_exposures(path: Optional[Path]) -> List[Dict]:
    """Extract management service exposures from enum summary."""
    if not path or not path.exists():
        return []
    
    text = safe_read_text(path).lower()
    findings = []
    
    for indicator, finding, severity, confidence in MANAGEMENT_EXPOSURES:
        if indicator.lower() in text:
            findings.append({
                "finding": finding,
                "severity": severity,
                "confidence": confidence,
            })
    
    return findings


def deduplicate_findings(findings: List[Dict]) -> List[Dict]:
    """Remove duplicate findings by (finding, source) key."""
    seen = set()
    unique = []
    
    for item in findings:
        key = (item.get("finding"), item.get("source"))
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    
    return unique


def generate_executive_summary(
    profile: str,
    target: str,
    mode: str,
    counts: Counter,
    total: int
) -> List[str]:
    """Generate executive summary section."""
    lines = ["## Executive Summary", ""]
    
    if total == 0:
        lines.append(
            f"- Quick scan profile `{profile}` ran against `{target}` in `{mode}` mode "
            f"and did not capture notable candidate findings."
        )
        lines.append(
            "- This suggests either a relatively clean exposed surface or limited "
            "visibility from low-impact triage checks."
        )
    else:
        highest = next(
            (s for s in ["Critical", "High", "Medium", "Low", "Info"] if counts.get(s)),
            "Info"
        )
        lines.append(
            f"- Quick scan profile `{profile}` ran against `{target}` in `{mode}` mode "
            f"and captured {total} meaningful candidate observations, "
            f"with highest provisional severity `{highest}`."
        )
        lines.append(
            "- These results are triage-oriented and should be manually validated "
            "before being treated as confirmed vulnerabilities."
        )
    
    lines.append("")
    return lines


def generate_phase_excerpt(path: Optional[Path], title: str) -> List[str]:
    """Generate excerpt from phase summary."""
    lines = [f"## {title}", ""]
    
    if not path or not path.exists():
        lines.append("- No summary generated for this phase.")
    else:
        content = safe_read_text(path)
        excerpt = content.splitlines()[:30]
        lines.extend(excerpt)
    
    lines.append("")
    return lines


def generate_next_action(
    counts: Counter,
    has_recon: bool,
    has_enum: bool,
    has_vuln: bool
) -> List[str]:
    """Generate recommended next action."""
    lines = ["## Recommended Next Action", ""]
    
    if counts.get("Critical") or counts.get("High"):
        lines.append(
            "- Escalate to a full pentest workflow or targeted manual validation "
            "immediately for the highest-risk candidates."
        )
    elif counts.get("Medium"):
        lines.append(
            "- Perform focused manual validation on the medium-severity candidates "
            "and expand service-specific enumeration where relevant."
        )
    elif has_enum or has_vuln:
        lines.append(
            "- Preserve artifacts and consider a deeper follow-up scan if this "
            "target matters operationally."
        )
    else:
        lines.append(
            "- If higher confidence is needed, rerun with a broader profile or "
            "move to a full pentest workflow."
        )
    
    lines.append("")
    return lines


def generate_findings_table(candidates: List[Dict], max_rows: int = 30) -> List[str]:
    """Generate markdown findings table."""
    lines = [
        "## Candidate Findings",
        "",
        "| Severity | Source | Confidence | Finding |",
        "|---|---|---|---|",
    ]
    
    if candidates:
        for item in candidates[:max_rows]:
            safe_finding = item["finding"].replace("|", "\\|")
            lines.append(
                f"| {item['severity']} | {item.get('source', 'unknown')} | "
                f"{item['confidence']} | {safe_finding} |"
            )
    else:
        lines.append(
            "| Info | none | none | "
            "No notable candidate findings captured from current summaries. |"
        )
    
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate quick scan report from phase summaries"
    )
    parser.add_argument("--engagement", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--mode", default="safe")
    parser.add_argument("--steps", default="0", type=str)
    args = parser.parse_args()

    base = get_engagements_dir() / args.engagement
    reporting_dir = base / "quick-scan" / "reporting"
    reporting_dir.mkdir(parents=True, exist_ok=True)
    
    ts = datetime.now().strftime("%Y-%m-%d_%H%M")

    # Find latest summaries
    recon = latest_file(base / "recon", "RECON_SUMMARY_*.md") if (base / "recon").exists() else None
    enum = latest_file(base / "enum", "ENUM_SUMMARY_*.md") if (base / "enum").exists() else None
    vuln = latest_file(base / "vuln", "VULN_SUMMARY_*.md") if (base / "vuln").exists() else None

    # Collect candidates
    candidates = []
    for source_name, summary in [("recon", recon), ("enum", enum), ("vuln", vuln)]:
        for item in extract_candidate_lines(summary):
            item["source"] = source_name
            candidates.append(item)
    
    # Add management exposures
    for item in extract_management_exposures(enum):
        item["source"] = "enum"
        candidates.append(item)

    # Deduplicate and count
    candidates = deduplicate_findings(candidates)
    counts = Counter(item["severity"] for item in candidates)

    # Generate executive summary
    exec_summary_path = reporting_dir / f"EXECUTIVE_SUMMARY_QUICK_SCAN_{ts}.md"
    exec_lines = [
        f"# Executive Summary (Quick Scan) — {args.target}",
        "",
        f"- Profile: `{args.profile}`",
        f"- Mode: `{args.mode}`",
        f"- Engagement: `{args.engagement}`",
        f"- Steps executed: `{args.steps}`",
        f"- Generated: `{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')}`",
        "",
        "## Severity Snapshot",
        f"- Critical: {counts.get('Critical', 0)}",
        f"- High: {counts.get('High', 0)}",
        f"- Medium: {counts.get('Medium', 0)}",
        f"- Low: {counts.get('Low', 0)}",
        f"- Info: {counts.get('Info', 0)}",
        "",
        "## Assessment Note",
        "- This is a rapid triage output presented in pentest-report style.",
        "- Review candidate findings manually before treating them as confirmed vulnerabilities.",
        "",
    ]
    safe_write_text(exec_summary_path, "\n".join(exec_lines), backup=False)

    # Generate full report
    report_path = reporting_dir / f"REPORT_QUICK_SCAN_{ts}.md"
    report_lines = [
        f"# Penetration Test Report (Quick Scan) — {args.target}",
        "",
        f"- Profile: `{args.profile}`",
        f"- Mode: `{args.mode}`",
        f"- Engagement: `{args.engagement}`",
        f"- Steps executed: `{args.steps}`",
        f"- Generated: `{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')}`",
        "",
        "## Scope",
        "- Rapid triage / hygiene / exposure assessment",
        "- Safe or low-impact checks where possible",
        "- This is not a substitute for a full pentest",
        "",
    ]
    
    report_lines.extend(generate_executive_summary(
        args.profile, args.target, args.mode, counts, len(candidates)
    ))
    
    report_lines.extend([
        "## Severity Buckets",
        "",
        f"- Critical: {counts.get('Critical', 0)}",
        f"- High: {counts.get('High', 0)}",
        f"- Medium: {counts.get('Medium', 0)}",
        f"- Low: {counts.get('Low', 0)}",
        f"- Info: {counts.get('Info', 0)}",
        "",
    ])
    
    report_lines.extend(generate_findings_table(candidates))
    report_lines.append("")
    
    report_lines.extend([
        "## What Needs Manual Validation",
        "",
    ])
    if candidates:
        for item in candidates[:12]:
            report_lines.append(f"- Validate: {item['finding']}")
    else:
        report_lines.append(
            "- Validate whether the limited findings are due to clean posture, "
            "low-impact mode, or missing service visibility."
        )
    report_lines.append("")
    
    report_lines.extend(generate_next_action(
        counts, recon is not None, enum is not None, vuln is not None
    ))
    report_lines.extend(generate_phase_excerpt(recon, "Recon Summary"))
    report_lines.extend(generate_phase_excerpt(enum, "Enumeration Summary"))
    report_lines.extend(generate_phase_excerpt(vuln, "Vulnerability Summary"))
    
    report_lines.extend([
        "## Recommendations",
        "",
        "- Validate candidate findings manually before escalation.",
        "- Escalate to a full pentest workflow if high-risk candidates are found.",
        "- Preserve engagement artifacts for follow-up analysis.",
        "",
    ])
    
    safe_write_text(report_path, "\n".join(report_lines), backup=False)

    print(exec_summary_path)
    print(report_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

---

## Backward Compatibility Strategy

1. **Profile YAMLs:** No changes - existing profiles work unchanged
2. **API Surface:** Legacy imports via `load_quick_manifest = load_manifest` alias
3. **Command-line:** All existing arguments preserved, new ones are optional
4. **Output Format:** Report structure unchanged

## Testing Strategy

1. **Unit tests** for `quickscan_lib.py` functions
2. **Integration tests** with sample profiles
3. **Dry-run mode** to validate without side effects
4. **Backward compatibility tests** against existing engagements

## Migration Path

1. Create `quickscan_lib.py` alongside existing code
2. Migrate one script at a time (runner first, then reports)
3. Keep old implementations as `.legacy.py` backups initially
4. Remove backups after validation period
