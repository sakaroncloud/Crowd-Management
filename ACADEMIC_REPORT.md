<COVER PAGE PLACEHOLDER>
---
Title: CrowdSync: Real-Time Cloud Architecture for High-Density Venue Analytics
Student Name: [PLACEHOLDER: Insert Name]
Student ID: [PLACEHOLDER: Insert ID]
Module: [PLACEHOLDER: Insert Module]
Date: [PLACEHOLDER: Insert Date]
---

## Abstract
This report details the architectural design and implementation of CrowdSync, a highly scalable, serverless venue intelligence platform. Developed to address the challenges of high-density crowd management, CrowdSync leverages an event-driven AWS architecture to ingest, process, and visualize telemetry data in real time. The implementation demonstrates best practices in cloud computing, utilizing services such as AWS API Gateway, SQS, Lambda, DynamoDB, AppSync, and S3 to achieve sub-300ms latency, high availability, and secure data durability.

## Table of Contents
1. Introduction
2. Project Plan
3. Requirements Gathering
   3.1 Functional Requirement Specification
   3.2 Non-Functional Requirement Specification
4. Data Centre
   4.1 Type
   4.2 Site Selection
   4.3 Topology
5. Cloud Architecture
   5.1 Choice of Cloud Platform & Rationale
   5.2 Rationale for Choice of Services
   5.3 Cloud System Architecture
6. Cloud Implementation
   6.1 Solution Implementation & Justification
   6.2 Implementation Screenshots
7. Costing
8. Analysis and Reflection
   8.1 Evaluation & Critical Appraisal
   8.2 Maintenance, Evolution, & Compliance
9. References

---

## 1. Introduction
Managing crowd flow in high-density entertainment venues presents a significant challenge. Sudden bottlenecks, overcrowding, and inefficient resource allocation can lead to poor user experiences and critical safety hazards. **CrowdSync** was developed as an advanced, real-time venue intelligence platform to solve these issues. By leveraging IoT telemetry and serverless cloud computing, CrowdSync provides administrators with a "Pulse-to-Pixel" dashboard that monitors occupancy, detects critical thresholds (>90%), and proactively suggests redirection strategies.

## 2. Project Plan

### 2.1 Phases & Milestones
The development of CrowdSync was structured into six agile phases to ensure methodical implementation, validation, and alignment with project milestones:
1.  **Requirements & Problem Definition**: Gathering system specifications for high-throughput crowd monitoring, defining the problem domain, and mapping the core functional and non-functional requirements.
2.  **Architecture & Design**: Defining the dual-track "Lambda Architecture" (Amazon Web Services, 2026c) to handle both real-time alerts and historic batch analytics securely.
3.  **Ingestion & Edge Layer**: Implementing a secure, resilient pipeline starting from local CCTV Edge AI devices, through AWS WAF protection, into an SQS ingestion buffer.
4.  **Data Persistence & Streaming**: Configuring DynamoDB for highly available live state storage and an S3 Data Lake for historic archiving, coupled with DynamoDB Streams for change-data-capture.
5.  **Real-Time Bridge**: Implementing AWS AppSync to relay database changes to the frontend in milliseconds using GraphQL WebSockets (Amazon Web Services, 2026b).
6.  **Dashboard UI & Deployment**: Building a React-based interactive heatmap (Meta Platforms, Inc., 2026) and orchestrating the entire deployment via AWS CloudFormation (SAM) and automated Python scripts for reproducible infrastructure.

### 2.2 Project Progress
The CrowdSync prototype has successfully reached Stage 1 functional maturity. The foundational AWS infrastructure, including the WAF-shielded API Gateway, SQS ingestion buffer, and the dual-write Lambda handler, has been fully deployed and tested. Furthermore, the real-time distribution mechanism utilizing DynamoDB Streams and AWS AppSync has been successfully integrated with a functional React frontend, proving the sub-300ms latency requirement. Currently, minor UI polishing on the React dashboard and rigorous load testing (simulating 10,000+ concurrent devices) are pending. Future enterprise evolution (Stage 2) will focus on integrating machine learning pipelines using Amazon SageMaker to shift from reactive monitoring to proactive crowd surge prediction.

