#!/usr/bin/env python3
"""
Sentence-Style Passphrase Candidate Miner

Mines workspace artifacts (pentest_engagement zip contents, NTV/Player research)
for likely sentence-style passphrase candidates for setup.enc.

Minimal dependencies: Python 3 stdlib only.

Usage:
    python3 mine_sentence_passphrases.py [--output DIR]
"""

import os
import re
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Set

@dataclass
class Candidate:
    phrase: str
    source: str
    confidence: float
    notes: str = ""

    def __lt__(self, other):
        return self.confidence > other.confidence

def find_text_files(root: Path, patterns: List[str] = None, max_depth: int = 4) -> List[Path]:
    """Recursively find text files under root, limited depth."""
    default_patterns = ['*.md', '*.txt', '*.py', '*.sh']
    search_patterns = patterns if patterns is not None else default_patterns
    files = []
    for p in search_patterns:
        files.extend(root.rglob(p))
    return sorted(set(files))[:200]

def extract_quoted_phrases(content: str) -> List[str]:
    """Extract quoted strings that could be passphrases."""
    phrases = []
    # Double-quoted phrases
    phrases.extend(re.findall(r'"([^"]{8,80})"', content))
    # Single-quoted phrases
    phrases.extend(re.findall(r"'([^']{8,80})'", content))
    # Backtick-quoted
    phrases.extend(re.findall(r'`([^`]{8,80})`', content))
    return [p.strip() for p in phrases if len(p.strip()) >= 8 and ' ' in p]

def extract_sentence_patterns(content: str) -> List[str]:
    """Extract sentence-like patterns from content."""
    sentences = []
    # Look for lines that look like instructions, commands, or memorable phrases
    patterns = [
        r'(?:enter|type|use|enter your|enter the|use password:?\s*)\S+',
        r'(?:password|passphrase|passwd|pwd|secret|key)[:\s]+[\w\d\s\-_]{6,40}',
        r'\b(?:install|setup|deploy|configure)[:\s]+[\w\s\d\-_]{8,50}',
        r'\b(?:the |a |this )?[\w]{4,15}[\s]+[\w]{4,15}[\s]+[\w\d]{2,10}\b',
    ]
    for p in patterns:
        matches = re.findall(p, content, re.IGNORECASE)
        sentences.extend([m.strip() for m in matches if len(m.strip()) >= 10])
    return sentences

def extract_serial_embedded(content: str) -> List[str]:
    """Find serial/CID values that could be embedded in phrases."""
    phrases = []
    # Pi serial format: 16 hex chars
    serials = re.findall(r'\b([0-9a-fA-F]{16})\b', content)
    # CID format: 32 hex chars
    cids = re.findall(r'\b([0-9a-fA-F]{32})\b', content)
    
    for serial in serials[:2]:  # Limit to avoid too many combos
        # Sentence templates with serial embedded
        phrases.extend([
            f"the serial is {serial}",
            f"serial {serial}",
            f"device {serial}",
            f"pi serial {serial}",
            f"{serial}",
            f"password {serial}",
            f"key {serial}",
            f"nctv serial {serial}",
            f"ncompass player serial {serial}",
            f"player serial {serial}",
        ])
    return [p.lower() for p in phrases]

def extract_mnemonic_phrases(content: str) -> List[str]:
    """Extract memorable phrase patterns."""
    phrases = []
    # Known business/project keywords
    keywords = [
        'ncompass', 'nctv', 'ntv360', 'nctv360', 'player', 'playerv2', 
        'arjay', 'darkhorse', 'bryan', 'pulse', 'compass', 'tv', 'pi',
        'raspberry', 'setup', 'install', 'deploy', 'hardware', 'secure'
    ]
    # Find sentences containing these keywords
    lines = content.split('\n')
    for line in lines:
        line_lower = line.lower()
        if any(k in line_lower for k in keywords) and 15 < len(line) < 120:
            # Clean markdown artifacts
            cleaned = re.sub(r'[#*`\[\]]', '', line).strip()
            if len(cleaned) >= 10 and ' ' in cleaned:
                phrases.append(cleaned)
    return phrases

