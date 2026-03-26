#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
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
    saw_table_header = False

    def close_blocks():
        nonlocal in_list, in_table, saw_table_header
        if in_list:
            body.append("</ul>")
            in_list = False
        if in_table:
            body.append("</table>")
            in_table = False
            saw_table_header = False

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
            tag = "th" if not saw_table_header else "td"
            body.append("<tr>" + "".join(f"<{tag}>{cell}</{tag}>" for cell in cells) + "</tr>")
            saw_table_header = True
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


def export_one(markdown_path: Path) -> list[Path]:
    text = markdown_path.read_text(encoding="utf-8", errors="ignore")
    stem = markdown_path.stem
    txt_path = markdown_path.with_suffix(".txt")
    html_path = markdown_path.with_suffix(".html")
    pdf_path = markdown_path.with_suffix(".pdf")

    txt_path.write_text(text, encoding="utf-8")
    html_path.write_text(markdown_to_html(text, stem), encoding="utf-8")

    outputs = [txt_path, html_path]
    if export_pdf_if_possible(markdown_path, pdf_path):
        outputs.append(pdf_path)
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description="Export the latest quick scan report into shareable formats")
    parser.add_argument("--engagement", required=True)
    parser.add_argument("--report", default="", help="Explicit markdown report path")
    args = parser.parse_args()

    reporting_dir = ROOT / "engagements" / args.engagement / "quick-scan" / "reporting"
    if not reporting_dir.exists():
        raise SystemExit(f"reporting directory not found: {reporting_dir}")

    report_path = Path(args.report) if args.report else latest_file(reporting_dir, "REPORT_QUICK_SCAN_*.md")
    if not report_path or not report_path.exists():
        raise SystemExit("no quick scan report markdown found")

    summary_path = latest_file(reporting_dir, "EXECUTIVE_SUMMARY_QUICK_SCAN_*.md")

    outputs = []
    if summary_path and summary_path.exists():
        outputs.extend(export_one(summary_path))
    outputs.extend(export_one(report_path))

    for path in outputs:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
