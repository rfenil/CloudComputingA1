import boto3
import json
import hashlib
import uuid

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Users')


def check_email_exists(email):
    response = table.query(
        IndexName='email-index',  
        KeyConditionExpression="email = :email",
        ExpressionAttributeValues={":email": email}
    )
    return 'Items' in response and len(response['Items']) > 0


def lambda_handler(event, context):
    body = json.loads(event['body'])
    
    email = body.get('email')
    username = body.get('username')
    password = body.get('password')
    if not email or not username or not password:
        return {'statusCode': 400, 'body': json.dumps({'data':{},'message':'Missing required fields'})}
    
   
    if check_email_exists(email):
        return {'statusCode': 400, 'body': json.dumps({'data':{},'message':'User already exists'})}

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    Id=str(uuid.uuid4())
    table.put_item(Item={'Id':Id,'email': email, 'username': username, 'password': hashed_password})
    
    return {'statusCode': 201, 'body': json.dumps({
                    'data':Id,'message': 'user created successfully'
                })}
