import json
import boto3
import hashlib
import datetime
import uuid
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Users')

def generate_response(status_code, message, data=None):
    return {
        'statusCode': status_code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization"
        },
        'body': json.dumps({'data': data, 'message': message})
    }

def check_email_exists(email):
    response = table.query(
        IndexName='email-index',
        KeyConditionExpression=Key('email').eq(email)
    )
    return 'Items' in response and len(response['Items']) > 0

def get_user_by_email(email):
    response = table.query(
        IndexName='email-index',
        KeyConditionExpression=Key('email').eq(email)
    )
    if response.get('Items'):
        return response['Items'][0]
    else:
        return None

def lambda_handler(event, context):
    try:
        if event['httpMethod'] == 'GET':
            user_id = event.get('queryStringParameters', {}).get('user_id')
            if user_id:
                response = table.get_item(Key={'Id': user_id})
                if 'Item' in response:
                    user_data = {
                        'username': response['Item'].get('username', 'N/A'),
                        'email': response['Item'].get('email', 'N/A')
                    }
                    return generate_response(200, 'User found', user_data)
                else:
                    return generate_response(404, 'User not found')
            else:
                return generate_response(400, 'Missing user_id')

        else:
            body = json.loads(event['body'])
            action_type = body.get('type')

            if action_type == "login":
                email = body['email']
                password = body['password']
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                user = get_user_by_email(email)

                if user is None:
                    return generate_response(401, 'Invalid email')
                
                if user['password'] != hashed_password:
                    return generate_response(401, 'Invalid password')

                user_id = user['Id']
                return generate_response(200, 'Login successful', {'user_id': user_id})

            elif action_type == "register":
                email = body.get('email')
                username = body.get('username')
                password = body.get('password')
                if not email or not username or not password:
                    return generate_response(400, 'Missing required fields')

                if check_email_exists(email):
                    return generate_response(400, 'User already exists')

                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                user_id = str(uuid.uuid4())
                table.put_item(Item={'Id': user_id, 'email': email, 'username': username, 'password': hashed_password})

                return generate_response(201, 'User created successfully', {'user_id': user_id})

            else:
                return generate_response(400, 'Invalid type')

    except Exception as e:
        return generate_response(500, 'Internal server error', {'error': str(e)})
