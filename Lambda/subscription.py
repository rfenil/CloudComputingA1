import json
import boto3
import uuid
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('subscriptions')

def lambda_handler(event, context):
    try:
        
        if 'body' not in event or not event['body']:
            return generate_response(400, "Request body is missing")

        try:
            body = json.loads(event['body'])
        except json.JSONDecodeError:
            return generate_response(400, "Invalid JSON format")

        
        song_id = body.get('music_id')
        user_id = body.get('user_id')
        typeofrequest = body.get('type')

        
        if not song_id or not user_id:
            return generate_response(400, "Missing required parameters: music_id and user_id")

        print(f"Processing request: Type={typeofrequest}, MusicID={song_id}, UserID={user_id}")

        
        if typeofrequest == "unsubscribe":
            return unsubscribe_user(song_id, user_id)
        elif typeofrequest == "getsubscriptions":
            return get_user_subscriptions(user_id)
        else:
            return create_subscription(song_id, user_id)

    except Exception as e:
        print(f"Error: {str(e)}")
        return generate_response(500, f"Internal server error: {str(e)}")



def unsubscribe_user(song_id, user_id):
    response = table.query(
        IndexName='UserIdIndex', 
        KeyConditionExpression=Key('user_id').eq(user_id) & Key('music_id').eq(song_id)
    )
    
    if response.get('Items'):
        subscription_id = response['Items'][0]['subscription_id']
        table.delete_item(Key={'subscription_id': subscription_id})
        return generate_response(200, "Subscription deleted successfully")
    else:
        return generate_response(404, "Subscription not found")



def get_user_subscriptions(user_id):
    response = table.query(
        IndexName='UserIdIndex', 
        KeyConditionExpression=Key('user_id').eq(user_id)
    )
    
    if response.get('Items'):
        music_ids = [item['music_id'] for item in response['Items']]
        return generate_response(200, {"data": music_ids})
    else:
        return generate_response(404, "No subscriptions found")



def create_subscription(song_id, user_id):
    
    response = table.query(
        IndexName='UserIdIndex', 
        KeyConditionExpression=Key('user_id').eq(user_id) & Key('music_id').eq(song_id)
    )
    
    if response.get('Items'):
        return generate_response(400, "Subscription already exists")

    
    subscription_id = str(uuid.uuid4())
    item = {
        "subscription_id": subscription_id,
        "user_id": user_id,
        "music_id": song_id
    }
    table.put_item(Item=item)
    print(f"New Subscription Created: {item}")
    
    return generate_response(201, {"subscription_id": subscription_id, "message": "Subscription created successfully"})


def generate_response(status_code, message):
    return {
        "statusCode": status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization"
        },
        "body": json.dumps({"message": message} if isinstance(message, str) else message)
    }
