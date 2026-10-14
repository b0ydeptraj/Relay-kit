@echo off
title Relay-Kit Sniffer Hub (Port 8999)
cd /d "%~dp0"
echo [*] Starting Relay-Kit Unified Sniffer Hub on http://127.0.0.1:8999...
start "" http://127.0.0.1:8999
python -m tools.api_interceptor.sniffer_hub
pause
