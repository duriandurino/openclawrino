#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def latest_file(directory: Path, pattern: str) -> Path | None:
    matches = sorted(directory.glob(pattern), key=lambda p: p.stat().st_mtime)
    return matches[-1] if matches else None


def markdown_to_html(markdown_text: str, title: str) -> str:
    lines = markdown_text.splitlines()
    body = []
    in_list = False
    in_table = False

    def close_blocks():
        nonlocal in_list, in_table
        if in_list:
            body.append("</ul>")
            in_list = False
        if in_table:
            body.append("</table>")
            in_table = False

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            close_blocks()
            continue
        if line.startswith("# "):
            close_blocks()
            body.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            close_blocks()
            body.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("### "):
            close_blocks()
            body.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("|") and line.endswith("|"):
            cells = [html.escape(cell.strip()) for cell in line.strip("|").split("|")]
            if all(set(cell) <= {"-", ":"} for cell in cells):
                continue
            if not in_table:
                close_blocks()
                body.append("<table border='1' cellspacing='0' cellpadding='6'>")
                in_table = True
            tag = "th" if not any("<td" in row for row in body[-3:]) else "td"
            body.append("<tr>" + "".join(f"<{tag}>{cell}</{tag}>" for cell in cells) + "</tr>")
        elif line.startswith("- "):
            if not in_list:
                close_blocks()
                body.append("<ul>")
                in_list = True
            body.append(f"<li>{html.escape(line[2:])}</li>")
        else:
            close_blocks()
            body.append(f"<p>{html.escape(line)}</p>")

    close_blocks()
    return f"""<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 1000px; margin: 2rem auto; line-height: 1.5; }}
    h1, h2, h3 {{ color: #1f2937; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
    th {{ background: #f3f4f6; }}
    td, th {{ vertical-align: top; }}
    code {{ background: #f3f4f6; padding: 0.1rem 0.3rem; border-radius: 4px; }}
  </style>
</head>
<body>
{''.join(body)}
</body>
</html>
"""


def export_pdf_if_possible(markdown_path: Path, pdf_path: Path) -> bool:
    pandoc = shutil.which("pandoc")
    if pandoc:
        result = subprocess.run([pandoc, str(markdown_path), "-o", str(pdf_path)], capture_output=True, text=True)
        return result.returncode == 0 and pdf_path.exists()
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Export the latest quick scan report into shareable formats")
    parser.add_argument("--engagement", required=True)
    parser.add_argument("--report", default="", help="Explicit markdown report path")
    args = parser.parse_args()

    reporting_dir = ROOT / "engagements" / args.engagement / "quick-scan" / "reporting"
    if not reporting_dir.exists():
        raise SystemExit(f"reporting directory not found: {reporting_dir}")

    report_path = Path(args.report) if args.report else latest_file(reporting_dir, "QUICK_SCAN_REPORT_*.md")
    if not report_path or not report_path.exists():
        raise SystemExit("no quick scan report markdown found")

    text = report_path.read_text(encoding="utf-8", errors="ignore")
    stem = report_path.stem
    txt_path = reporting_dir / f"{stem}.txt"
    html_path = reporting_dir / f"{stem}.html"
    pdf_path = reporting_dir / f"{stem}.pdf"

    txt_path.write_text(text, encoding="utf-8")
    html_path.write_text(markdown_to_html(text, stem), encoding="utf-8")

    pdf_created = export_pdf_if_possible(report_path, pdf_path)

    print(txt_path)
    print(html_path)
    if pdf_created:
        print(pdf_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
