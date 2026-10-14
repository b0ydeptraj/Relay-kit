#!/usr/bin/env python3
"""
CLI entry point for Relay-Kit Unified API Interceptor & Sniffer Hub.
Usage:
    python scripts/api_sniffer.py start --port 8999
    python scripts/api_sniffer.py mobile-cert <cert_file.pem>
    python scripts/api_sniffer.py frida-script [--out bypass.js]
"""

import argparse
import sys
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from tools.api_interceptor.mobile_helper import (
    FRIDA_UNIVERSAL_SSL_BYPASS,
    get_connected_adb_devices,
    prepare_system_ca_cert,
)
from tools.api_interceptor.sniffer_hub import run_sniffer_hub


def main() -> None:
    parser = argparse.ArgumentParser(description="Relay-Kit Unified API Interceptor & Sniffer Hub")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: start
    p_start = subparsers.add_parser("start", help="Start the local API Sniffer Hub and Web Dashboard")
    p_start.add_argument("--port", type=int, default=8999, help="Server port (default: 8999)")
    p_start.add_argument("--host", type=str, default="127.0.0.1", help="Server host (default: 127.0.0.1)")

    # Subcommand: mobile-cert
    p_cert = subparsers.add_parser("mobile-cert", help="Prepare CA certificate for Android /system/etc/security/cacerts")
    p_cert.add_argument("cert_file", type=str, help="Path to CA certificate (.pem or .crt)")
    p_cert.add_argument("--out-dir", type=str, default=None, help="Directory to save the formatted <hash>.0 file")

    # Subcommand: frida-script
    p_frida = subparsers.add_parser("frida-script", help="Export Universal Mobile SSL Pinning Bypass script")
    p_frida.add_argument("--out", type=str, default=None, help="Output path (e.g. bypass.js)")

    # Subcommand: adb-status
    subparsers.add_parser("adb-status", help="Check connected Android emulators and devices")

    args = parser.parse_args()

    if args.command == "start":
        server = run_sniffer_hub(port=args.port, host=args.host)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Stopping Sniffer Hub...")
            server.server_close()
            sys.exit(0)

    elif args.command == "mobile-cert":
        cert_p = Path(args.cert_file)
        out_p = Path(args.out_dir) if args.out_dir else None
        res = prepare_system_ca_cert(cert_p, out_p)
        print("\n" + "=" * 60)
        print("📱 ANDROID SYSTEM CA CERT PREPARED")
        print(f"[*] Hash Name : {res['system_hash']}")
        print(f"[*] Saved to  : {res['output_file']}")
        print("\n[!] Run the following ADB commands to install:")
        print(res["adb_instructions"])
        print("=" * 60 + "\n")

    elif args.command == "frida-script":
        if args.out:
            out_file = Path(args.out)
            out_file.write_text(FRIDA_UNIVERSAL_SSL_BYPASS, encoding="utf-8")
            print(f"[+] Saved Frida SSL Pinning script to: {out_file.resolve()}")
        else:
            print(FRIDA_UNIVERSAL_SSL_BYPASS)

    elif args.command == "adb-status":
        devices = get_connected_adb_devices()
        print(f"[*] Connected ADB Devices: {len(devices)}")
        for d in devices:
            print(f"  -> {d}")


if __name__ == "__main__":
    main()
