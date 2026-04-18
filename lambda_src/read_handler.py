import json
import boto3
import os
from decimal import Decimal

# Initialize clients
dynamodb = boto3.resource('dynamodb')

# Custom encoder to handle DynamoDB Decimal types
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super(DecimalEncoder, self).default(obj)

# Load environment variables
TABLE_NAME = os.environ.get('TABLE_NAME')
METADATA_TABLE = os.environ.get('METADATA_TABLE')

def lambda_handler(event, context):
    """
    AppSync Data Source: Fetches zones and merges with metadata.
    """
    print(f"DEBUG: GraphQL Read Request Triggered. Info: {event.get('info', {}).get('fieldName')}")
    
    try:
        table = dynamodb.Table(TABLE_NAME)
        meta_table = dynamodb.Table(METADATA_TABLE)
        
        # 1. Fetch all metadata (capacities, etc.)
        meta_response = meta_table.scan()
        metadata_map = {item['zoneId']: item for item in meta_response.get('Items', [])}
        
        def merge_metadata(item):
            if not item: return item
            zone_id = item.get('zoneId')
            meta = metadata_map.get(zone_id, {'capacity': 100}) # Default
            return {**item, **meta}

        # 2. Logic for specific zone or all zones
        arguments = event.get('arguments', {})
        zone_id = arguments.get('zoneId')
        
        if zone_id:
            response = table.get_item(Key={'zoneId': zone_id})
            item = response.get('Item')
            if not item:
                return None
            
            return merge_metadata(item)
            
        # Default: list all
        response = table.scan()
        items = response.get('Items', [])
        full_items = [merge_metadata(item) for item in items]
        
        # Convert Decimals to native Python types for AppSync
        return json.loads(json.dumps(full_items, cls=DecimalEncoder))
        
    except Exception as e:
        print(f"Error reading zones: {str(e)}")
        raise e
