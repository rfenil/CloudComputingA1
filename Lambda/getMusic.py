import json
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Songs')


def lambda_handler(event, context):
    try:
        headers = event.get('headers', {})
        song_id = headers.get('Id')
        if song_id:
            response = table.get_item(Key={'Id': song_id})
            if 'Item' in response:
                return {
                    'statusCode': 200,
                    'body': json.dumps(response['Item'])
                }
            else:
                return {
                    'statusCode': 404,
                    'body': {},
                    'message':'Song not found'
                }
        else:
            response = table.scan()  
            return {
                'statusCode': 200,
                'body': json.dumps(response.get('Items', []))
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }