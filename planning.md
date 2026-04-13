# Crowd Management on AWS — Project Planning

## Project title
**Cost-Efficient AWS Real-Time Crowd Monitoring System with Admin Dashboard for Entertainment Venues**

---

## 1. Project overview

This project proposes a simple AWS-based real-time crowd monitoring system for entertainment venues such as sports arenas, concerts, and event halls. The system receives crowd data for different venue zones, processes it in near real time, stores the latest zone state, generates alerts when a threshold is exceeded, and exposes data to an admin dashboard.

The system is intentionally designed as a **university-friendly prototype**:
- simple to implement,
- cost-efficient,
- secure by default,
- aligned with the **AWS Well-Architected Framework**,
- realistic enough to demonstrate cloud architecture, implementation, costing, and analysis.

---

## 2. Problem statement

Large entertainment venues often experience uneven crowd distribution across entry gates, food courts, seating areas, and stage-access zones. Overcrowding can reduce safety, increase delays, and negatively affect user experience.

The goal of this project is to create a cloud-based solution that:
- monitors crowd count by zone,
- identifies congestion,
- stores current and historical data,
- sends alerts to administrators,
- provides an admin dashboard for operational visibility.

---

## 3. Scope

### In scope
- Simulated crowd data input
- Real-time event ingestion
- Rule-based congestion detection
- Admin dashboard backend APIs
- Current zone state storage
- Alerting for critical congestion
- Historical log storage
- Terraform-based AWS infrastructure
- Basic security hardening
- High availability through managed AWS services

### Out of scope
- Real camera integration
- Computer vision model training
- Mobile end-user app
- Complex prediction engine
- Multi-region deployment
- Physical IoT device integration

---

## 4. Functional requirements

1. The system shall accept crowd data for multiple venue zones.
2. The system shall process incoming events in near real time.
3. The system shall classify zone status as Normal, Busy, or Critical.
4. The system shall store the latest zone state.
5. The system shall store historical event records.
6. The system shall generate alerts for critical congestion.
7. The system shall provide APIs for the admin dashboard.
8. The admin dashboard shall display live crowd information and alerts.

---

## 5. Non-functional requirements

1. **Security**: only authorized components can access AWS resources.
2. **Availability**: the system should remain accessible during normal cloud service disruptions within a region.
3. **Reliability**: failed events should be logged and retried where appropriate.
4. **Fault tolerance**: use managed services that recover automatically from instance-level failure.
5. **Cost efficiency**: prefer serverless and pay-per-use components.
6. **Maintainability**: infrastructure should be reproducible using Terraform.
7. **Performance**: event processing should complete within seconds for dashboard visibility.

---

## 6. Final architecture

### Data flow
1. Simulated crowd data is sent to **Amazon API Gateway**.
2. API Gateway invokes **AWS Lambda**.
3. Lambda evaluates crowd thresholds.
4. Lambda writes current state to **Amazon DynamoDB**.
5. Lambda writes historical logs to **Amazon S3**.
6. Lambda publishes alerts to **Amazon SNS** when a zone becomes Critical.
7. The admin dashboard reads data through API Gateway + Lambda.

### Core AWS services
- **API Gateway** — public API entry point
- **AWS Lambda** — event processing and read APIs
- **DynamoDB** — latest zone state
- **Amazon S3** — historical logs
- **Amazon SNS** — alert notifications
- **Amazon CloudWatch** — logs, metrics, alarms
- **IAM** — access control
- **KMS** — encryption for supported services

---

## 7. Why this architecture

This design is chosen because it is:
- simpler than using Kafka or Kinesis,
- cheaper for a student prototype,
- easier to explain in a report and presentation,
- naturally scalable with serverless services,
- aligned with AWS Well-Architected principles.

---

## 8. Security design

### Identity and access management
- Use **least privilege IAM roles**.
- Lambda gets only the permissions it needs:
  - write/read DynamoDB table,
  - put objects to S3 logs bucket,
  - publish to SNS topic,
  - write logs to CloudWatch.

### API protection
- Start with HTTP API for simplicity.
- Restrict public access where possible.
- Add request validation in Lambda.
- For future improvement: add JWT or Cognito auth for the admin dashboard.

### Encryption
- Enable **server-side encryption**:
  - S3 with SSE-S3 or SSE-KMS,
  - DynamoDB encryption at rest,
  - SNS encryption at rest where required.
