#!/usr/bin/env python3
"""
Upload a PPTX to Google Drive and convert to Google Slides.
This script uses the Google Drive / Slides API and performs the following:
- Upload a PPTX as a Google Slides presentation
- Optionally share with anyone with the link
- Return the Slides URL (webViewLink) and Drive link (alternateLink)

First-run flow:
- You will be prompted to authorize via a browser. This creates token.json.

Dependencies (install if missing):
- google-api-python-client
- google-auth-httplib2
- google-auth-oauthlib

Notes:
- If credentials.json is not found in the same directory, the script will raise an error.
"""

import os
from pathlib import Path
from typing import Optional

# Google API imports (optional for offline testing)
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google.auth.transport.requests import Request
except Exception as e:
    Credentials = None
    InstalledAppFlow = None
    build = None
    MediaFileUpload = None
    Request = None

SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive'
]

CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'token.json'

# Helpers

def ensure_dependencies():
    # This function is a no-op at runtime, but left to document intent.
    if Credentials is None or build is None:
        raise RuntimeError('Google API client libraries not available. Install via pip.')


def get_credentials(credentials_path: str = CREDENTIALS_FILE,
                    token_path: str = TOKEN_FILE):
    """Return a valid Credentials object, prompting for consent if needed."""
    if not Path(credentials_path).exists():
        raise FileNotFoundError(f"Credentials file not found: {credentials_path}")

    creds = None
    token_file = Path(token_path)
    if token_file.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
        except Exception:
            creds = None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token and Request is not None:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    return creds


def upload_pptx_to_drive(file_path: str,
                         file_title: Optional[str] = None,
                         share_public: bool = True) -> dict:
    """Upload a PPTX to Drive as a Google Slides presentation and optionally share."""
    if not Path(file_path).exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ensure_dependencies()
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)

    mime_type_pptx = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    metadata = {
        'name': file_title or Path(file_path).stem,
        'mimeType': 'application/vnd.google-apps.presentation'
    }
    media = MediaFileUpload(file_path, mimetype=mime_type_pptx, resumable=True)

    drive_file = service.files().create(body=metadata,
                                      media_body=media,
                                      fields='id,webViewLink,alternateLink').execute()
    file_id = drive_file.get('id')

    # Optionally set share permissions to anyone with the link
    if share_public and file_id:
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        try:
            service.permissions().create(fileId=file_id, body=permission).execute()
        except Exception:
            # Non-fatal; permissions may already exist or be restricted
            pass

    return {
        'id': file_id,
        'webViewLink': drive_file.get('webViewLink'),
        'alternateLink': drive_file.get('alternateLink')
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Upload PPTX to Drive and convert to Slides.')
    parser.add_argument('pptx', help='Path to the PPTX file to upload')
    parser.add_argument('--title', help='Optional title for the Slides presentation')
    parser.add_argument('--share', action='store_true', help='Share with anyone with the link')
    parser.add_argument('--no-share', dest='share', action='store_false', help='Do not set public sharing')
    parser.set_defaults(share=True)
    args = parser.parse_args()

    try:
        result = upload_pptx_to_drive(args.pptx, file_title=args.title, share_public=args.share)
        print("LINKS:")
        print(f"Drive file ID: {result['id']}")
        print(f"Google Slides URL: {result['webViewLink']}")
        print(f"Drive URL: {result['alternateLink']}")
    except Exception as e:
        print(f"ERROR: {e}")
        raise

if __name__ == '__main__':
    main()
