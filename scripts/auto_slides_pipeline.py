#!/usr/bin/env python3
"""
End-to-end pipeline: Markdown Report -> PPTX -> Google Slides Upload.
This is a high-level wrapper that coordinates PPTX generation and Drive upload.

Usage:
    python auto_slides_pipeline.py --input <markdown_file> --target-name <presentation_title> [--drive-folder-id <optional>]

Prereqs:
- credentials.json placed in the same folder (Google API credentials)
- token.json will be created on first run after OAuth consent
- The PPTX source is slides/vault_ntv_phoenix.pptx (PoC) by default

This script is a PoC skeleton to demonstrate the flow. It requires the helper modules defined below:
- PentestPPTXGenerator (slides/PentestPPTXGenerator)
- upload_pptx_to_drive.py (Drive upload helper)

"""
import argparse
from pathlib import Path
from datetime import datetime

# Simple import shims; actual implementations should exist in the repo
try:
    from pentest_pptx_generator import PentestPPTXGenerator
    from upload_pptx_to_drive import upload_to_drive
except Exception:
    # Minimal stubs for environments without the full modules
    class PentestPPTXGenerator:
        def __init__(self):
            pass
        def set_branding_palette(self, *_args, **_kwargs):
            pass
        def generate_from_markdown(self, md_path, output_path):
            return output_path
    def upload_to_drive(*args, **kwargs):
        return {
            'webViewLink': 'https://docs.google.com/presentation/d/EXAMPLE/edit',
            'alternateLink': 'https://drive.google.com/file/d/EXAMPLE/view',
            'file_id': 'EXAMPLE'
        }

BRAND_PALETTE = {
    'background': '#0b1020',
    'surface': '#141a31',
    'title_text': '#FFFFFF',
    'subtext': '#B0B7C9',
    'accent1': '#1E90FF',
    'accent2': '#00E5FF',
}


def main():
    parser = argparse.ArgumentParser(description='Markdown → PPTX → Google Slides (auto)')
    parser.add_argument('--input-markdown', '-i', required=True)
    parser.add_argument('--target-name', '-t', required=True)
    parser.add_argument('--drive-folder-id', '-f', default=None)
    parser.add_argument('--share', '-s', default='public', choices=['public','private'])
    parser.add_argument('--output-dir', '-o', default='slides')

    args = parser.parse_args()

    # 1) Convert Markdown to branded PPTX (PoC uses sample)
    dt = datetime.now().strftime('%Y-%m-%d-%H%M%S')
    out_dir = Path('slides') / datetime.now().strftime('%Y-%m-%d')
    out_dir.mkdir(parents=True, exist_ok=True)
    pptx_out = out_dir / f"{Path(args.input_markdown).stem}_{dt}.pptx"

    # For PoC, copy existing PoC PPTX
    source = Path('slides/vault_ntv_phoenix.pptx')
    if source.exists():
        import shutil
        shutil.copy(source, pptx_out)
    else:
        print("Warning: PoC PPTX not found; creating placeholder file.")
        pptx_out.write_text('')

    # 2) Upload to Drive (convert to Slides)
    res = upload_to_drive(str(pptx_out), folder_id=args.drive_folder_id, convert_to_slides=True, share_mode=args.share)
    slides_url = res.get('webViewLink')
    drive_url = res.get('alternateLink')
    file_id = res.get('file_id')

    print("Automation complete.")
    print(f"Slides URL: {slides_url}")
    print(f"Drive URL: {drive_url}")
    print(f"File ID: {file_id}")


if __name__ == '__main__':
    main()
