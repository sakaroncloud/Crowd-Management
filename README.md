# ✥ CrowdSync — Advanced Venue Intelligence ✥

[![Terraform](https://img.shields.io/badge/Infrastructure-Terraform-623CE4?style=for-the-badge&logo=terraform)](https://www.terraform.io/)
[![AWS](https://img.shields.io/badge/Cloud-AWS-232F3E?style=for-the-badge&logo=amazon-aws)](https://aws.amazon.com/)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge&logo=react)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Scripts-Python-3776AB?style=for-the-badge&logo=python)](https://www.python.org/)

> **Elevate your venue management with real-time crowd diagnostics and automated incident response.**

---

## 🏛️ System Architecture

```text
                                  ╭──────────────────────────────────╮
                                  │          AWS CLOUD (eu-west-2)   │
      ╔═══════════════════════════╧══════════════════════════════════╧═══════════════════════════╗
      ║                                                                                          ║
      ║   ╭───────────────╮          ╭────────────────╮          ╭───────────────────────────╮   ║
      ║   │  🔐 COGNITO   │◀──┬───▶  │  🌐 API GATEWAY │  ──────▶  │   ⚡ LAMBDA FUNCTIONS      │   ║
      ║   │  User Identity│   │      │   HTTP API v2  │          │   (Ingest, Read, Auth)    │   ║
      ║   ╰───────────────╯   │      ╰────────────────╯          ╰─────────────┬─────────────╯   ║
      ║                       │                                                │                 ║
      ║                       ▼                                                ▼                 ║
      ║   ╭───────────────────────╮          ╭────────────────╮          ╭───────────────────╮   ║
      ║   │  📦 SSM PARAMETER     │  ◀─────  │  🛡️ AUTHORIZER  │          │   📊 DYNAMODB     │   ║
      ║   │  Ingest API Token     │          │  Lambda-based  │          │   Zones Table     │   ║
      ║   ╰───────────────────────╯          ╰────────────────╯          ╰───────────────────╯   ║
      ║                                                                                          ║
      ║   ╭───────────────────────╮          ╭────────────────╮          ╭───────────────────╮   ║
      ║   │  ☁️ CLOUDFRONT (CDN)   │  ◀─────  │  📦 S3 BUCKET    │          │   🔔 SNS TOPIC    │   ║
      ║   │  Global Dashboard     │          │  Static Hosting │          │   Critical Alerts │   ║
      ║   ╰───────────────────────╯          ╰────────────────╯          ╰───────────────────╯   ║
      ║                                                                                          ║
      ║                                                                                          ║
      ╚═══════════════════════════════════════════════╦══════════════════════════════════════════╝
                                                      ║
                                                      ▼ 
                                         ╭──────────────────────────╮
                                         │   🖥️ REACT DASHBOARD    │
                                         │   (Vite + TypeScript)    │
                                         ╰──────────────────────────╯
```

---

## 📂 Project Navigation

```text
.
├── 📂 dashboard/               # High-Fidelity React Frontend
│   ├── 📂 src/
│   │   ├── 📄 App.tsx          # Real-time Telemetry & Notification Engine
│   │   ├── 📄 aws-config.ts    # ⚡ Auto-injected AWS Configuration
│   │   └── 📂 components/      # UI Design System (Shadcn/UI)
│   └── 📄 package.json
│
├── 📂 lambda_src/              # Serverless Application Logic
│   ├── 🐍 ingest_handler.py    # Crowd Data Ingestion Pipeline
│   ├── 🐍 read_handler.py     # High-Performance Read API
│   └── 🐍 authorizer_handler.py # Robust API Token Validation
│
├── 📂 modules/                 # Infrastructure-as-Code (Terraform)
│   ├── 📦 cognito/             # Identity & Access Management
│   ├── 📦 dynamodb/            # Schema-less Data Storage
│   └── 📦 frontend/            # S3/CloudFront Distribution Layer
│
├── 📂 scripts/                 # Automated Workflow Engine
│   ├── 🐍 manage.py            # Phase-aware Deployment Mission Control
│   └── 🐍 simulate.py          # Real-time Telemetry Simulator
│
├── 📄 main.tf                   # Root Orchestrator
└── 📄 README.md                 # Project Manifesto
```

---

## ⚡ Quick Start

### 1️⃣ Initial Infrastructure
Ensure your Terraform backend is configured in `providers.tf`.

### 2️⃣ Full Deployment
Run the mission control script. It handles infrastructure, config injection, and frontend compilation in a single pass:
```bash
python3 scripts/manage.py up
```

### 3️⃣ Live Simulation
Stream synthetic crowd data to your live dashboard:
```bash
python3 scripts/simulate.py
```

---

## 🧪 Deployment Intelligence

This project uses a **Two-Phase Deployment** strategy implemented in `manage.py`:

| Execution Phase | Action |
| :--- | :--- |
| **Phase I: Provisioning** | Terraform builds the AWS environment and outputs unique Resource IDs. |
| **Phase II: Injection** | Python extracts IDs and injects them directly into `dashboard/src/aws-config.ts`. |
| **Phase III: Compilation** | The dashboard is compiled with the *correct* live credentials. |
| **Phase IV: Distribution** | Terraform re-syncs the final bundle to the S3/CloudFront edge nodes. |

---

## 🛠️ Infrastructure Core

*   **🔒 Identity**: Cognito User Pools with strict administrative control and "First Login" password enforcement.
*   **📡 Networking**: CloudFront OAC (Origin Access Control) for secure, low-latency edge delivery.
*   **📊 Storage**: DynamoDB Pay-Per-Request table with 6 pre-seeded zones for immediate visualization.
*   **🔔 Alerts**: SNS integration triggers notifications on capacity breaches (80%+ occupancy).

---

## 📈 Dashboard Logic

The dashboard polls at **15s intervals** with intelligent state tracking:
*   **Normal (0-50)**: Green indicators. "Steady State."
*   **Busy (51-80)**: Yellow warnings. "Monitor Flow."
*   **Critical (81+)**: Red pulsing alerts. "Restrict Entry / Redirect Flow."

*Toasts and bell notifications only trigger on status transitions to minimize noise.*

---

## 🧹 Maintenance

**Wipe Environment:**
```bash
python3 scripts/manage.py down
```
*Requires manual 'yes' confirmation. Irreversible deletion of DynamoDB datasets and Cognito identities.*

---
*✥ Crafted for Operational Excellence ✥*
