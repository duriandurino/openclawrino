"""Shared utilities for quick-scan framework."""
from __future__ import annotations

import functools
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional, Dict, Any, Tuple
from datetime import datetime

# Try to import yaml, fallback to simple parser if unavailable
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

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
    
    Searches upward from current file for marker files.
    """
    global _WORKSPACE_ROOT
    if _WORKSPACE_ROOT is not None:
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
    """Validate that a script exists and is readable."""
    if not script_path.exists():
        raise StepExecutionError(f"Script not found: {script_path}")


def latest_file(directory: Path, pattern: str) -> Optional[Path]:
    """Find most recently modified file matching pattern.
    
    Args:
        directory: Directory to search
        pattern: Glob pattern (e.g., "RECON_SUMMARY_*.md")
    
    Returns:
        Path to latest file or None if no matches
    """
    if not directory or not directory.exists():
        return None
    
    matches = sorted(directory.glob(pattern), key=lambda p: p.stat().st_mtime)
    return matches[-1] if matches else None


def safe_read_text(path: Path, default: str = "") -> str:
    """Read file with error handling."""
    if not path or not path.exists():
        return default
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except (IOError, OSError) as e:
        return default


def safe_write_text(path: Path, content: str, backup: bool = False) -> None:
    """Write file atomically with optional backup."""
    path.parent.mkdir(parents=True, exist_ok=True)
    
    if backup and path.exists():
        backup_path = path.with_suffix(f".backup.{datetime.now():%Y%m%d_%H%M%S}{path.suffix}")
        try:
            path.rename(backup_path)
        except OSError:
            pass  # Continue even if backup fails
    
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
        try:
            os.unlink(temp.name)
        except OSError:
            pass
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


def _parse_yaml_simple(text: str) -> Dict[str, Any]:
    """Simple YAML parser fallback when PyYAML is not available.
    
    Handles basic quick-scan manifest format.
    """
    data: Dict[str, Any] = {"steps": []}
    current_step: Optional[Dict[str, Any]] = None
    
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        
        if not stripped or stripped.startswith("#"):
            continue
        
        # Top-level keys
        if not line.startswith(" ") and ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip().strip('"')
            
            if key == "steps":
                data["steps"] = []
                current_step = None
            else:
                data[key] = value
            continue
        
        # Steps list
        if stripped.startswith("-"):
            current_step = {}
            data.setdefault("steps", []).append(current_step)
            entry = stripped[1:].strip()
            if ":" in entry:
                key, value = entry.split(":", 1)
                current_step[key.strip()] = value.strip().strip('"')
            continue
        
        # Step attributes
        if current_step is not None and ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            
            # Handle args array
            if key == "args" and value.startswith("[") and value.endswith("]"):
                items = [item.strip().strip('"') for item in value[1:-1].split(",") if item.strip()]
                current_step["args"] = items
            else:
                current_step[key] = value.strip('"')
    
    return data


def load_manifest(path: Path) -> Manifest:
    """Load and validate a quick-scan manifest.
    
    Uses PyYAML if available, otherwise uses simple parser.
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
    except IOError as e:
        raise ManifestError(f"Cannot read manifest {path}: {e}")
    
    # Parse YAML
    if HAS_YAML:
        try:
            data = yaml.safe_load(text)
        except Exception as e:
            raise ManifestError(f"Invalid YAML in {path}: {e}")
    else:
        data = _parse_yaml_simple(text)
    
    if not isinstance(data, dict):
        raise ManifestError(f"Manifest must be a YAML object: {path}")
    
    # Validate required fields
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
        
        # Parse args - handle both list and string formats
        args = step_data.get('args', [])
        if isinstance(args, str):
            args = [args]
        
        steps.append(ManifestStep(
            phase=step_data.get('phase', 'unknown'),
            script=step_data['script'],
            args=args,
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
    if candidate.exists() and candidate.suffix in ('.yaml', '.yml'):
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
    
    def substitute_args(self, args: List[str], context: Dict[str, str]) -> List[str]:
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
    
    def run_step(self, step: ManifestStep, context: Dict[str, str], index: int) -> StepResult:
        """Execute a single step."""
        # Resolve script path
        script_path = get_workspace_root() / "scripts" / step.script
        
        # Pre-flight validation
        validate_script_exists(script_path)
        
        # Build command
        args = self.substitute_args(step.args, context)
        cmd = [str(script_path)] + [a for a in args if a]
        
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
load_quick_manifest = load_manifest