## 3. Requirements Gathering

### 3.1 Functional Requirement Specification
To provide actionable venue intelligence, CrowdSync must fulfill the following functional capabilities:
*   **Real-Time Telemetry Ingestion**: The system must expose a secure endpoint to receive HTTP POST payloads containing zone occupancy data every 10 seconds from IoT sensors.
*   **Live Dashboard Updates**: Administrators must see zone occupancy changes reflected on a visual dashboard map without requiring a manual page refresh.
*   **Threshold Alerting**: The system must automatically detect when a zone's occupancy exceeds 90% of its capacity and flag it as a "Critical" event on the UI.
*   **Predictive Redirection**: Upon detecting a critical bottleneck, the system must intelligently query the current state of all zones and suggest an alternative "Normal" zone to redirect traffic.
*   **Historic Data Archiving**: Every raw telemetry event must be permanently logged and partitioned by date and zone for future analysis.

### 3.2 Non-Functional Requirement Specification
To ensure CrowdSync meets enterprise-grade operational standards, the following non-functional requirements were established:
*   **High Throughput & Scalability**: Capable of dynamically scaling to handle 14.4 million events per 4-hour window (10,000 concurrent devices) without dropping payloads or requiring manual intervention.
*   **Low Latency**: End-to-end processing (from the sensor's API request to the WebSocket update on the dashboard) must complete in under 300 milliseconds.
*   **Security & Zero-Trust**: All public endpoints must be shielded by a Web Application Firewall (WAF) to mitigate Layer 7 attacks. Ingestion must use Edge-side AI to prevent raw video transmission, and internal APIs must enforce strict token-based authentication via SSM. Dashboard access is secured via Amazon Cognito.
*   **Cost-Efficiency**: The infrastructure must utilize a pay-per-use billing model, minimizing compute costs through techniques like SQS batching, and scaling to $0 when the venue is inactive.
*   **High Availability & Fault Tolerance**: The architecture must span multiple Availability Zones (AZs) inherently (via Serverless services) to prevent single points of failure.

## 4. Data Centre

### 4.1 Type
The platform is deployed within a **Hyperscale Public Cloud Data Center** operated by AWS. This model was chosen over an on-premise or co-located private data center because high-density venue analytics inherently experience massive, unpredictable spikes in traffic (e.g., thousands of attendees moving simultaneously during an intermission). A hyperscale data center provides virtually infinite elasticity, allowing CrowdSync to automatically provision immense compute resources on-demand to process traffic bursts, and then scale back down to zero when the venue is empty, converting fixed capital expenditures (CapEx) into highly optimized operational expenditures (OpEx).

### 4.2 Site Selection
The primary deployment region was strategically selected as **AWS London (`eu-west-2`)**, supported by global edge distribution via Amazon CloudFront (`us-east-1` for global WAF rules).
*   **Proximity and Latency**: Deploying in `eu-west-2` minimizes network latency for local European venues, directly supporting the <300ms end-to-end latency requirement.
*   **Data Sovereignty and Compliance**: Keeping sensitive venue telemetry and user authentication data within the UK ensures strict adherence to GDPR and local data protection regulations.
*   **Security Standards**: The architecture enforces TLS 1.3 encryption for all data in transit across REST and WebSocket APIs. Data at rest in DynamoDB and S3 is protected using AWS Key Management Service (KMS) managed encryption, adhering to the principle of least privilege through scoped IAM roles.

### 4.3 Topology (Centralized/Zoned/Top-of-Rack/Multi-tier)
While the serverless abstraction hides physical infrastructure from the developer, the underlying data center employs a **Multi-tier Zoned Topology**. AWS regions are constructed using isolated Availability Zones (AZs). Each AZ consists of one or more discrete data centers, each with redundant power, networking, and connectivity, housed in separate facilities. Internally, AWS utilizes a high-bandwidth, non-blocking **Spine-and-Leaf** network topology to minimize packet latency between racks, which directly supports the project's strict sub-300ms latency requirement. By utilizing serverless components like DynamoDB and SQS, CrowdSync inherently inherits this multi-zoned fault tolerance, automatically replicating data synchronously across multiple facilities without requiring manual configuration.

## 5. Cloud Architecture

### 5.1 Choice of Cloud Platform & Rationale
**Amazon Web Services (AWS)** was selected as the public cloud provider. A 100% Serverless Public Cloud model was chosen because:
*   It eliminates the operational overhead of patching, scaling, and maintaining Virtual Private Clouds (VPCs) or EC2 instances.
*   AWS offers the most mature ecosystem of deeply integrated, event-driven services (Lambda, DynamoDB Streams, SQS) required for high-velocity analytics.

### 5.2 Rationale for Choice of Services
**Architectural Trade-off: SQS over Kinesis Data Streams**
While Amazon Kinesis Data Streams is traditionally considered the industry standard for high-volume streaming, this project strategically selected an SQS-based ingestion model. This decision was driven by three critical factors:
1.  **Bursty Telemetry & Elasticity**: CCTV-based crowd monitoring is inherently "bursty" (e.g., traffic spikes during event intermissions). SQS provides a zero-management "shock absorber" that scales from 0 to thousands of messages per second instantly. Unlike Kinesis, which requires manual or auto-scaling of shards, SQS handles unpredictable peaks with 100% elasticity and zero idle cost.
2.  **Discrete Event Processing**: Our system processes discrete state updates (e.g., "Zone A occupancy: 85%") rather than continuous, high-bandwidth raw data streams. SQS is optimized for this decoupled, event-driven model, ensuring each pulse is processed as an independent, durable task.
3.  **Environmental Constraints**: Initial deployment revealed account-level limitations (`SubscriptionRequiredException`) for Kinesis. Adapting to such constraints is a key real-world engineering competency, and SQS combined with DynamoDB Streams provided a functionally equivalent real-time bridge with significantly lower operational complexity.

### 5.3 Cloud System Architecture
To satisfy the requirements, a highly decoupled, dual-track **Lambda Architecture** was engineered (Amazon Web Services, 2026c).

> [!TIP]
> **[PLACEHOLDER: Insert Architecture Diagram Image]**
> *Ensure you include a caption below the image as per the rubric (e.g., "Figure 1: CrowdSync Serverless Architecture Diagram").*

![Figure 1: CrowdSync Pulse-to-Pixel Architecture](./architecture_final.png)

## 6. Cloud Implementation

### 6.1 Solution Implementation & Justification
The entire AWS infrastructure was implemented using **Infrastructure as Code (IaC)** via the AWS Serverless Application Model (SAM) and CloudFormation (Amazon Web Services, 2026a). 
*   **Automation**: A unified Python orchestrator (`manage.py`) automatically builds the SAM stack, packages the Lambda functions, deploys the CloudFormation changeset, seeds the Cognito Admin user, and deploys the React frontend to an S3/CloudFront CDN. 
*   This approach ensures the environment is reproducible, strictly version-controlled, and immutable, representing industry best practices for cloud deployment.

### 6.2 Implementation Screenshots
> [!NOTE]
> **[IMAGE PLACEHOLDER 1: AWS CloudFormation Stack]**
> *Take a screenshot of the AWS CloudFormation console showing your stack successfully deployed (Status: CREATE_COMPLETE or UPDATE_COMPLETE).*
> 
> *Figure 2: AWS CloudFormation Stack Deployment Success, demonstrating automated Infrastructure-as-Code provisioning.*

> [!NOTE]
> **[IMAGE PLACEHOLDER 2: Amazon SQS Queue]**
> *Take a screenshot of the Amazon SQS console showing your ingestion queue, ideally with some messages visible in the "Messages available" column.*
> 
> *Figure 3: Amazon SQS Ingestion Buffer, acting as the fault-tolerant shock absorber for telemetry spikes.*

> [!NOTE]
> **[IMAGE PLACEHOLDER 3: AWS AppSync GraphQL API]**
> *Take a screenshot of the AWS AppSync console showing your schema or the Queries testing interface.*
> 
> *Figure 4: AWS AppSync GraphQL API interface, bridging the DynamoDB Streams to the React client via WebSockets.*

## 7. Costing
The architecture is heavily optimized for high-density environments, balancing performance with aggressive cost management.

**Baseline**: 10,000 Concurrent Devices, 1 Pulse Every 10 Seconds, 4 Hours duration (Total: 14.4 Million Events).

| Service | Component | Projected Cost | Rationale |
| :--- | :--- | :--- | :--- |
| **API Gateway** | HTTP API Ingestion | **$18.58** | 14.4M requests @ $1.29/M |
| **SQS** | Standard Queue Buffer | **$11.52** | 14.4M requests @ $0.40/M + API calls |
| **S3 Data Lake** | Analytics Ingestion | **$72.00** | 14.4M PUT requests @ $0.005/1K |
| **Lambda** | Logic & Processing | **$2.45** | SQS Batching reduces execution count by 90% |
| **DynamoDB** | Live State Storage | **$18.13** | On-Demand writes/reads for 14.4M events |
| **AppSync** | Real-time Pub/Sub | **$1.15** | WebSocket connection & data transfer |
| **WAF** | Edge Security | **$18.64** | Inspection for 14.4M global requests |
| **Other** | CloudFront & SNS | **$4.20** | CDN egress and alert distribution |
| **TOTAL** | | **$146.67** | Approximately **$0.01 per attendee**. |

*Note: SQS batching acts as a cost-control mechanism, reducing Lambda invocations by up to 90% and preventing massive compute bills during traffic spikes.*

## 8. Analysis and Reflection

### 8.1 Evaluation & Critical Appraisal
**Strengths**: The decoupling of ingestion and processing via a **4-Lambda Architecture** (Authorizer, Ingest, Notifier, and Query) proved highly successful. This separation of concerns ensured that security, ingestion, real-time broadcasting, and data retrieval could scale independently. The use of SQS as a "shock absorber" prevented database throttling, while the custom Query Lambda allowed for seamless merging of live telemetry with zone metadata for the frontend.

**Areas for Improvement**: Currently, the predictive redirection engine runs entirely on the client side (React). In future iterations, implementing Machine Learning on the backend (e.g., using Amazon SageMaker) could analyze historical S3 Data Lake patterns to predict crowd surges *before* they happen, shifting the platform from reactive monitoring to proactive, AI-driven intelligence.

### 8.2 Maintenance, Evolution, & Compliance
Maintaining a high-velocity telemetry system requires continuous monitoring of cloud metrics (via Amazon CloudWatch) to track error rates and SQS queue depth, ensuring the "shock absorber" is functioning efficiently. As the system evolves to meet future business needs, the highly decoupled architecture allows for seamless integration of new features; for instance, the S3 Data Lake can be easily connected to Amazon QuickSight for business intelligence reporting, or integrated with ticketing APIs to correlate zone density with ticket sales. From a compliance perspective, the system inherently aligns with stringent data protection frameworks (e.g., GDPR). Since the IoT sensors transmit anonymous aggregate counts rather than Personally Identifiable Information (PII), regulatory risk is minimized. Furthermore, automated lifecycle policies on the S3 Data Lake ensure that raw telemetry is systematically archived and eventually deleted in accordance with data retention mandates.

## 9. References

Amazon Web Services, 2026a. *AWS Serverless Application Model (SAM) Developer Guide*. [online] Available at: <https://docs.aws.amazon.com/serverless-application-model/> [Accessed 28 Apr. 2026].

Amazon Web Services, 2026b. *Building Real-Time Serverless APIs with AWS AppSync*. [online] Available at: <https://aws.amazon.com/appsync/> [Accessed 28 Apr. 2026].

Amazon Web Services, 2026c. *Implementing Lambda Architecture on AWS*. [online] AWS Architecture Center.

Meta Platforms, Inc., 2026. *React Documentation: Building Interactive UIs*. [online] Available at: <https://react.dev/> [Accessed 28 Apr. 2026].
