import os
import boto3
import json

ssm = boto3.client('ssm')

def lambda_handler(event, context):
    print(f"Authorizing request: {json.dumps(event)}")
    
    # 1. Get the token from header
    headers = event.get('headers', {})
    received_token = headers.get('x-api-token') or headers.get('X-Api-Token')
    
    if not received_token:
        print("Error: Missing x-api-token header")
        return generate_policy('user', 'Deny', event['routeArn'])

    # 2. Get the valid token from SSM
    param_name = os.environ.get('TOKEN_PARAM_NAME')
    try:
        response = ssm.get_parameter(Name=param_name, WithDecryption=True)
        valid_token = response['Parameter']['Value']
    except Exception as e:
        print(f"Error fetching token from SSM: {str(e)}")
        return generate_policy('user', 'Deny', event['routeArn'])

    # 3. Compare tokens
    if received_token == valid_token:
        print("Authorization successful")
        return { "isAuthorized": True }
    else:
        print("Authorization failed: Token mismatch")
        return { "isAuthorized": False }

def generate_policy(principal_id, effect, resource):
    """Simple response authorizer helper."""
    return { "isAuthorized": effect == 'Allow' }

