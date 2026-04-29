#!/usr/bin/env python3
"""
CrowdSync | CloudFormation Operations Manager
---------------------------------------------
A unified interface to plan, deploy, destroy, and simulate
your AWS CloudFormation infrastructure and React frontend.

Usage:
    python3 manage.py [command]

Commands:
    plan      Preview changes to AWS infrastructure without applying them.
    apply     Build and deploy everything (Infrastructure + React UI).
    destroy   Tear down all AWS infrastructure and empty S3 buckets.
    simulate  Start the real-time crowd data simulator.
"""

import sys
import subprocess
import json
import argparse
from pathlib import Path

# --- Configuration ---
PROJECT_NAME = "crowd-monitoring"
ENVIRONMENT = "dev"
REGION = "eu-west-2"
WAF_REGION = "us-east-1"

# Load local .env if it exists
def load_env():
    import os
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.strip() and not line.startswith("#"):
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()

load_env()
import os # Ensure os is imported for later use

MAIN_STACK = f"{PROJECT_NAME}-main-{ENVIRONMENT}"
WAF_STACK = f"{PROJECT_NAME}-waf-{ENVIRONMENT}"
ARTIFACT_BUCKET = f"{PROJECT_NAME}-cfn-artifacts-{ENVIRONMENT}"
ROOT_DIR = Path(__file__).parent.parent.resolve()
CFN_DIR = Path(__file__).parent.resolve()
DASHBOARD_DIR = ROOT_DIR / "dashboard"

# --- Utility Functions ---
def run_cmd(cmd, cwd=CFN_DIR, check=True):
    print(f"\033[0;36m[Running]\033[0m {cmd}")
    result = subprocess.run(cmd, cwd=cwd, shell=True)
    if check and result.returncode != 0:
        print(f"\033[0;31m[Error]\033[0m Command failed with exit code {result.returncode}.")
        sys.exit(result.returncode)
    return result

def get_cfn_output(stack_name, output_key, region=REGION):
    cmd = f'aws cloudformation describe-stacks --stack-name {stack_name} --region {region} --query "Stacks[0].Outputs[?OutputKey==\'{output_key}\'].OutputValue" --output text'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    val = result.stdout.strip()
    if val == "None" or not val:
        return ""
    return val

def get_frontend_bucket():
    cmd = f'aws cloudformation describe-stack-resources --stack-name {MAIN_STACK} --region {REGION} --query "StackResources[?LogicalResourceId==\'FrontendBucket\'].PhysicalResourceId" --output text'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def empty_s3_bucket(bucket_name):
    if bucket_name and "None" not in bucket_name:
        print(f"Emptying S3 bucket: {bucket_name}")
        subprocess.run(f"aws s3 rm s3://{bucket_name} --recursive --region {REGION}", shell=True)

# --- Commands ---
def plan():
    print("\n\033[1;33m--- PLANNING INFRASTRUCTURE ---\033[0m")
    # Ensure artifact bucket exists for plan upload
    subprocess.run(f"aws s3api head-bucket --bucket {ARTIFACT_BUCKET} --region {REGION} 2>/dev/null || aws s3 mb s3://{ARTIFACT_BUCKET} --region {REGION}", shell=True)
    
    run_cmd("sam build --template-file template.yaml")
    run_cmd(f"sam deploy --template-file .aws-sam/build/template.yaml --stack-name {MAIN_STACK} --s3-bucket {ARTIFACT_BUCKET} --region {REGION} --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM --parameter-overrides ProjectName={PROJECT_NAME} Environment={ENVIRONMENT} --no-execute-changeset")

