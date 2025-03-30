import json
import boto3
import hashlib
import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Users')

def lambda_handler(event, context):
    try:
        user_id = event.get('queryStringParameters', {}).get('Id')
        if user_id:
            response = table.get_item(Key={'Id': user_id})
            user_data = {
                'username': response['Item'].get('username', 'N/A'),
                'email': response['Item'].get('email', 'N/A')
            }
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(user_data)
            }
        else:
            return {
                'statusCode': 404,
                'message': 'User not found',
                'body': {}
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'message': {'error': str(e)},
            'body': {}
        }
