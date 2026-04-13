# ✥ CrowdSync — Advanced Venue Intelligence ✥

[![Terraform](https://img.shields.io/badge/Infrastructure-Terraform-623CE4?style=for-the-badge&logo=terraform)](https://www.terraform.io/)
[![AWS](https://img.shields.io/badge/Cloud-AWS-232F3E?style=for-the-badge&logo=amazon-aws)](https://aws.amazon.com/)
[![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge&logo=react)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Scripts-Python-3776AB?style=for-the-badge&logo=python)](https://www.python.org/)

> **Elevate your venue management with real-time crowd diagnostics and automated incident response.**

---

## 🏛️ System Architectures

CrowdSync is designed to evolve from a functional prototype into a high-scale industrial monitoring system. Below are the two implementation paths.

### Stage 1: Functional Prototype (Current)
*Designed for rapid validation, low cost, and serverless agility.*

```text
                                  ╭──────────────────────────────────╮
                                  │   🌐 AWS CLOUD (Prototype)       │
      ╔═══════════════════════════╧══════════════════════════════════╧═══════════════════════════╗
      ║                                                                                          ║
      ║   ╭────────────────╮         ╭────────────────╮          ╭───────────────────────────╮   ║
      ║   │  🔐 COGNITO    │ ◀──┬──▶ │  🌐 API GATEWAY │  ──────▶  │   ⚡ LAMBDA FUNCTIONS      │   ║
      ║   │  JWT Auth      │    │    │   HTTP API v2  │          │   (Ingest, Read, Auth)    │   ║
      ║   ╰────────────────╯    │    ╰────────────────╯          ╰─────────────┬─────────────╯   ║
      ║                         │                                              │                 ║
      ║                         ▼                                              ▼                 ║
      ║   ╭───────────────────────╮          ╭────────────────╮          ╭───────────────────╮   ║
      ║   │  📦 SSM PARAMETER     │  ◀─────  │  🛡️ AUTHORIZER  │          │   📊 DYNAMODB     │   ║
      ║   │  Secure API Token     │          │  Lambda-based  │          │   Zones Table     │   ║
      ║   ╰───────────────────────╯          ╰────────────────╯          ╰───────────────────╯   ║
      ║                                                                                          ║
      ║   ╭───────────────────────╮          ╭────────────────╮          ╭───────────────────╮   ║
      ║   │  ☁️ CLOUDFRONT (CDN)   │  ◀─────  │  📦 S3 BUCKET    │          │   🔔 SNS TOPIC    │   ║
      ║   │  Global Dashboard     │          │  Static Hosting │          │   Critical Alerts │   ║
      ║   ╰───────────────────────╯          ╰────────────────╯          ╰───────────────────╯   ║
      ║                                                                                          ║
      ╚════════════╦══════════════════════════════════════════════════════════╦══════════════════╝
                   ║                                                          ║
                   ▼                                                          ▼
      ╭──────────────────────────╮                               ╭──────────────────────────╮
      │   💻 PYTHON SIMULATOR    │                               │   🖥️ REACT DASHBOARD    │
      │   (Ingest API Client)    │                               │   (15s Auto-Polling)     │
      ╰──────────────────────────╯                               ╰──────────────────────────╯
```

### Stage 2: Enterprise Venue (Real-World)
*Designed for tens of thousands of sensors, massive concurrency, and 99.99% availability.*

```text
                                  ╭──────────────────────────────────╮
                                  │   🏢 AWS CLOUD (Production)      │
      ╔═══════════════════════════╧══════════════════════════════════╧═══════════════════════════╗
      ║                                                                                          ║
      ║   ╭────────────────╮          ╭────────────────╮          ╭───────────────────────────╮  ║
      ║   │  🛡️ AWS WAF     │ ◀──────  │  🕸️ APP SYNC   │  ──────▶  │   ⚡ LAMBDA RESOLVERS     │  ║
      ║   │  Edge Guard    │          │  GraphQL / WS  │          │   High-Performance Logic  │  ║
      ║   ╰────────────────╯          ╰────────────────╯          ╰─────────────┬─────────────╯  ║
      ║          ▲                           ▲                                  │                ║
      ║          │                           │            (Real-time Push)      ▼                ║
      ║          │                           │                         ╭───────────────────╮     ║
      ║   ╭──────┴─────────╮          ╭──────┴─────────╮               │   📊 DYNAMODB     │     ║
      ║   │  🛰️ IoT CORE    │ ──────▶  │  🌊 KINESIS    │ ──────▶       │   Global Tables   │     ║
      ║   │  mTLS Auth     │          │  Data Streams  │               ╰───────────────────╯     ║
      ║   ╰────────────────╯          ╰────────────────╯                         │                ║
      ║          ▲                                                               ▼                ║
      ║          │                                                     ╭───────────────────╮     ║
      ║   ╭──────┴─────────╮          ╭────────────────╮               │   🧠 SAGEMAKER    │     ║
      ║   │ 📷 CV SENSORS  │          │  📦 DATA LAKE  │ ◀──────       │   Predictive AI   │     ║
      ║   │ AI Edge Vision │          │   S3 / Athena  │               ╰───────────────────╯     ║
      ║   ╰────────────────╯          ╰────────────────╯                                         ║
      ║                                                                                          ║
      ╚═══════════════════════════════════════════════╦══════════════════════════════════════════╝
                                                      ║
                                                      ▼ 
                                         ╭──────────────────────────╮
                                         │   📱 MOBILE DASHBOARD    │
                                         │   (GraphQL Subscriptions)│
                                         ╰──────────────────────────╯
```

---

## 🛡️ Security & Compliance

CrowdSync implements a multi-layered security model to protect telemetry data and administrative access.

### 🔑 Identity & Access Control
*   **Cognito User Pools**: Secure user authentication with mandated password complexity.
*   **Authentication Challenge**: New administrators are forced to update their temporary password on first login via a custom security dashboard.
*   **JWT Validation**: The `read` API requires a valid Cognito Identity Token in the `Authorization` header.
*   **Least Privilege (IAM)**: Every Lambda function runs with a minimal policy, restricting access only to the specific DynamoDB tables, S3 buckets, or SNS topics they require.

### 🛡️ Infrastructure Protection
*   **CloudFront OAC (Origin Access Control)**: Restricts S3 bucket access solely to the CloudFront distribution. The bucket is not accessible via public internet.
*   **API Gateway Authorizer**: The `ingest` endpoint is protected by a Lambda Authorizer that validates an `x-api-token` against an encrypted SSM parameter.
*   **SSM SecureStrings**: Sensitive credentials like API tokens are stored as encrypted strings using AWS-managed KMS keys.
*   **Masked Outputs**: Terraform outputs containing secret tokens are marked as `sensitive` to prevent them from appearing in CI/CD logs.

### 📜 Data Protection
*   **Encryption at Rest**:
    *   **DynamoDB**: Encrypted using AWS-managed keys.
    *   **S3**: AES-256 server-side encryption enabled for all log and frontend assets.
*   **Encryption in Transit**: All communication between the simulator, dashboard, and AWS occurs over **TLS 1.2/1.3**.

### 🌍 Real-World Security Evolution
In a production setting, we recommend the following additional layers:
1.  **AWS WAF**: Deploy a Web Application Firewall to block SQL injection and rate-limit abusive requests.
2.  **Mutual TLS (mTLS)**: Use IoT Core's certificate-based authentication to ensure only verified hardware sensors can talk to the ingest pipeline.
3.  **VPC Isolation**: Move Lambda functions into a private VPC with NAT Gateways to prevent direct outbound internet access.

---

## 📂 Project Navigation

```text
.
├── 📂 dashboard/               # High-Fidelity React Frontend
│   ├── 📂 src/
│   │   ├── 📄 App.tsx          # Real-time Telemetry & Notification Engine
│   │   ├── 📄 aws-config.ts    # ⚡ Auto-injected AWS Configuration
│   │   └── 📂 components/      # UI Design System (Shadcn/UI)
├── 📂 lambda_src/              # Serverless Application Logic
├── 📂 modules/                 # Infrastructure-as-Code (Terraform)
├── 📂 scripts/                 # Automated Workflow Engine
│   ├── 🐍 manage.py            # Phase-aware Deployment Mission Control
│   └── 🐍 simulate.py          # Real-time Telemetry Simulator
├── 📄 main.tf                   # Root Orchestrator
└── 📄 README.md                 # Project Manifesto
```

---

## 🧪 Deployment Intelligence

This project uses a **Two-Phase Deployment** strategy in `manage.py`:
- **Phase I**: Provisions infrastructure and generates unique AWS IDs.
- **Phase II**: Injects live IDs into `dashboard/src/aws-config.ts`.
- **Phase III**: Compiles the React dashboard and performs a final sync to the CDN.

---
*✥ Crafted for Operational Excellence ✥*
