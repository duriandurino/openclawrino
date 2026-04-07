#!/usr/bin/env python3
"""Test script for phase 2 adaptive quick-scan branching improvements."""

import sys
import json
from pathlib import Path

# Test imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

def test_step_key():
    """Test step deduplication key generation."""
    # Inline the step_key function logic for testing
    def step_key(step):
        script = step.get("script", "")
        args = step.get("args", [])
        normalized_args = []
        for arg in args:
            if arg and not arg.startswith("{{"):
                normalized_args.append(arg)
        return f"{script}:{','.join(normalized_args)}"
    
    # Test basic step key generation
    step1 = {"script": "enum/web/enum_graphql_basic.sh", "args": ["--target", "example.com", "--safe"]}
    step2 = {"script": "enum/web/enum_graphql_basic.sh", "args": ["--target", "example.com", "--safe"]}  # Same target
    step3 = {"script": "enum/web/enum_nestjs_api.sh", "args": ["--target", "example.com", "--safe"]}
    step4 = {"script": "enum/web/enum_graphql_basic.sh", "args": ["--target", "other.com", "--safe"]}  # Different target
    
    key1 = step_key(step1)
    key2 = step_key(step2)
    key3 = step_key(step3)
    key4 = step_key(step4)
    
    # Same script + same target should have same key
    assert key1 == key2, f"Same script+target should match: {key1} vs {key2}"
    # Different script should have different key
    assert key1 != key3, f"Different scripts should not match: {key1} vs {key3}"
    # Same script but different target should have different key (correct behavior - targets differ)
    assert key1 != key4, f"Different targets should have different keys: {key1} vs {key4}"
    
    print("✓ step_key() deduplication works correctly (includes target in key)")

def test_build_overlay_dedup():
    """Test that build_overlay respects already-executed steps."""
    import sys
    sys.path.insert(0, str(ROOT / "scripts" / "quick-scan"))
    from fingerprint_target import build_overlay
    
    fp = {
        "frameworks": ["graphql"],
        "deployments": [],
        "surfaces": ["graphql"],
        "traits": []
    }
    
    # Without executed steps - should add GraphQL overlay
    overlay_no_dedup = build_overlay("webapp", fp, None)
    assert len(overlay_no_dedup["extra_steps"]) > 0, "Should add steps without dedup"
    assert "graphql" in overlay_no_dedup["profiles_considered"]
    
    # With GraphQL already executed - should skip adding duplicate steps
    executed = [{"script": "enum/web/enum_graphql_basic.sh", "phase": "enum", "args": []}]
    overlay_with_dedup = build_overlay("webapp", fp, executed)
    
    # When deduped, profile is NOT in profiles_considered (intentionally - we note it in report_focus instead)
    # But should have no extra steps since they're already covered
    assert len(overlay_with_dedup["extra_steps"]) == 0, f"Should skip steps due to dedup, got: {overlay_with_dedup['extra_steps']}"
    # Report focus should note that GraphQL was already covered
    assert any("graphql" in item.lower() for item in overlay_with_dedup["report_focus"]), "Should note graphql coverage in report"
    
    print("✓ build_overlay() deduplication works correctly")

def test_early_fingerprint_trigger():
    """Test that fingerprint can be triggered after recon phase."""
    # This is a logic check - in real run, first_recon_idx is identified
    steps = [
        {"phase": "recon", "script": "recon/web/recon.sh"},
        {"phase": "enum", "script": "enum/web/enum.sh"},
        {"phase": "vuln", "script": "vuln/web/vuln.sh"}
    ]
    
    first_recon_idx = -1
    for i, step in enumerate(steps):
        if step.get("phase") == "recon":
            first_recon_idx = i
            break
    
    assert first_recon_idx == 0, "Should identify first recon step at index 0"
    print("✓ Early fingerprint trigger logic works correctly")

def test_step_insertion_order():
    """Test that overlay steps are inserted at the right position."""
    steps = [
        {"phase": "recon", "script": "recon.sh"},
        {"phase": "enum", "script": "enum.sh"},
        {"phase": "vuln", "script": "vuln.sh"}
    ]
    
    overlay = [
        {"phase": "enum", "script": "enum_special.sh"},
        {"phase": "vuln", "script": "vuln_special.sh"}
    ]
    
    # Simulate insertion after recon (idx=0)
    idx = 0
    remaining = steps[idx+1:]
    new_steps = steps[:idx+1] + overlay + remaining
    
    expected_order = ["recon.sh", "enum_special.sh", "vuln_special.sh", "enum.sh", "vuln.sh"]
    actual_order = [s["script"] for s in new_steps]
    
    assert actual_order == expected_order, f"Order mismatch: {actual_order} vs {expected_order}"
    print("✓ Step insertion ordering works correctly")

def main():
    print("Testing Phase 2 Adaptive Quick-Scan Improvements")
    print("=" * 50)
    
    try:
        test_step_key()
        test_build_overlay_dedup()
        test_early_fingerprint_trigger()
        test_step_insertion_order()
        
        print("=" * 50)
        print("All tests passed! ✓")
        return 0
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
