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
    """Logic to process a single telemetry record with Analytics logging."""
    body = json.loads(record_body)
    zone_id = body.get('zoneId')
    crowd_count = body.get('crowdCount')
    
    if not zone_id or crowd_count is None:
        print(f"Invalid record data: {record_body}")
        return
    
    # 0. Fetch Metadata
    metadata = get_zone_metadata(zone_id)
    capacity = int(metadata.get('capacity', 100))
    
    # Threshold logic
    occupancy_rate = (crowd_count / capacity) * 100
    status = "Normal"
    action = "No Action"
    
    if occupancy_rate > 90:
        status = "Critical"
        action = "Restrict Entry / Redirect Flow"
    elif occupancy_rate > 70:
        status = "Busy"
        action = "Monitor closely"
        
    # 1. Heuristic Predictive Engine (with Hysteresis/Smoothing)
    table = dynamodb.Table(TABLE_NAME)
    prev_item = table.get_item(Key={'zoneId': zone_id}).get('Item', {})
    
    prev_count = int(prev_item.get('crowdCount', crowd_count))
    prev_predicted = prev_item.get('predictedAction', 'Stable')
    # Use TTL or a timestamp to keep the alert "sticky"
    prev_expiry = float(prev_item.get('predictiveExpiry', 0))
    
    velocity = crowd_count - prev_count
    predicted_action = "Stable"
    predictive_expiry = 0
    
    # Check if we should RETAIN an existing alert (Smoothing)
    if prev_predicted != "Stable" and now.timestamp() < prev_expiry and occupancy_rate > 60:
        predicted_action = prev_predicted
        predictive_expiry = prev_expiry
        action = f"PROACTIVE: Monitoring {zone_id} surge"

    # Trigger NEW alert if velocity is high
    if status != "Critical" and occupancy_rate > 70 and velocity > 5:
        predicted_action = f"PREDICTIVE_ALERT: Bottleneck expected (Velocity: +{velocity})"
        predictive_expiry = now.timestamp() + 180 # Stay active for 3 minutes
        action = f"PROACTIVE: Prepare for {zone_id} overflow"
    
    # 2. Speed Layer: Real-time Dashboard Update (via DynamoDB + Stream)
    timestamp = datetime.datetime.utcnow().isoformat() + 'Z'
    table.put_item(
        Item={
            'zoneId': zone_id,
            'crowdCount': crowd_count,
            'capacity': capacity,
            'status': status,
            'action': action,
            'predictedAction': predicted_action,
            'predictiveExpiry': str(predictive_expiry),
            'lastUpdated': timestamp
        }
    )
    
    # 2. Batch Layer: Analytics Data Lake (Partitioned S3)
    # Using Hive-style partitioning for compatibility with pro analytics tools
    now = datetime.datetime.utcnow()
    partition_path = now.strftime('year=%Y/month=%m/day=%d')
    event_id = str(uuid.uuid4())
    
    analytics_payload = {
        'eventId': event_id,
        'zoneId': zone_id,
        'crowdCount': crowd_count,
        'capacity': capacity,
        'occupancyRate': round(occupancy_rate, 2),
        'status': status,
        'timestamp': timestamp,
        'ingestionTime': now.isoformat() + 'Z'
    }
    
    # We append a newline to make it a JSONL (JSON Lines) format
    log_data = json.dumps(analytics_payload) + "\n"
    
    # Save to S3
    s3_key = f"analytics/{partition_path}/{zone_id}/{event_id}.json"
    
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=log_data,
        ContentType='application/x-jsonlines'
    )
    
    # 3. Alert Layer
    if status == "Critical":
        message = f"ANALYTICS ALERT: Zone {zone_id} is at {occupancy_rate}% capacity ({crowd_count}/{capacity})."
        sns.publish(
            TopicArn=TOPIC_ARN,
            Message=message,
            Subject=f"CrowdSync Alert: {zone_id} CRITICAL"
        )
    
    print(f"Processed: {zone_id} | {crowd_count}/{capacity} | {status}")

def lambda_handler(event, context):
    """SQS Triggered Handler."""
    records = event.get('Records', [])
    for record in records:
        try:
            process_record(record['body'])
        except Exception as e:
            print(f"Error processing record: {str(e)}")
            # We don't raise here to allow other records in batch to process, 
            # but in production you'd use a DLQ.
    
    return {'status': 'success', 'processed': len(records)}