def extract_config_patterns(content: str) -> List[str]:
    """Extract configuration/prompt-like strings."""
    phrases = []
    # Look for = assignments that might be prompts
    assignments = re.findall(r'(?:password|passphrase|secret|key)\s*=\s*["\']?([^"\'\n]+)["\']?', content, re.IGNORECASE)
    for a in assignments:
        a = a.strip()
        if len(a) >= 8:
            phrases.append(a)
    # Look for environment variable patterns
    env_assigns = re.findall(r'(?:PASSPHRASE|PASSWORD|SECRET|KEY)[=\s]+([^\s\n]{8,60})', content, re.IGNORECASE)
    phrases.extend([a.strip() for a in env_assigns if len(a.strip()) >= 8])
    return phrases

def extract_number_patterns(content: str) -> List[str]:
    """Extract sentences with embedded numbers that could be dates/versions."""
    phrases = []
    # Sentence with year patterns
    year_patterns = re.findall(r'[\w\s]{5,50}(?:202[0-6]|20\d{2})[\w\s]{0,20}', content)
    for p in year_patterns:
        if 12 < len(p) < 80:
            phrases.append(p.strip())
    # Sentence with version patterns
    ver_patterns = re.findall(r'[\w\s]{5,30}(?:v\d[\.\d]*|\d+\.\d+)[\w\s]{0,20}', content)
    phrases.extend([p.strip() for p in ver_patterns if 12 < len(p) < 80])
    return phrases

def score_candidate(phrase: str, source: str, all_sources: List[str]) -> float:
    """Score a candidate phrase by confidence."""
    score = 0.5  # Base
    
    source_lower = source.lower()
    phrase_lower = phrase.lower()
    
    # Source-based scoring
    if 'hardware_lock' in source_lower:
        score += 0.15
    if 'turnover' in source_lower:
        score += 0.1
    if 'installer' in source_lower:
        score += 0.1
    if 'setup' in source_lower:
        score += 0.05
    
    # Content-based scoring
    # Contains serial/CID pattern
    if re.search(r'[0-9a-f]{16}|[0-9a-f]{32}', phrase_lower):
        score += 0.15
    # Contains known keywords
    keywords = ['ncompass', 'nctv', 'player', 'serial', 'password', 'secret', 'key', 'pi']
    kw_count = sum(1 for k in keywords if k in phrase_lower)
    score += min(kw_count * 0.03, 0.12)
    
    # Sentence structure indicators
    if re.search(r'\b(?:the|this|enter|type|use)\b', phrase_lower):
        score += 0.08
    if re.search(r'\b(?:is|are|was|were)\b', phrase_lower):
        score += 0.05
    
    # Length considerations (too short less likely, too long too complex)
    if 15 <= len(phrase) <= 40:
        score += 0.1
    elif 41 <= len(phrase) <= 60:
        score += 0.05
    
    # Penalize markdown artifacts
    if any(c in phrase for c in ['[', ']', '#', '*`']):
        score -= 0.2
    
    return min(max(score, 0.1), 0.95)

