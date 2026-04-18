import boto3
import time

client = boto3.client('logs')
log_group = '/aws/lambda/crowd-monitoring-notifier-dev'

try:
    streams = client.describe_log_streams(
        logGroupName=log_group,
        orderBy='LastEventTime',
        descending=True,
        limit=1
    )

    if not streams['logStreams']:
        print("No log streams found.")
    else:
        stream_name = streams['logStreams'][0]['logStreamName']
        events = client.get_log_events(
            logGroupName=log_group,
            logStreamName=stream_name,
            limit=20
        )
        for event in events['events']:
            print(f"[{time.strftime('%H:%M:%S', time.gmtime(event['timestamp']/1000.0))}] {event['message'].strip()}")
except Exception as e:
    print(f"Error: {e}")
