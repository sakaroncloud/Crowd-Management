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
METADATA_TABLE = os.environ.get('METADATA_TABLE')
BUCKET_NAME = os.environ.get('BUCKET_NAME')
TOPIC_ARN = os.environ.get('TOPIC_ARN')

def get_zone_metadata(zone_id):
    """Fetch capacity and metadata for a zone."""
    try:
        table = dynamodb.Table(METADATA_TABLE)
        response = table.get_item(Key={'zoneId': zone_id})
        return response.get('Item', {})
    except Exception as e:
        print(f"Error fetching metadata for {zone_id}: {e}")
        return {}

def process_record(record_body):
    """Logic to process a single telemetry record."""
    body = json.loads(record_body)
    zone_id = body.get('zoneId')
    crowd_count = body.get('crowdCount')
    
    if not zone_id or crowd_count is None:
        print(f"Invalid record data: {record_body}")
        return
    
    # 0. Fetch Metadata for dynamic thresholds
    metadata = get_zone_metadata(zone_id)
    capacity = int(metadata.get('capacity', 100))
    
    # Threshold logic (Percentage based)
    occupancy_rate = (crowd_count / capacity) * 100
    
    status = "Normal"
    action = "No Action"
    
    if occupancy_rate > 90:
        status = "Critical"
        action = "Restrict Entry / Redirect Flow"
    elif occupancy_rate > 70:
        status = "Busy"
        action = "Monitor closely"
        
    timestamp = datetime.datetime.utcnow().isoformat() + 'Z'
    
    # 1. Update DynamoDB
    table = dynamodb.Table(TABLE_NAME)
    table.put_item(
        Item={
            'zoneId': zone_id,
            'crowdCount': crowd_count,
            'capacity': capacity,
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
    
    print(f"Processed record for {zone_id}: {status}")

def lambda_handler(event, context):
    """SQS Triggered Handler."""
    print(f"Received SQS event with {len(event.get('Records', []))} records.")
    
    for record in event.get('Records', []):
        try:
            process_record(record['body'])
        except Exception as e:
            print(f"Error processing record {record['messageId']}: {str(e)}")
            # Re-rising error would cause the whole batch to retry if not using partial failures
            # For now, we log and continue, but in high-integrity systems we might use partial results
            raise e 
    
    return {
        'message': 'Successfully processed batch'
    }