def apply():
    print("\n\033[1;32m--- APPLYING INFRASTRUCTURE & UI ---\033[0m")
    # 1. Artifact Bucket
    print("Ensuring artifact bucket exists...")
    subprocess.run(f"aws s3api head-bucket --bucket {ARTIFACT_BUCKET} --region {REGION} 2>/dev/null || aws s3 mb s3://{ARTIFACT_BUCKET} --region {REGION}", shell=True)
    
    # 2. WAF Deploy
    print("\nDeploying Global WAF...")
    run_cmd(f"aws cloudformation deploy --template-file waf-global.yaml --stack-name {WAF_STACK} --region {WAF_REGION} --parameter-overrides ProjectName={PROJECT_NAME} Environment={ENVIRONMENT} --no-fail-on-empty-changeset")
    
    # 3. Main Infrastructure Deploy
    print("\nBuilding and Deploying Main Infrastructure...")
    run_cmd("sam build --template-file template.yaml")
    run_cmd(f"sam package --output-template-file packaged.yaml --s3-bucket {ARTIFACT_BUCKET} --region {REGION}")
    run_cmd(f"sam deploy --template-file packaged.yaml --stack-name {MAIN_STACK} --region {REGION} --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM --parameter-overrides ProjectName={PROJECT_NAME} Environment={ENVIRONMENT} --no-fail-on-empty-changeset")

    # 4. Extract Outputs & Inject into React
    print("\nExtracting dynamic AWS outputs...")
    user_pool_id = get_cfn_output(MAIN_STACK, "UserPoolId")
    client_id = get_cfn_output(MAIN_STACK, "UserPoolClientId")
    api_url = get_cfn_output(MAIN_STACK, "ApiUrl")
    appsync_url = get_cfn_output(MAIN_STACK, "AppSyncUrl")
    frontend_bucket = get_frontend_bucket()

    aws_config_path = DASHBOARD_DIR / "src" / "aws-config.ts"
    config_content = f"""// Auto-generated by manage.py — do not edit manually
const awsConfig = {{
    Auth: {{
        region: '{REGION}',
        userPoolId: '{user_pool_id}',
        userPoolWebClientId: '{client_id}',
    }},
    API: {{
        endpoints: [
            {{
                name: 'CrowdMonitorAPI',
                endpoint: '{api_url}',
                region: '{REGION}',
            }}
        ]
    }},
    aws_appsync_graphqlEndpoint: '{appsync_url}',
    aws_appsync_region: '{REGION}',
    aws_appsync_authenticationType: 'AMAZON_COGNITO_USER_POOLS',
}}

export default awsConfig;
"""
    aws_config_path.write_text(config_content)
    print(f"\033[0;32m[✓] React config updated dynamically!\033[0m")

    # 5. Build and Deploy React
    print("\nBuilding React Dashboard...")
    run_cmd("npm install", cwd=DASHBOARD_DIR)
    run_cmd("npm run build", cwd=DASHBOARD_DIR)
    
    print(f"\nSyncing to S3 ({frontend_bucket})...")
    run_cmd(f"aws s3 sync dist/ s3://{frontend_bucket} --delete", cwd=DASHBOARD_DIR)
    
    cloudfront_url = get_cfn_output(MAIN_STACK, "CloudFrontUrl")
    # 6. Seed Admin User
    seed_user(user_pool_id)

    print(f"\n\033[1;32m✥ DEPLOYMENT COMPLETE ✥\033[0m")
    print(f"Live Dashboard: {cloudfront_url}\n")

def status():
    print("\n\033[1;36m--- CROWDSYNC INFRASTRUCTURE STATUS ---\033[0m")
    
    # Refresh logic
    try:
        cmd = f'aws cloudformation describe-stacks --stack-name {MAIN_STACK} --region {REGION} --query "Stacks[0].Outputs" --output json'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            outputs = {item['OutputKey']: item['OutputValue'] for item in json.loads(result.stdout)}
            
            print(f"\n🚀 \033[1;37mDashboard URL:\033[0m   {outputs.get('CloudFrontUrl', 'N/A')}")
            print(f"🔗 \033[1;37mAPI Endpoint:\033[0m    {outputs.get('ApiUrl', 'N/A')}")
            print(f"📡 \033[1;37mGraphQL URL:\033[0m     {outputs.get('AppSyncUrl', 'N/A')}")
            print("-" * 60)
            print(f"🆔 \033[1;37mUserPool ID:\033[0m     {outputs.get('UserPoolId', 'N/A')}")
            print(f"🔑 \033[1;37mClient ID:\033[0m       {outputs.get('UserPoolClientId', 'N/A')}")
            print("-" * 60)
            print("\033[1;32mStatus: ONLINE\033[0m")
        else:
            print("\033[1;31mStatus: OFFLINE (Stack not found)\033[0m")
    except Exception as e:
        print(f"\033[1;31mError checking status: {str(e)}\033[0m")

