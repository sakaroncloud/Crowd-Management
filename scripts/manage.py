#!/usr/bin/env python3
"""
CrowdSync | Infrastructure Management Suite
-------------------------------------------
Python equivalent of manage.sh — cleaner, more readable.

Usage:
    python3 manage.py up       — Build UI, deploy all infrastructure
    python3 manage.py down     — Tear down all infrastructure
    python3 manage.py status   — Show live endpoints and outputs
    python3 manage.py refresh  — Sync state without changing infrastructure
"""

import subprocess
import sys
import os
from pathlib import Path

# ── Configuration ────────────────────────────────────────────
ROOT_DIR     = Path(__file__).parent.parent.resolve()  # project root (one level above scripts/)
UI_DIR       = ROOT_DIR / "dashboard"
TERRAFORM    = "/opt/homebrew/bin/terraform"

# ── ANSI colours ─────────────────────────────────────────────
class C:
    RED    = "\033[0;31m"
    GREEN  = "\033[0;32m"
    CYAN   = "\033[0;36m"
    YELLOW = "\033[1;33m"
    RESET  = "\033[0m"

def colour(text: str, code: str) -> str:
    return f"{code}{text}{C.RESET}"

# ── Helpers ───────────────────────────────────────────────────
def run(cmd: list[str], cwd: Path = ROOT_DIR) -> int:
    """Run a command, stream output live, return exit code."""
    result = subprocess.run(cmd, cwd=cwd)
    return result.returncode

def tf(*args: str) -> int:
    """Run a terraform command from ROOT_DIR."""
    return run([TERRAFORM, *args])

def tf_output(name: str) -> str:
    """Read a single terraform output value silently."""
    result = subprocess.run(
        [TERRAFORM, "output", "-raw", name],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""

# ── Banner ─────────────────────────────────────────────────────
def print_banner():
    print(colour("""
  _____                      _____                   
 / ___/______ _    _________ / ___/________  _______ 
 | |   / ___/ __ \\ | | /| / / \\__ \\/ ___/ __ \\/ ___/ 
 | |__/ /  / /_/ / | |/ |/ / ___/ / /__/ /_/ / /__   
  \\___/_/   \\____/  |__/|__/ /____/\\___/\\____/\\___/   
                   Infrastructure Management Suite
 -----------------------------------------------------------""", C.CYAN))

# ── Validation ─────────────────────────────────────────────────
def check_dependencies():
    print(colour("[*] Validating environment...", C.YELLOW))

    if not Path(TERRAFORM).exists():
        print(colour(f"[!] Terraform not found at {TERRAFORM}", C.RED))
        sys.exit(1)
    print(colour("[✓] Terraform ready.", C.GREEN))

    npm = subprocess.run(["npm", "--version"], capture_output=True)
    if npm.returncode != 0:
        print(colour("[!] npm not found — UI build will fail.", C.RED))
        sys.exit(1)
    print(colour("[✓] npm ready.", C.GREEN))

# ── Commands ───────────────────────────────────────────────────
def cmd_up():
    """Build the React UI, then deploy all infrastructure."""
    # Step 1: Build React app
    print(colour("\n[●] Building UI...", C.GREEN))
    exit_code = run(["npm", "run", "build"], cwd=UI_DIR)
    if exit_code != 0:
        print(colour("[!] UI build failed. Aborting deployment.", C.RED))
        sys.exit(1)
    print(colour("[✓] UI build complete.", C.GREEN))

    # Step 2: Terraform init + apply
    print(colour("\n[▲] Initialising & Deploying Infrastructure...", C.GREEN))
    if tf("init") != 0:
        sys.exit(1)
    if tf("apply", "-auto-approve") != 0:
        sys.exit(1)

    print(colour("\n[✓] Deployment Complete.", C.GREEN))
    cmd_status()


def cmd_down():
    """Destroy all infrastructure. Irreversible."""
    print(colour("[▼] CAUTION: DESTROYING ALL INFRASTRUCTURE...", C.RED))
    print(colour("[!] This will permanently delete DynamoDB data and Cognito users.", C.YELLOW))

    confirm = input(colour("    Type 'yes' to confirm: ", C.YELLOW)).strip()
    if confirm != "yes":
        print(colour("[✗] Aborted.", C.CYAN))
        sys.exit(0)

    if tf("destroy", "-auto-approve") != 0:
        sys.exit(1)
    print(colour("\n[✓] Environment successfully wiped.", C.RED))


def cmd_status():
    """Print all live infrastructure endpoints."""
    print(colour("\n[ℹ] System Status & Endpoints:", C.CYAN))

    outputs = {
        "API Gateway":    tf_output("api_endpoint"),
        "App Client ID":  tf_output("cognito_client_id"),
        "User Pool ID":   tf_output("cognito_user_pool_id"),
        "Frontend (CDN)": tf_output("frontend_url"),
    }

    for label, value in outputs.items():
        display = colour(value or "not deployed", C.GREEN if value else C.YELLOW)
        print(f"  > {label:<15} {display}")

    print(f"  > {'UI Dev Server':<15} {colour('http://localhost:5173', C.YELLOW)}")


def cmd_refresh():
    """Sync Terraform state with real AWS resources, no changes applied."""
    print(colour("[~] Refreshing state...", C.CYAN))
    tf("apply", "-refresh-only", "-auto-approve")


# ── Entry Point ────────────────────────────────────────────────
COMMANDS = {
    "up":      cmd_up,
    "down":    cmd_down,
    "status":  cmd_status,
    "refresh": cmd_refresh,
}

def main():
    print_banner()
    check_dependencies()

    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(colour("\nUsage: python3 manage.py {up|down|status|refresh}", C.YELLOW))
        sys.exit(1)

    COMMANDS[sys.argv[1]]()

if __name__ == "__main__":
    main()
