import os
import json
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

try:
    from relay_kit_v3.evidence_ledger import EvidenceLedger
    from relay_kit_v3.lane_lock import LaneLockManager
except ImportError:
    pass

app = FastAPI(title="Relay-Kit Dashboard")
PROJECT_ROOT = Path(os.getenv("RELAY_KIT_PROJECT_ROOT", "."))


def get_template(name: str) -> str:
    template_path = Path(__file__).parent / "templates" / name
    if template_path.exists():
        return template_path.read_text(encoding="utf-8")
    return ""


@app.get("/", response_class=HTMLResponse)
async def index():
    html_content = get_template("index.html")
    return HTMLResponse(content=html_content)


@app.get("/api/lane-status", response_class=HTMLResponse)
async def lane_status():
    # Placeholder for lane status from ledger/locks
    # Currently we do not have a live lane status API in EvidenceLedger.
    # We will build HTML table rows.
    html = "<tr><td colspan='3'>Lane status data integrated from lane-audit/delegation.</td></tr>"
    return HTMLResponse(content=html)


@app.get("/api/lock-status", response_class=HTMLResponse)
async def lock_status():
    try:
        lock_mgr = LaneLockManager(PROJECT_ROOT)
        locks = lock_mgr.get_all_locks()
    except Exception:
        locks = {}

    if not locks:
        return HTMLResponse(content="<tr><td colspan='3'>No active locks.</td></tr>")
    
    rows = []
    for filepath, lock_info in locks.items():
        locked_by = lock_info.get("agent_id", "-")
        acquired_at = lock_info.get("acquired_at", "-")
        rows.append(f"<tr><td>{filepath}</td><td>{locked_by}</td><td>{acquired_at}</td></tr>")
    
    return HTMLResponse(content="\n".join(rows))


@app.get("/api/event-timeline", response_class=HTMLResponse)
async def event_timeline():
    try:
        ledger = EvidenceLedger(PROJECT_ROOT)
        events = ledger.read_events(limit=20)
    except Exception:
        events = []

    if not events:
        return HTMLResponse(content="<tr><td colspan='4'>No events found in timeline.</td></tr>")
        
    rows = []
    for event in events:
        time = event.get("timestamp", "-")
        gate = event.get("gate", event.get("command", "-"))
        status = event.get("status", "-")
        findings = event.get("findings_count", "-")
        rows.append(f"<tr><td>{time}</td><td>{gate}</td><td>{status}</td><td>{findings}</td></tr>")
    
    return HTMLResponse(content="\n".join(rows))

