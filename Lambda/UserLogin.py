import json
import boto3
import hashlib
import datetime

# SECRET_KEY = "your-secret-key"
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Users')

# def generate_jwt(Id):
#     payload = {
#         "Id": Id,
#         "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
#     }
#     token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
#     return token

def get_user_by_email(email):
    response = table.query(
        IndexName='email-index',
        KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(email)
    )
    
    if response.get('Items'):
        return response['Items'][0]
    else:
        return None

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        email = body['email']
        password = body['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        response = get_user_by_email(email)

        if response is None:
            return {
                'statusCode': 401,
                'body': json.dumps({'data': {}, 'message': 'Invalid email'})
            }

        if response['password'] != hashed_password:
            return {
                'statusCode': 401,
                'body': json.dumps({'data': {}, 'message': 'Invalid password'})
            }

        user_id = response['Id']
        # token = generate_jwt(user_id)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'data': user_id,
                'message': 'Login successful!',
            })
        }

    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'data':{},'message': str(e)})
        }
