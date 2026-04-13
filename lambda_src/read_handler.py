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

def lambda_handler(event, context):
    try:
        table = dynamodb.Table(TABLE_NAME)
        
        # Check if a specific zoneId is requested via path parameter
        path_params = event.get('pathParameters')
        if path_params and path_params.get('id'):
            zone_id = path_params.get('id')
            response = table.get_item(Key={'zoneId': zone_id})
            item = response.get('Item')
            
            if not item:
                return {
                    'statusCode': 404,
                    'headers': {
                        'Content-Type': 'application/json'
                    },
                    'body': json.dumps({'error': f'Zone {zone_id} not found'})
                }
                
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json'
                },
                'body': json.dumps(item, cls=DecimalEncoder)
            }
        
        # Otherwise, return all zones
        response = table.scan()
        items = response.get('Items', [])
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(items, cls=DecimalEncoder)
        }
        
    except Exception as e:
        print(f"Error reading zones: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }

