#!/usr/bin/env python3
"""
CrowdSync | Live Data Simulator (CloudFormation)
------------------------------------------------
Sends randomised crowd data to all zones to simulate traffic.
"""

import subprocess
import json
import time
import random
import urllib.request
import urllib.error
import ssl
from datetime import datetime

ssl._create_default_https_context = ssl._create_unverified_context

MIN_INTERVAL = 1
MAX_INTERVAL = 2

# Default zones with randomized starting populations
ZONES = {
    "ZONE-A1": random.randint(10, 60),
    "ZONE-B2": random.randint(10, 60),
    "ZONE-C3": random.randint(10, 60),
    "ZONE-D4": random.randint(10, 60),
    "ZONE-E5": random.randint(10, 60),
    "ZONE-F6": random.randint(10, 60)
}

class C:
    RED    = "\033[0;31m"
    GREEN  = "\033[0;32m"
    CYAN   = "\033[0;36m"
    YELLOW = "\033[1;33m"
    RESET  = "\033[0m"

def colour(text: str, code: str) -> str:
    return f"{code}{text}{C.RESET}"

def cfn_output(key: str) -> str:
    cmd = f'aws cloudformation describe-stacks --stack-name crowd-monitoring-main-dev --region eu-west-2 --query "Stacks[0].Outputs[?OutputKey==\'{key}\'].OutputValue" --output text'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def get_token() -> str:
    cmd = f'aws ssm get-parameter --name /crowd-monitoring/dev/ingest_token --with-decryption --region eu-west-2 --query "Parameter.Value" --output text'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

# --- Realistic Logic ---
# --- High-Fidelity Realistic Logic ---
class ZoneState:
    def __init__(self, zone_id, start_count, capacity):
        self.zone_id = zone_id
        self.count = start_count
        self.capacity = capacity
        # Force a LONG-LASTING massive spike for ZONE-A1
        if zone_id == "ZONE-A1":
            self.target = 98
            self.count = 30
        else:
            self.target = random.randint(int(capacity * 0.15), int(capacity * 0.85))
        self.ticks_at_target = 0

    def update(self):
        # Every 60-120 ticks (now much faster), pick a brand new target behavior
        if self.ticks_at_target > random.randint(60, 120):
            if random.random() < 0.2: # 20% chance of a busier state
                self.target = random.randint(int(self.capacity * 0.75), self.capacity + 5)
            else:
                self.target = random.randint(int(self.capacity * 0.1), int(self.capacity * 0.5))
            self.ticks_at_target = 0
        
        self.ticks_at_target += 1

        # Smoothly migrate toward the target (faster for ZONE-C3 spike)
        if self.count < self.target:
            step = 12 if self.zone_id == "ZONE-A1" else random.choice([1, 2])
            self.count += step
        elif self.count > self.target:
            self.count -= random.choice([0, 1, 2])
        else:
            self.count += random.randint(-1, 1)

        # Hard clamp
        self.count = max(0, min(self.capacity + 15, self.count))
        return self.count

def status_label(count, capacity):
    pct = (count / capacity) * 100
    if pct >= 90: return "CRITICAL", C.RED
    elif pct >= 70: return "BUSY", C.YELLOW
    return "NORMAL", C.GREEN

def post_zone(api_url: str, token: str, zone_id: str, count: int) -> int:
    payload = json.dumps({"zoneId": zone_id, "crowdCount": count}).encode()
    req = urllib.request.Request(
        f"{api_url}/crowd-data",
        data=payload,
        headers={"Content-Type": "application/json", "x-api-token": token},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        print(f"  [!] Error: {e}")
        return -1

def main():
    print(colour("[*] Reading CloudFormation configuration...", C.CYAN))
    api_url = cfn_output("ApiUrl")
    token = get_token()

    if not api_url or not token:
        print(colour("[!] Could not read config. Ensure AWS CLI is authenticated and stack is deployed.", C.RED))
        return

    print(colour(f"[✓] API Endpoint: {api_url}", C.GREEN))
    print(colour("[✓] Token loaded", C.GREEN))
    print(colour("[~] Starting Realistic Simulation. Press Ctrl+C to stop.\n", C.CYAN))

    # Initialize stateful zones
    states = {z: ZoneState(z, count, 100) for z, count in ZONES.items()}
    i = 0

    try:
        while True:
            i += 1
            now = datetime.now().strftime("%H:%M:%S")
            print(colour(f"\n--- Simulation Tick [{now}] ---", C.CYAN))
            
            # --- SECURITY PROBE (WAF TEST) ---
            # Every 5th tick, try to send a malicious payload to test the WAF
            if i % 5 == 0:
                print(f"  \033[1;31m[SECURITY] Sending WAF Probe (Hacker Word Test)...\033[0m")
                probe_data = json.dumps({
                    "zoneId": "HACKER-TEST",
                    "crowdCount": 999,
                    "payload": "I am a HACKER trying to bypass security"
                }).encode()
                req = urllib.request.Request(
                    f"{api_url}/crowd-data",
                    data=probe_data,
                    headers={"Content-Type": "application/json", "x-api-token": token},
                    method="POST",
                )
                try:
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        print(f"  \033[1;33m[WARN] WAF allowed the probe (Status: {resp.status})\033[0m")
                except urllib.error.HTTPError as e:
                    if e.code == 403:
                        print(f"  \033[1;32m[SHIELD] WAF blocked the attack! (403 Forbidden)\033[0m")
                    else:
                        print(f"  \033[1;33m[WARN] WAF returned error {e.code}\033[0m")
                except Exception as e:
                    print(f"  \033[1;31m[ERROR] Security probe failed: {str(e)}\033[0m")

            for zone_id, state in states.items():
                count = state.update()
                label, label_colour = status_label(count, state.capacity)

                http_status = post_zone(api_url, token, zone_id, count)
                if http_status == 200:
                    print(f"  [{now}] {zone_id} → {count:>3} people  [{colour(label, label_colour)}]")
                elif http_status != -1:
                    print(colour(f"  [{now}] {zone_id} → HTTP {http_status} (failed)", C.RED))

                time.sleep(0.3)

            sleep_time = random.randint(MIN_INTERVAL, MAX_INTERVAL)
            print(colour(f"    Next update in {sleep_time}s...", C.YELLOW))
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        print(colour("\n[✓] Simulation stopped.", C.CYAN))

if __name__ == "__main__":
    main()
