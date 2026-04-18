#!/usr/bin/env python3
"""
CrowdSync | Live Data Simulator
--------------------------------
Sends randomised crowd data to all zones at random intervals,
simulating real-world occupancy fluctuations.

Usage:
    python3 simulate.py
"""

import subprocess
import json
import time
import random
import urllib.request
import urllib.error
import ssl
from datetime import datetime
from pathlib import Path

# Bypass SSL verification (Commonly required for macOS Python environments)
ssl._create_default_https_context = ssl._create_unverified_context

# ── Configuration ────────────────────────────────────────────
ROOT_DIR     = Path(__file__).parent.parent.resolve()  # project root (one level above scripts/)
TERRAFORM    = "/opt/homebrew/bin/terraform"
MIN_INTERVAL = 5   # seconds between ticks (min)
MAX_INTERVAL = 15  # seconds between ticks (max)

ZONES: dict[str, int] = {
    "ZONE-A1": 23,
    "ZONE-B2": 67,
    "ZONE-C3": 95,
    "ZONE-D4": 12,
    "ZONE-E5": 54,
    "ZONE-F6": 8,
}

# ── ANSI colours ─────────────────────────────────────────────
class C:
    RED    = "\033[0;31m"
    GREEN  = "\033[0;32m"
    CYAN   = "\033[0;36m"
    YELLOW = "\033[1;33m"
    RESET  = "\033[0m"

def colour(text: str, code: str) -> str:
    return f"{code}{text}{C.RESET}"

# ── Terraform outputs ─────────────────────────────────────────
def tf_output(name: str) -> str:
    result = subprocess.run(
        [TERRAFORM, "output", "-raw", name],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""

# ── Crowd simulation ──────────────────────────────────────────
def next_count(current: int) -> int:
    """Bounded random walk: shift ±15, clamped between 1 and 120."""
    delta = random.randint(-15, 15)
    return max(1, min(120, current + delta))

def status_label(count: int) -> tuple[str, str]:
    """Return (status_string, colour_code) based on crowd count."""
    if count > 80:
        return "CRITICAL", C.RED
    elif count > 50:
        return "BUSY", C.YELLOW
    return "NORMAL", C.GREEN

# ── HTTP POST ─────────────────────────────────────────────────
def post_zone(api_url: str, token: str, zone_id: str, count: int) -> int:
    """POST crowd data. Returns HTTP status code."""
    payload = json.dumps({"zoneId": zone_id, "crowdCount": count}).encode()
    req = urllib.request.Request(
        f"{api_url}/crowd-data",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-token": token,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        # Return a negative number or specific code to indicate a local/network error
        print(f"  [!] Connection Error: {e}")
        return -1

# ── Main ──────────────────────────────────────────────────────
def main():
    print(colour("[*] Reading infrastructure configuration...", C.CYAN))

    api_url = tf_output("api_endpoint")
    token   = tf_output("ingest_token")

    if not api_url or not token:
        print(colour("[!] Could not read Terraform outputs. Run 'python3 manage.py up' first.", C.RED))
        raise SystemExit(1)

    print(colour(f"[✓] API Endpoint: {api_url}", C.GREEN))
    print(colour("[✓] Token loaded", C.GREEN))
    print(colour("[~] Starting simulation. Press Ctrl+C to stop.\n", C.CYAN))

    counts = dict(ZONES)  # mutable copy of starting counts

    try:
        while True:
            now = datetime.now().strftime("%H:%M:%S")
            print(colour(f"\n--- Simulation Tick [{now}] ---", C.CYAN))

            for zone_id in counts:
                counts[zone_id] = next_count(counts[zone_id])
                count  = counts[zone_id]
                label, label_colour = status_label(count)

                http_status = post_zone(api_url, token, zone_id, count)

                if http_status == 200:
                    print(
                        f"  [{datetime.now().strftime('%H:%M:%S')}] "
                        f"{zone_id} → {count:>3} people  "
                        f"[{colour(label, label_colour)}]"
                    )
                elif http_status == -1:
                    # Connection/SSL error already printed by post_zone
                    pass
                else:
                    print(colour(
                        f"  [{datetime.now().strftime('%H:%M:%S')}] "
                        f"{zone_id} → HTTP {http_status} (failed)",
                        C.RED,
                    ))

                time.sleep(0.3)  # small stagger between zones

            sleep_time = random.randint(MIN_INTERVAL, MAX_INTERVAL)
            print(colour(f"    Next update in {sleep_time}s...", C.YELLOW))
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print(colour("\n[✓] Simulation stopped.", C.CYAN))

if __name__ == "__main__":
    main()