- Enforce HTTPS in API access.

### Secrets
- Do not hardcode secrets in Terraform or Lambda.
- If secrets are later needed, store them in **AWS Systems Manager Parameter Store** or **Secrets Manager**.

### Logging and auditing
- Enable CloudWatch Logs for Lambda and API Gateway.
- Capture failures and alert-worthy events.

---

## 9. High availability, reliability, and fault tolerance

### High availability
This system uses managed AWS services that are regionally resilient:
- API Gateway is managed and highly available,
- Lambda scales automatically across AWS-managed infrastructure,
- DynamoDB is multi-AZ by design within a region,
- SNS is managed and highly available,
- S3 is highly durable and resilient.

### Reliability
- CloudWatch monitors function errors and API failures.
- Lambda code should handle invalid payloads safely.
- DynamoDB stores latest known valid zone state.
- S3 keeps history for audit and replay.

### Fault tolerance
- No single EC2 instance exists, so there is no VM single point of failure.
- Serverless services reduce infrastructure failure handling burden.
- Lambda should handle partial failures gracefully.
- Failed writes should be logged for later analysis.

### Simple note for report
This project achieves fault tolerance mainly by using fully managed AWS services rather than self-managed servers.

---

## 10. Well-Architected Framework alignment

### 10.1 Operational Excellence
- Infrastructure defined as code using Terraform
- Centralized logging with CloudWatch
- Clear deployment and rollback process
- Small modular services for easier changes

### 10.2 Security
- IAM least privilege
- Encryption at rest and in transit
- Input validation in Lambda
- Private configuration for environment variables where needed

### 10.3 Reliability
- Managed serverless services
- Monitoring and alarms
- Durable historical storage in S3
- Service decoupling through clear API boundaries

### 10.4 Performance Efficiency
- Lambda scales automatically on request volume
- DynamoDB provides low-latency lookups
- Minimal architecture avoids unnecessary bottlenecks

### 10.5 Cost Optimization
- No always-on EC2 servers
- Pay-per-use model
- S3 for cheap long-term storage
- Small footprint for student prototype

### 10.6 Sustainability
- Serverless reduces idle compute waste
- Efficient managed services minimize overprovisioning

---

## 11. Terraform implementation plan

### Recommended folder structure

```text
terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── providers.tf
├── terraform.tfvars
├── versions.tf
├── locals.tf
├── modules/
│   ├── api_gateway/
│   ├── lambda/
│   ├── dynamodb/
│   ├── s3/
│   ├── sns/
│   ├── iam/
│   └── cloudwatch/
└── lambda_src/
    ├── ingest_handler.py
    └── read_handler.py
```

### Phase 1: Base infrastructure
Create:
- provider and backend config
- tagging strategy
- KMS key if needed
- S3 bucket for logs/history
- DynamoDB table
- SNS topic

### Phase 2: IAM
Create:
- Lambda execution role
- policy attachments for DynamoDB, S3, SNS, CloudWatch

### Phase 3: Lambda
Create:
- ingestion Lambda
- read/query Lambda
- environment variables for table name, bucket name, topic ARN

### Phase 4: API Gateway
Create:
- `POST /crowd-data`
- `GET /zones`
- `GET /zone/{id}`
- `GET /alerts` (optional)

### Phase 5: Monitoring
Create:
- CloudWatch log groups
- metric alarms for Lambda errors
- alarm for API 5XX where practical

---

## 12. Terraform resource planning

### Likely Terraform resources

#### Core
- `aws_dynamodb_table`
- `aws_s3_bucket`
- `aws_sns_topic`
- `aws_lambda_function`
- `aws_iam_role`
- `aws_iam_role_policy`
- `aws_cloudwatch_log_group`
- `aws_apigatewayv2_api`
- `aws_apigatewayv2_integration`
- `aws_apigatewayv2_route`
- `aws_apigatewayv2_stage`

#### Helpful additions
- `aws_s3_bucket_versioning`
- `aws_s3_bucket_server_side_encryption_configuration`
- `aws_cloudwatch_metric_alarm`
- `aws_lambda_permission`

---

## 13. API design

### POST /crowd-data
Receives:
```json
{
  "zoneId": "GateA",
  "crowdCount": 85,
  "timestamp": "2026-04-12T18:30:00Z"
}
```

