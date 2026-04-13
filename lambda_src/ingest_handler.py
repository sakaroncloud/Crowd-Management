import json
import boto3
import os
import datetime
import uuid

# Initialize clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
sns = boto3.client('sns')

# Load environment variables
TABLE_NAME = os.environ.get('TABLE_NAME')
BUCKET_NAME = os.environ.get('BUCKET_NAME')
TOPIC_ARN = os.environ.get('TOPIC_ARN')

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Parse input
        body = json.loads(event.get('body', '{}'))
        zone_id = body.get('zoneId')
        crowd_count = body.get('crowdCount')
        
        if not zone_id or crowd_count is None:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing zoneId or crowdCount'})
            }
        
        # Threshold logic
        status = "Normal"
        action = "No Action"
        
        if crowd_count > 80:
            status = "Critical"
            action = "Restrict Entry / Redirect Flow"
        elif crowd_count > 50:
            status = "Busy"
            action = "Monitor closely"
            
        timestamp = datetime.datetime.utcnow().isoformat() + 'Z'
        
        # 1. Update DynamoDB
        table = dynamodb.Table(TABLE_NAME)
        table.put_item(
            Item={
                'zoneId': zone_id,
                'crowdCount': crowd_count,
                'status': status,
                'action': action,
                'lastUpdated': timestamp
            }
        )
        
        # 2. Log to S3
        event_id = str(uuid.uuid4())
        log_payload = {
            'eventId': event_id,
            'zoneId': zone_id,
            'crowdCount': crowd_count,
            'status': status,
            'timestamp': timestamp
        }
        
        date_path = datetime.datetime.utcnow().strftime('%Y/%m/%d')
        s3_key = f"logs/{date_path}/{event_id}.json"
        
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=json.dumps(log_payload),
            ContentType='application/json'
        )
        
        # 3. SNS Alert if Critical
        if status == "Critical":
            message = f"CRITICAL CONGESTION ALERT: Zone {zone_id} has reached {crowd_count} people. Action required: {action}."
            sns.publish(
                TopicArn=TOPIC_ARN,
                Message=message,
                Subject=f"Crowd Alert: {zone_id} CRITICAL"
            )
            
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'zoneId': zone_id,
                'status': status,
                'action': action,
                'timestamp': timestamp
            })
        }
        
    except Exception as e:
        print(f"Error processing event: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }

