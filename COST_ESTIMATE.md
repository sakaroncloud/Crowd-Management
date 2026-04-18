# ✥ CrowdSync Cost Estimation (eu-west-2) ✥

This document provides a detailed breakdown of the projected operational costs for the CrowdSync platform within the **AWS London (eu-west-2)** region.

## 📊 High-Density Event Scenario
To provide a realistic baseline, the following estimates are calculated for a **Single High-Density Event**:
- **Venue Capture**: 10,000 Concurrent Devices
- **Heartbeat Frequency**: 1 Pulse Every 10 Seconds
- **Event Duration**: 4 Hours (Active Ingestion)
- **Total Load**: **14,400,000 Ingestion Events**

---

## 💸 Cost Breakdown by Service

| Service | Component | Quantity | Unit Rate | Projected Cost |
| :--- | :--- | :--- | :--- | :--- |
| **API Gateway** | HTTP API Ingestion | 14.4M Requests | $1.29 / 1M | **$18.58** |
| **SQS** | Standard Queue (Send/Receive) | 28.8M API Calls | $0.40 / 1M | **$11.52** |
| **Lambda** | Ingest & Notifier Execs | 1.44M Invocations | $0.20 / 1M + Dur | **$1.79** |
| **DynamoDB** | On-Demand (Writes/Reads) | 14.4M WRU / 500k RRU | $1.25 (W) / $0.25 (R) | **$18.13** |
| **AppSync** | Real-time Updates (WS) | 14.4M Updates | $0.08 / 1M | **$1.15** |
| **CloudFront** | Data Transfer Out | 20 GB | $0.085 / GB | **$1.70** |
| **AWS WAF** | Web ACL + Rule Processing | 14.4M Req + Base | $0.60/1M + Static | **$18.64** |
| **Monitoring** | CloudWatch Metrics & Alarms | Alarms + Metrics | Fixed/Variable | **$2.50** |
| **Cognito** | Identity (MAUs) | < 50,000 MAUs | $0.00 (Free Tier) | **$0.00** |
| **TOTAL** | | | | **$74.01** |

> [!NOTE]
> Prices reflect standard **eu-west-2 (London)** rates as of 2024/2025. Costs are highly dependent on the "Pulse Frequency". Reducing heartbeat to 30s would divide major variable costs by 3.

---

## 📈 Scalability Economics

### **Cost per 1,000 Attendees**
In a 4-hour window, the cost per 1,000 attendees is approximately **$7.40**.

### **Free Tier Optimization**
- **Lambda**: First 1M requests/month are free.
- **SQS**: First 1M requests/month are free.
- **Cognito**: First 50,000 monthly active users are free.
- **AppSync**: Includes 250,000 query/mutations free/month for first 12 months.

---

## 🛠️ Infrastructure Efficiency Strategies

1.  **Batching**: API Gateway to SQS integration consumes 1 request, while Lambda processes 10 messages in a single execution, reducing invocation costs by 90%.
2.  **On-Demand Storage**: DynamoDB is configured in `PAY_PER_REQUEST` mode, meaning zero costs when no events are running.
3.  **Global Edge**: Static assets are served via CloudFront, significantly reducing compute load on backends for dashboard visualization.

---
*✥ Documented for Financial Transparency and Operational Scale ✥*
