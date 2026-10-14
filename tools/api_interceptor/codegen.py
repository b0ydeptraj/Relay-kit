import json
import shlex
from typing import Dict
from .models import CapturedRequest


def generate_python_script(req: CapturedRequest) -> str:
    """Generate clean, standalone Python requests script from a CapturedRequest."""
    filtered_headers = {}
    for k, v in req.headers.items():
        k_low = k.lower()
        # Filter out transport-level headers that requests handles automatically
        if k_low not in ("content-length", "host", "connection", "accept-encoding"):
            filtered_headers[k] = v

    headers_str = json.dumps(filtered_headers, indent=4, ensure_ascii=False)

    body_code = ""
    send_param = ""
    if req.body:
        try:
            # Check if JSON
            parsed_json = json.loads(req.body)
            body_code = f"payload = {json.dumps(parsed_json, indent=4, ensure_ascii=False)}\n"
            send_param = ", json=payload"
        except Exception:
            # Raw string or data
            body_code = f"payload = {repr(req.body)}\n"
            send_param = ", data=payload"

    code = f'''#!/usr/bin/env python3
"""
Auto-generated API Replay Script
Source: {req.source.upper()}
Endpoint: {req.method} {req.url}
"""

import json
import requests

url = "{req.url}"
headers = {headers_str}

{body_code}response = requests.{req.method.lower()}(
    url,
    headers=headers{send_param},
    timeout=30
)

print(f"Status Code: {{response.status_code}}")
try:
    print("Response JSON:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception:
    print("Response Text:")
    print(response.text[:2000])
'''
    return code


def generate_curl_command(req: CapturedRequest) -> str:
    """Generate copy-pasteable cURL command from CapturedRequest."""
    parts = ["curl", "-X", req.method, f'"{req.url}"']
    for k, v in req.headers.items():
        if k.lower() not in ("content-length", "host", "connection", "accept-encoding"):
            parts.extend(["-H", f'"{k}: {v}"'])

    if req.body:
        try:
            # If JSON, format minified
            min_json = json.dumps(json.loads(req.body), ensure_ascii=False)
            parts.extend(["--data-raw", f"'{min_json}'"])
        except Exception:
            parts.extend(["--data-raw", f"'{req.body}'"])

    return " ".join(parts)
