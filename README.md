# CrowdSync — Real-Time Crowd Monitoring Platform

A full-stack, cloud-native crowd monitoring system built entirely on AWS, managed with Terraform, and visualised through a React dashboard. Venue operators can track occupancy across multiple zones in real time, receive critical alerts when capacity thresholds are breached, and host the entire platform on AWS with a single command.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
  - [Authentication Flow](#authentication-flow)
  - [Data Ingestion Flow](#data-ingestion-flow)
  - [Dashboard & Alerts](#dashboard--alerts)
- [Infrastructure Modules](#infrastructure-modules)
- [Lambda Functions](#lambda-functions)
- [Dashboard (React)](#dashboard-react)
- [Scripts](#scripts)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Teardown](#teardown)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS Cloud                             │
│                                                             │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────────┐  │
│  │ Cognito  │    │ API Gateway  │    │    Lambda Fns     │  │
│  │ User Pool│◄──►│  HTTP API   │───►│ ingest / read /   │  │
│  └──────────┘    │             │    │   authorizer      │  │
│                  └──────────────┘    └────────┬──────────┘  │
│  ┌──────────┐                                 │             │
│  │    SSM   │◄─── authorizer reads token      │             │
│  └──────────┘                        ┌────────▼──────────┐  │
│                                      │     DynamoDB      │  │
│  ┌──────────┐                        │  crowd-zones table│  │
│  │   SNS    │◄─── critical alert     └───────────────────┘  │
│  └──────────┘                                               │
│                                                             │
│  ┌──────────────────────────────┐                           │
│  │  S3 + CloudFront             │  ← React dashboard hosted │
│  └──────────────────────────────┘                           │
│                                                             │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ S3 Logs  │  │  CloudWatch  │  │  Remote TF State (S3)│  │
│  └──────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         ▲
         │  HTTPS (Cognito JWT)
         │
┌────────┴──────────┐
│  React Dashboard  │  localhost:5173 (dev) or CloudFront URL (prod)
│  (Vite + TypeScript)
└───────────────────┘
```

---

## Project Structure

```
cloud/
│
├── dashboard/                  # React frontend application
│   ├── src/
│   │   ├── App.tsx             # Main dashboard + notification system
│   │   ├── aws-config.ts       # Cognito & API Gateway endpoints
│   │   ├── index.css           # Global styles & design tokens
│   │   ├── main.tsx            # React entry point
│   │   └── components/
│   │       └── auth-center.tsx # Custom login + password change UI
│   ├── index.html              # CSP headers live here
│   ├── package.json
│   └── tsconfig.app.json
│
├── lambda_src/                 # Python source code for Lambda functions
│   ├── ingest_handler.py       # Handles POST /crowd-data
│   ├── read_handler.py         # Handles GET /zones
│   └── authorizer_handler.py  # Validates x-api-token via SSM
│
├── modules/                    # Terraform infrastructure modules
│   ├── cognito/                # User authentication (Cognito User Pool)
│   ├── dynamodb/               # DynamoDB table for zone data
│   ├── frontend/               # S3 + CloudFront for hosting dashboard
│   ├── iam/                    # Lambda IAM roles and policies
│   ├── lambda/                 # Lambda function definitions
│   ├── monitoring/             # CloudWatch alarms
│   ├── s3/                     # S3 bucket for ingestion logs
│   ├── sns/                    # SNS topic for critical alerts
│   └── ssm/                    # SSM parameter for ingest API token
│
├── scripts/                    # Python management tools
│   ├── manage.py               # Deploy / destroy / status / refresh
│   └── simulate.py             # Live crowd data simulator
│
├── main.tf                     # Root: wires all modules together
├── providers.tf                # AWS provider + S3 remote backend config
├── variables.tf                # Global variables (region, project name, env)
├── outputs.tf                  # Exports: API URL, Cognito IDs, frontend URL
├── seed_data.tf                # Initial DynamoDB zone records
├── .gitignore
└── README.md
```

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| [Terraform](https://www.terraform.io/) | ≥ 1.6 | Infrastructure provisioning |
| Python | 3.10+ | Management scripts |
| Node.js + npm | ≥ 18 | React dashboard |
| AWS Account | — | Hosting all infrastructure |
| AWS credentials | — | Configured via `~/.aws/credentials` |

> **Terraform binary location**: The scripts assume `/opt/homebrew/bin/terraform` (macOS Homebrew).
> Update `TERRAFORM` in `scripts/manage.py` and `scripts/simulate.py` if your path differs.

---

## Quick Start

### 1. Configure Remote State Backend

The Terraform state is stored remotely in S3 for safety and team collaboration.
Ensure the bucket exists in your AWS account (`providers.tf`):

```hcl
backend "s3" {
  bucket       = "sakar-lab-tfstate-bucket"
  key          = "day-5/terraform.tfstate"
  region       = "eu-west-2"
  use_lockfile = true
  encrypt      = true
}
```

### 2. Update Dashboard Config

Edit `dashboard/src/aws-config.ts` with your Cognito and API values.
These are printed automatically after every `manage.py up` run:

```typescript
const awsConfig = {
  Auth: {
    region: 'eu-west-2',
    userPoolId: 'eu-west-2_XXXXXXXX',
    userPoolWebClientId: 'XXXXXXXXXXXXXXXXXXXXXXXX',
  },
  API: {
    endpoints: [{
      name: 'CrowdMonitorAPI',
      endpoint: 'https://XXXXXXXXXX.execute-api.eu-west-2.amazonaws.com',
      region: 'eu-west-2'
    }]
  }
}
```

### 3. Deploy Everything

```bash
python3 scripts/manage.py up
```

This single command:
- Builds the React dashboard (`npm run build`)
- Runs `terraform init` (connects to S3 backend)
- Runs `terraform apply` (provisions all 38 AWS resources)
- Uploads the built dashboard to S3/CloudFront
- Prints all live endpoints

### 4. First Login

Terraform automatically creates a seed admin user (`sakaroncloud@gmail.com`).
AWS Cognito emails a temporary password. On first login, you will be prompted to set a permanent password.

### 5. Run the Data Simulator (optional)

```bash
python3 scripts/simulate.py
```

Sends realistic random crowd data to all 6 zones every 5–15 seconds.

---

## How It Works

### Authentication Flow

```
User enters email + password
        │
        ▼
AWS Cognito (USER_PASSWORD_AUTH)
        │
        ├─── First login? → NEW_PASSWORD_REQUIRED challenge
        │         └─→ "Security Upgrade" UI shown → User sets permanent password
        │
        └─── Authenticated → Cognito issues JWT tokens (ID, Access, Refresh)
                    │
                    ▼
            JWT stored in cookie (secure, same-site strict)
                    │
                    ▼
       Attached as `Authorization: Bearer <token>` on every API call
```

### Data Ingestion Flow

```
POST /crowd-data  { zoneId, crowdCount }
        │
        ▼
API Gateway → Lambda Authorizer
        │   reads x-api-token header
        │   validates against SSM SecureString
        │
        ▼ (authorised)
ingest_handler Lambda
        │
        ├──► DynamoDB: update zone record with count, status, action, timestamp
        ├──► S3: write structured JSON log entry (logs/YYYY/MM/DD/<uuid>.json)
        └──► SNS: if crowdCount > 80 → publish CRITICAL ALERT notification
```

**Status thresholds:**

| Count | Status | Action |
|-------|--------|--------|
| > 80 | 🔴 Critical | Restrict Entry / Redirect Flow |
| > 50 | 🟡 Busy | Monitor closely |
| ≤ 50 | 🟢 Normal | No Action |

### Dashboard & Alerts

The React dashboard polls `GET /zones` every **15 seconds** using the user's Cognito JWT.

**Critical Alert System:**
- On each poll, the dashboard compares the current zone status against the previous status
- If any zone **transitions into Critical** (was Normal/Busy → now Critical), a toast notification slides in from the top-right
- The notification bell in the navbar accumulates all incidents with a badge count
- Toasts auto-dismiss after 8 seconds with an animated countdown bar

---

## Infrastructure Modules

### `modules/cognito/`
Creates the Cognito User Pool and App Client for authentication.
- Email-based login (no username)
- Admin-only user creation (`allow_admin_create_user_only = true`)
- Callback URLs include both localhost (dev) and CloudFront URL (prod)
- Seeds an initial admin user via `aws_cognito_user`

### `modules/dynamodb/`
Provisions the `crowd-monitoring-zones-dev` DynamoDB table.
- Partition key: `zoneId` (String)
- Billing mode: Pay-per-request (no capacity planning needed)

### `modules/frontend/`
Hosts the compiled React app on AWS with global CDN.
- Private S3 bucket (no public access)
- CloudFront Origin Access Control (OAC) — modern replacement for OAI
- Automatic HTTPS redirect
- SPA routing: 403/404 → `/index.html` (handles React Router deep links)
- All files in `dashboard/dist/` uploaded as `aws_s3_object` resources
- Cache: 1 hour default, 24 hour max

### `modules/iam/`
Lambda execution role with least-privilege policies:
- `AWSLambdaBasicExecutionRole` — CloudWatch Logs
- DynamoDB: `PutItem`, `GetItem`, `Scan`
- S3: `PutObject` on the logs bucket
- SNS: `Publish` on the alerts topic
- SSM: `GetParameter` for reading the ingest token

### `modules/lambda/`
Packages and deploys three Lambda functions from `lambda_src/`:
- `archive_file` data source zips each `.py` file automatically
- Re-deploys only when source file hash changes
- Runtime: Python 3.9

### `modules/monitoring/`
Three CloudWatch Metric Alarms:
- `5xx` errors on API Gateway
- Errors on the `ingest` Lambda
- Errors on the `read` Lambda

### `modules/s3/`
Encrypted, private S3 bucket for ingestion event logs.
- SSE-AES256 encryption at rest
- All public access blocked

### `modules/sns/`
SNS topic that receives critical crowd alerts from the ingest Lambda.
Connect an email subscription in the AWS Console to receive SMS/email notifications.

### `modules/ssm/`
Stores the randomly generated ingest API token as an SSM `SecureString`.
- Token is 32 characters, auto-generated by `random_password`
- The Lambda Authorizer reads it at runtime to validate `x-api-token` headers
- Exposed as a sensitive Terraform output for use by `simulate.py`

---

## Lambda Functions

### `ingest_handler.py` — POST /crowd-data
Receives crowd data from sensors/simulators. Validates the payload, determines status, writes to DynamoDB, logs to S3, and triggers SNS if critical.

```python
# Input
{ "zoneId": "ZONE-A1", "crowdCount": 85 }

# Output
{ "zoneId": "ZONE-A1", "status": "Critical", "action": "Restrict Entry / Redirect Flow", "timestamp": "..." }
```

### `read_handler.py` — GET /zones or GET /zones/{id}
Returns zone data from DynamoDB. Requires a valid Cognito JWT in the `Authorization` header.

```python
# GET /zones → returns all zones as a JSON array
# GET /zones/ZONE-A1 → returns a single zone object
```

### `authorizer_handler.py` — Lambda Authorizer
Protects the `POST /crowd-data` endpoint. Reads the `x-api-token` header and validates it against the value stored in SSM. Returns `isAuthorized: true/false`.

---

## Dashboard (React)

Built with **Vite + React + TypeScript**, using:
- `@aws-amplify/ui-react` — authentication state management
- `aws-amplify` — Cognito integration and session management
- `framer-motion` — animations and toast transitions
- `lucide-react` — icons
- `shadcn/ui` components — Card, Badge, Alert, Skeleton, Separator

### Key files

| File | Purpose |
|------|---------|
| `src/App.tsx` | Main dashboard, zone cards, notification system, stat cards |
| `src/components/auth-center.tsx` | Login form + NEW_PASSWORD_REQUIRED flow |
| `src/aws-config.ts` | **Update this after every deploy** with new Cognito/API values |
| `src/index.css` | Design tokens, glassmorphism, typography |
| `index.html` | Content Security Policy (CSP) headers |

### Zone Capacity (frontend config)

Defined statically in `App.tsx` — update as needed:

```typescript
const ZONE_CAPACITY: Record<string, number> = {
  'ZONE-A1': 100,
  'ZONE-B2': 80,
  'ZONE-C3': 120,
  'ZONE-D4': 60,
  'ZONE-E5': 90,
  'ZONE-F6': 50,
};
```

---

## Scripts

### `scripts/manage.py`

Infrastructure lifecycle manager. Reads config from Terraform outputs automatically.

```bash
python3 scripts/manage.py up       # Build dashboard + deploy all AWS resources
python3 scripts/manage.py down     # Destroy all infra (prompts for confirmation)
python3 scripts/manage.py status   # Print all live endpoints
python3 scripts/manage.py refresh  # Sync Terraform state without applying changes
```

### `scripts/simulate.py`

Sends randomised crowd counts to all zones at random intervals (5–15 seconds).
Uses a **bounded random walk** (±15 per tick, clamped 1–120) for realistic-looking data.
Reads the API endpoint and ingest token directly from Terraform state.

```bash
python3 scripts/simulate.py
```

Press `Ctrl+C` to stop.

---

## API Reference

### `POST /crowd-data`
Ingest crowd data for a zone.

**Auth:** `x-api-token: <ssm_token>` (from `terraform output -raw ingest_token`)

```json
// Request
{ "zoneId": "ZONE-A1", "crowdCount": 75 }

// Response 200
{ "zoneId": "ZONE-A1", "status": "Busy", "action": "Monitor closely", "timestamp": "2026-04-13T20:00:00Z" }

// Response 400
{ "error": "Missing zoneId or crowdCount" }
```

### `GET /zones`
Retrieve all zone records.

**Auth:** `Authorization: Bearer <cognito_id_token>`

```json
[
  { "zoneId": "ZONE-A1", "crowdCount": 75, "status": "Busy", "action": "Monitor closely", "lastUpdated": "..." },
  ...
]
```

### `GET /zones/{id}`
Retrieve a single zone record.

---

## Configuration

### Changing region or project name

Edit `variables.tf`:
```hcl
variable "aws_region"    { default = "eu-west-2" }
variable "project_name"  { default = "crowd-monitoring" }
variable "environment"   { default = "dev" }
```

### Changing alert thresholds

Edit `lambda_src/ingest_handler.py`:
```python
if crowd_count > 80:    # Critical
elif crowd_count > 50:  # Busy
```

### After a redeploy (new API Gateway URL)

Update `dashboard/src/aws-config.ts` with the new values:
```bash
python3 scripts/manage.py status   # see new values
```
Then rebuild and redeploy:
```bash
python3 scripts/manage.py up
```

---

## Teardown

To destroy all AWS resources:

```bash
python3 scripts/manage.py down
```

> ⚠️ **This permanently deletes:**
> - All DynamoDB zone data
> - The Cognito User Pool and all user accounts
> - S3 logs and frontend files
> - All Lambda functions, API Gateway, CloudFront distribution

The Terraform state in S3 is **not** deleted by this command (it's your recovery point).
