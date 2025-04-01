import json
import hashlib
import boto3
from uuid import uuid4
from boto3.dynamodb.conditions import Key
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('users')


class AuthService:

    def __init__(self, event, context, body):
        self.event = event
        self.context = context
        self.body = body

    def _generate_response(self, status_code: int, message: str, data=None):
        return {
            'statusCode': status_code,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            'body': json.dumps({
                'data': data,
                'message': message
            })
        }

    def _get_user_by_email(self, email: str) -> dict:
        try:
            response = table.query(
                IndexName="EmailIndex",
                KeyConditionExpression=Key('email').eq(email))
            if response.get('Items'):
                return response['Items'][-1]
            else:
                return None
        except Exception as error:
            logger.error(f"Error getting user by email: {error}")
            return None

    def _check_email_exists(self, email: str) -> bool:
        try:
            response = table.query(
                IndexName='EmailIndex',
                KeyConditionExpression=Key('email').eq(email))
            return 'Items' in response and len(response['Items']) > 0
        except Exception as error:
            logger.error(f"Error checking email exists: {error}")
            return False

    def login(self) -> dict:
        try:
            email: str = self.body['email']
            password: str = self.body['password']
            if not email or not password:
                return self._generate_response(400, "Missing required fields")

            user: dict = self._get_user_by_email(email)
            if user is None:
                return self._generate_response(401, "Invalid Credentials")

            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if user.get('password') != hashed_password:
                return self._generate_response(401, "Invalid Credentials")

            user_id = user['id']
            return self._generate_response(200, 'Login Successful',
                                           {'user_id': user_id})

        except Exception as error:
            logger.error(f"Error during login: {error}")
            return self._generate_response(500, "Internal Server Error")

    def register(self) -> dict:
        try:
            email: str = self.body['email']
            username: str = self.body['username']
            password: str = self.body['password']

            if not email or not username or not password:
                return self._generate_response(400, 'Missing required fields')

            if self._check_email_exists(email):
                return self._generate_response(409, 'User already exists')

            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            user_id = str(uuid4())
            table.put_item(
                Item={
                    'id': user_id,
                    'email': email,
                    'username': username,
                    'password': hashed_password
                })
            return self._generate_response(201, 'User created successfully',
                                           {'user_id': user_id})
        except Exception as error:
            logger.error(f"Error during registration: {error}")
            return self._generate_response(500, "Internal Server Error")
    
    def get_user(self) -> dict:
        try:
            logger.info("Getting user")
            query_params = self.event.get('queryStringParameters')
            user_id = query_params.get('user_id') if query_params else None
            logger.info(f"Query parameters: {query_params}")
            if not user_id:
                return self._generate_response(400, "Missing user_id in query parameters")
            logger.info(f"User ID: {user_id}")
            response = table.get_item(
                Key={
                    'id': user_id
                }
            )
            
            if 'Item' not in response:
                return self._generate_response(404, "User not found")

            logger.info(f"Got the respons for the user")
            
            user = response['Item']
            
            user_data = {
                'user_id': user['id'],
                'email': user['email'],
                'username': user['username'],
                'subscriptions': user['subscription']
            }
            
            return self._generate_response(200, "User retrieved successfully", user_data)
            
        except Exception as error:
            logger.error(f"Error retrieving user: {error}")
            return self._generate_response(500, "Internal Server Error")


def lambda_handler(event, context):
    try:
        httpMethod = event.get('httpMethod', '')
        path = event.get('path')
        raw_body = event.get('body')
        body = json.loads(raw_body) if isinstance(raw_body, str) else {}
        auth = AuthService(event, context, body)


        if path == "/login" and httpMethod == 'POST':
            return auth.login()
        elif path == "/register" and httpMethod == 'POST':
            return auth.register()
        elif path == "/user" and httpMethod == 'GET':
            logger.info("GET USER")
            return auth.get_user()
        else:
            return auth._generate_response(400, 'Invalid action type')

    except Exception as error:
        logger.error(f"Error in lambda handler: {error}")
        return {
            'statusCode': 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            'body': json.dumps({'message': 'Internal Server Error'})
        }
