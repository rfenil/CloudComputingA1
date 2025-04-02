import json
import hashlib
import boto3
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
        logger.info(f"Generating response: {status_code} - {message}")

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
            logger.info(f"Querying user by email: {email}")
            response = table.query(
                IndexName="EmailIndex",
                KeyConditionExpression=Key('email').eq(email))
            if response.get('Items'):
                logger.info("User found in table.")
                return response['Items'][-1]
            else:
                logger.warning("User not found in table.")
                return None
        except Exception as error:
            logger.error(f"Error getting user by email: {error}")
            return None

    def _check_email_exists(self, email: str) -> bool:
        try:
            logger.info(f"Checking if email exists: {email}")
            response = table.query(
                IndexName='EmailIndex',
                KeyConditionExpression=Key('email').eq(email))
            return 'Items' in response and len(response['Items']) > 0
        except Exception as error:
            logger.error(f"Error checking email exists: {error}")
            return False

    def login(self) -> dict:
        try:
            logger.info("Attempting login.")
            email: str = self.body['email']
            password: str = self.body['password']
            logger.info(f"Login request for email: {email}")
            if not email or not password:
                logger.warning("Missing email or password in request.")
                return self._generate_response(400, "Missing required fields")

            user: dict = self._get_user_by_email(email)
            if user is None:
                logger.warning("Login failed: Invalid email.")
                return self._generate_response(401, "Invalid Credentials")

            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if user.get('password') != hashed_password:
                logger.warning("Login failed: Invalid password.")
                return self._generate_response(401, "Invalid Credentials")

            email = user['email']
            return self._generate_response(200, 'Login Successful',
                                           {'Email Address': email})

        except Exception as error:
            logger.error(f"Error during login: {error}")
            return self._generate_response(500, "Internal Server Error")

    def register(self) -> dict:
        try:
            logger.info("Attempting registration.")
            email: str = self.body['email']
            username: str = self.body['username']
            password: str = self.body['password']

            logger.info(f"Registration data received: email={email}, username={username}")
            if not email or not username or not password:
                return self._generate_response(400, 'Missing required fields')

            if self._check_email_exists(email):
                return self._generate_response(409, 'User already exists')

            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            logger.info("Saving user to DynamoDB.")
            table.put_item(
                Item={
                    'email': email,
                    'username': username,
                    'password': hashed_password,
                    'subscription': []
                })
            logger.info(f"User registered successfully: {email}")
            return self._generate_response(201, 'User created successfully',
                                           {'email': email})
        except Exception as error:
            logger.error(f"Error during registration: {error}")
            return self._generate_response(500, "Internal Server Error")
    
    def get_user(self) -> dict:
        try:
            logger.info("Getting user")
            query_params = self.event.get('queryStringParameters')
            email = query_params.get('email') if query_params else None
            logger.info(f"Query parameters: {query_params}")
            if not email:
                logger.warning("Missing email in query parameters.")
                return self._generate_response(400, "Missing user_id in query parameters")
            logger.info(f"Email ID: {email}")
            user = self._get_user_by_email(email)
            
            if not user:
                logger.warning("User not found.")
                return self._generate_response(404, "User not found")

            logger.info(f"Got the respons for the user")
            
            
            user_data = {
                'email': user['email'],
                'username': user['username'],
                'subscriptions': user.get('subscription', []) 
            }
            
            logger.info("User retrieved successfully.")
            return self._generate_response(200, "User retrieved successfully", user_data)
            
        except Exception as error:
            logger.error(f"Error retrieving user: {error}")
            return self._generate_response(500, "Internal Server Error")


def lambda_handler(event, context):
    try:
        httpMethod = event.get('httpMethod', '')
        path = event.get('path')
        logger.info(f"PATH = {path}, HTTP_METHOD = {httpMethod}")
        raw_body = event.get('body')
        body = json.loads(raw_body) if isinstance(raw_body, str) else {}
        auth = AuthService(event, context, body)

        logger.info(f"Body: {body}")

        if path == "/login" and httpMethod == 'POST':
            return auth.login()
        elif path == "/register" and httpMethod == 'POST':
            return auth.register()
        elif path == "/user" and httpMethod == 'GET':
            logger.info("GET USER")
            return auth.get_user()
        else:
            logger.warning("Invalid path or method.")
            return {
                'statusCode': 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers":
                    "Content-Type, Authorization"
                },
                'body': json.dumps({'message': 'Invalid action type'})
            }

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