def mine_sources(search_root: Path) -> List[Candidate]:
    """Mine all relevant sources for passphrase candidates."""
    candidates: Set[str] = set()
    results: List[Candidate] = []
    
    # Define source directories to mine
    source_dirs = [
        search_root / 'research' / 'ntv-hardware-lock',
        search_root / 'engagements' / 'playerv2-setup-enc-sentence' / 'recon',
        search_root / 'engagements' / 'player-vault',
        search_root / 'engagements' / 'playerv2',
        search_root / 'engagements' / 'player-network',
    ]
    
    all_files = []
    for d in source_dirs:
        if d.exists():
            all_files.extend(find_text_files(d))
    
    for filepath in all_files:
        # Skip huge files (like rockyou wordlist)
        try:
            if filepath.stat().st_size > 5_000_000:  # 5MB limit
                continue
            content = filepath.read_text(errors='ignore')
        except Exception:
            continue
        
        source = str(filepath.relative_to(search_root))
        
        # Extract various candidate types
        phrases = (
            extract_quoted_phrases(content) +
            extract_sentence_patterns(content) +
            extract_mnemonic_phrases(content) +
            extract_config_patterns(content) +
            extract_number_patterns(content) +
            extract_serial_embedded(content)
        )
        
        for phrase in phrases:
            phrase = phrase.strip()
            # Normalize and deduplicate
            normalized = re.sub(r'\s+', ' ', phrase)
            if len(normalized) >= 8 and normalized not in candidates:
                candidates.add(normalized)
                confidence = score_candidate(normalized, source, [str(f) for f in all_files])
                results.append(Candidate(
                    phrase=normalized,
                    source=source,
                    confidence=confidence,
                    notes=""
                ))
    
    # Add high-priority serial-based candidates
    known_serials = [
        'ffb6d42807368154',
        '10000000d58ec40c',
    ]
    
    # Generate serial + keyword combos as potential phrases
    keywords = ['nctv', 'ncompass', 'player', 'darkhorse', 'setup', 'install', 'pi']
    for serial in known_serials:
        for kw in keywords:
            phrase = f"{kw}{serial}"
            if phrase not in candidates:
                candidates.add(phrase)
                results.append(Candidate(
                    phrase=phrase,
                    source="research/ntv-hardware-lock (serial-derived)",
                    confidence=0.55,  # Lower than sentence-based
                    notes=f"Serial {serial} + keyword {kw}"
                ))
    
    # Sort by confidence
    results.sort()
    return results

def main():
    parser = argparse.ArgumentParser(description='Mine sentence-style passphrase candidates')
    parser.add_argument('--output', default='.', help='Output directory')
    parser.add_argument('--workspace', default='/home/dukali/.openclaw/workspace', help='Workspace root')
    args = parser.parse_args()
    
    workspace = Path(args.workspace)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Mining sources under: {workspace}")
    candidates = mine_sources(workspace)
    
    # Write ranked candidates
    output_file = output_dir / 'PASSPHRASE_CANDIDATES_SENTENCE.md'
    
    with open(output_file, 'w') as f:
        f.write("# Ranked Sentence-Style Passphrase Candidates\n\n")
        f.write(f"**Generated:** 2026-04-08  \n")
        f.write(f"**Target:** setup.enc (PlayerV2 installer)  \n")
        f.write(f"**Total Candidates:** {len(candidates)}  \n\n")
        
        f.write("---\n\n")
        f.write("## Methodology\n\n")
        f.write("- Mined NTV Phoenix/Hardware-Lock research docs\n")
        f.write("- Mined Player/Vault engagement files\n")
        f.write("- Extracted quoted phrases, instructions, configuration values\n")
        f.write("- Embedded known Pi serials into phrase templates\n")
        f.write("- Scored by source relevance and phrase structure\n\n")
        
        f.write("---\n\n")
        f.write("## Top Candidates (Confidence >= 0.5)\n\n")
        f.write("| Rank | Confidence | Candidate | Source |\n")
        f.write("|------|------------|-----------|--------|\n")
        
        rank = 1
        for c in candidates[:100]:
            if c.confidence >= 0.5:
                f.write(f"| {rank} | {c.confidence:.2f} | `{c.phrase[:60]}{'...' if len(c.phrase) > 60 else ''}` | {c.source[:50]} |\n")
                rank += 1
        
        f.write("\n---\n\n")
        f.write("## All Candidates (Top 200)\n\n")
        f.write("```\n")
        for i, c in enumerate(candidates[:200], 1):
            f.write(f"{i:3}. [{c.confidence:.2f}] {c.phrase}\n")
        f.write("```\n\n")
        
        f.write("---\n\n")
        f.write("## High-Priority Serial Candidates\n\n")
        f.write("Known Pi serials embedded in phrases:\n\n")
        for c in candidates:
            if c.notes and 'serial' in c.notes.lower():
                f.write(f"- `{c.phrase}` (confidence: {c.confidence:.2f})\n")
    
    print(f"Output written to: {output_file}")
    print(f"Total candidates found: {len(candidates)}")
    
    # Also output as simple text list for piping to crackers
    simple_file = output_dir / 'passphrase_candidates.txt'
    with open(simple_file, 'w') as f:
        for c in candidates[:500]:
            f.write(f"{c.phrase}\n")
    print(f"Simple list written to: {simple_file}")

if __name__ == '__main__':
    main()
