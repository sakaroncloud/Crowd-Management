import json
import os
import boto3
import urllib.request
import urllib.parse
from datetime import datetime
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.session import Session

# Environment variables
APPSYNC_URL = os.environ.get('APPSYNC_URL')
REGION = os.environ.get('AWS_REGION')

def lambda_handler(event, context):
    print(f"DEBUG: Received {len(event['Records'])} records from DynamoDB")
    
    for record in event['Records']:
        print(f"DEBUG: Event Name: {record['eventName']}")
        if record['eventName'] in ['INSERT', 'MODIFY']:
            new_image = record['dynamodb']['NewImage']
            
            try:
                # Map DynamoDB types to Python values
                zone_id = new_image['zoneId']['S']
                crowd_count = int(new_image['crowdCount']['N'])
                capacity = int(new_image.get('capacity', {'N': '100'})['N'])
                status = new_image['status']['S']
                action = new_image['action']['S']
                last_updated = new_image['lastUpdated']['S']
                
                print(f"DEBUG: Processing Zone {zone_id} ({crowd_count}/{capacity})")
                
                # Send to AppSync
                send_to_appsync(zone_id, crowd_count, capacity, status, action, last_updated)
            except Exception as e:
                print(f"DEBUG ERROR: Failed to parse record: {str(e)}")

def send_to_appsync(zone_id, crowd_count, capacity, status, action, last_updated):
    query = """
    mutation UpdateZone($zoneId: ID!, $crowdCount: Int!, $capacity: Int, $status: String, $action: String, $lastUpdated: String) {
        updateZone(zoneId: $zoneId, crowdCount: $crowdCount, capacity: $capacity, status: $status, action: $action, lastUpdated: $lastUpdated) {
            zoneId
            crowdCount
            capacity
            status
            action
            lastUpdated
        }
    }
    """
    
    variables = {
        "zoneId": zone_id,
        "crowdCount": crowd_count,
        "capacity": capacity,
        "status": status,
        "action": action,
        "lastUpdated": last_updated
    }
    
    payload = json.dumps({
        "query": query,
        "variables": variables
    }).encode('utf-8')
    
    print(f"DEBUG: Pushing to AppSync URL: {APPSYNC_URL}")
    
    # Sign the request using SigV4
    session = Session()
    credentials = session.get_credentials()
    
    request = AWSRequest(
        method='POST',
        url=APPSYNC_URL,
        data=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    SigV4Auth(credentials, 'appsync', REGION).add_auth(request)
    
    headers = dict(request.headers)
    req = urllib.request.Request(APPSYNC_URL, data=payload, headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            resp_body = response.read().decode('utf-8')
            print(f"DEBUG: AppSync Response Code: {response.getcode()}")
            result = json.loads(resp_body)
            if 'errors' in result:
                print(f"DEBUG ERROR: AppSync GraphQL Errors: {json.dumps(result['errors'])}")
            else:
                print(f"DEBUG SUCCESS: AppSync Mutation Accepted for {zone_id}")
    except Exception as e:
        print(f"DEBUG ERROR: Failed to call AppSync endpoint: {str(e)}")