Response:
```json
{
  "zoneId": "GateA",
  "status": "Critical",
  "action": "Restrict Entry"
}
```

### GET /zones
Returns all latest zone states.

### GET /zone/{id}
Returns one zone’s current state.

---

## 14. Business rules

### Threshold logic
- `0 - 50` → Normal
- `51 - 80` → Busy
- `81+` → Critical

### Action logic
- Normal → No Action
- Busy → Monitor
- Critical → Restrict Entry / Redirect Flow

This keeps implementation simple and easy to justify.

---

## 15. Data model

### DynamoDB table: `crowd_zones`
Suggested primary key:
- `zoneId` (String)

Attributes:
- `crowdCount`
- `status`
- `action`
- `lastUpdated`

### S3 object format
Store JSON logs by date:
```text
s3://<bucket>/logs/YYYY/MM/DD/<event-id>.json
```

---

## 16. Dashboard plan

### Dashboard features
- live zone cards
- crowd count per zone
- status badges
- recent alerts
- simple trend chart from historical data

### Dashboard security
For prototype:
- basic frontend with restricted use
- keep sensitive actions out of public access

For future:
- Cognito or external auth

---

## 17. Cost planning

### Expected low-cost design
- API Gateway: low traffic cost
- Lambda: likely within free tier for prototype use
- DynamoDB: on-demand small scale
- S3: very low cost for small logs
- SNS: near-zero for low notifications
- CloudWatch: low but monitor usage

### Cost optimization decisions
- no EC2
- no Kafka or MSK
- no Kinesis for this prototype
- no always-on servers

---

## 18. Deployment steps

1. Create AWS account / configure credentials
2. Initialize Terraform
3. Review plan
4. Apply infrastructure
5. Deploy Lambda code
6. Test `POST /crowd-data`
7. Verify DynamoDB updates
8. Verify S3 logs
9. Verify SNS alert
10. Test `GET /zones`
11. Capture screenshots for report

---

## 19. Testing plan

### Functional tests
- Valid crowd event is processed successfully
- Busy and Critical thresholds are classified correctly
- DynamoDB is updated
- S3 log is created
- SNS alert triggers for Critical zone

### Negative tests
- Missing zoneId
- Invalid crowdCount
- Invalid JSON payload

### Reliability tests
- Repeat multiple requests
- Confirm Lambda still responds
- Confirm latest state is updated consistently

---

## 20. Risks and mitigations

### Risk: Overcomplicated architecture
Mitigation: keep to serverless core services only.

### Risk: IAM misconfiguration
Mitigation: use least privilege and test incrementally.

### Risk: Terraform deployment issues
Mitigation: modularize code and apply in small steps.

### Risk: Cost overrun
Mitigation: stay on free tier and low traffic; monitor CloudWatch and billing.

### Risk: Time constraints
Mitigation: prioritize core flow before dashboard polish.

---

## 21. Deliverables mapping

This project supports the report structure with:
- introduction and problem domain,
- project plan,
- requirements gathering,
- cloud architecture,
- implementation,
- costing,
- reflection and future improvements.

---

## 22. Suggested future improvements

- Add Cognito authentication for dashboard access
- Add WebSocket updates for live dashboard push
- Add dead-letter queue or retry strategy
- Add analytics dashboard using QuickSight
- Add computer vision integration in a future version
- Add multi-region disaster recovery design

---

## 23. Suggested implementation order

### Minimum viable build
1. DynamoDB
2. Lambda ingestion
3. API Gateway POST route
4. S3 logging
5. SNS alert
6. Lambda read API
7. API Gateway GET route
8. Simple admin dashboard

### If time is short
Prioritize:
- POST flow
- DynamoDB
- alert logic
- screenshots

---

## 24. Notes for Terraform code generation

When generating Terraform:
- use variables for region, project name, table name, bucket name
- tag all resources
- keep modules small and reusable
- avoid unnecessary complexity
- output key endpoints and resource names
- separate Lambda code package from Terraform logic

---

## 25. Final summary

This project should be implemented as a **simple, secure, serverless AWS prototype**. The design should emphasize:
- cost efficiency,
- managed services,
- Terraform-based reproducibility,
- secure defaults,
- reliability through AWS-managed components,
- alignment with the AWS Well-Architected Framework.

The best strategy for full-mark potential is to keep the implementation small, but justify every architecture decision clearly.