def destroy():
    print("\n\033[1;31m--- DESTROYING INFRASTRUCTURE ---\033[0m")
    confirm = input("Are you sure you want to completely tear down everything? (y/N): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        sys.exit(0)
    
    # CloudFormation cannot delete non-empty S3 buckets. We must empty them first.
    frontend_bucket = get_frontend_bucket()
    if frontend_bucket:
        empty_s3_bucket(frontend_bucket)
        
    # Also empty the Analytics bucket (which stores historical pulses)
    analytics_bucket = get_cfn_output(MAIN_STACK, "AnalyticsBucketName") # I should add this output to template.yaml
    if not analytics_bucket:
        # Fallback search if output isn't available yet
        cmd = f'aws cloudformation describe-stack-resources --stack-name {MAIN_STACK} --region {REGION} --query "StackResources[?LogicalResourceId==\'AnalyticsBucket\'].PhysicalResourceId" --output text'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        analytics_bucket = result.stdout.strip()
    
    if analytics_bucket and "None" not in analytics_bucket:
        empty_s3_bucket(analytics_bucket)
        
    empty_s3_bucket(ARTIFACT_BUCKET)

    print("\nDeleting Main Infrastructure...")
    run_cmd(f"sam delete --stack-name {MAIN_STACK} --region {REGION} --no-prompts")

    print("\nDeleting Global WAF...")
    run_cmd(f"aws cloudformation delete-stack --stack-name {WAF_STACK} --region {WAF_REGION}")
    
    print("\n\033[1;32m✥ DESTROY COMPLETE ✥\033[0m")

def seed_user(user_pool_id):
    """Creates a default admin user for the dashboard."""
    print(f"\nSeeding Admin User in Pool: {user_pool_id}...")
    email = "sakaroncloud@gmail.com"
    password = os.environ.get("DASHBOARD_PASSWORD", "CrowdSync123!") # Fallback for local use
    
    # Check if user exists
    check_user = subprocess.run(f"aws cognito-idp admin-get-user --user-pool-id {user_pool_id} --username {email} --region {REGION}", shell=True, capture_output=True)
    
    if check_user.returncode != 0:
        print(f"Creating user {email}...")
        subprocess.run(f"aws cognito-idp admin-create-user --user-pool-id {user_pool_id} --username {email} --user-attributes Name=email,Value={email} Name=email_verified,Value=true --message-action SUPPRESS --region {REGION}", shell=True)
        subprocess.run(f"aws cognito-idp admin-set-user-password --user-pool-id {user_pool_id} --username {email} --password \"{password}\" --permanent --region {REGION}", shell=True)
        print(f"Success! Admin account created for {email}")
    else:
        print("Admin user already exists.")

def simulate():
    print("\n\033[1;36m--- STARTING SIMULATOR ---\033[0m")
    run_cmd("python3 simulate.py", cwd=CFN_DIR)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CrowdSync CloudFormation Orchestrator")
    parser.add_argument("command", choices=["plan", "apply", "status", "destroy", "simulate"], help="Action to perform")
    
    args = parser.parse_args()
    
    try:
        if args.command == "plan":
            plan()
        elif args.command == "apply":
            apply()
        elif args.command == "status":
            status()
        elif args.command == "destroy":
            destroy()
        elif args.command == "simulate":
            simulate()
    except KeyboardInterrupt:
        print("\n\n\033[1;33m🛑 Execution interrupted by user. Returning to Mission Control...\033[0m")
        sys.exit(0)
