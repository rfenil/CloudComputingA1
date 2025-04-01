import boto3
from pydantic import BaseModel, Field
from botocore.exceptions import ClientError
import random

AWS_REGION = "us-east-1"
USER_TABLE_NAME = "users"

class UserItem(BaseModel):
    email: str = Field(..., description="User email")
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")
    subscription: list[str] = Field(default_factory=list, description="List of user subscriptions")

class UserDynamoDBOperations:

    def __init__(self, region_name: str = AWS_REGION):
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table_name = USER_TABLE_NAME
        self.table = None

    def table_exists(self):
        """Check if the table already exists."""
        try:
            table = self.dynamodb.Table(self.table_name)
            table.load() 
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return False
            raise

    def create_table(self):
        """Create the DynamoDB table if it doesn't exist."""
        try:
            if self.table_exists():
                print(f"INFO: Table '{self.table_name}' already exists, using existing table")
                self.table = self.dynamodb.Table(self.table_name)
                return self.table

            print(f"INFO: Creating DynamoDB table '{USER_TABLE_NAME}'")
            self.table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {'AttributeName': 'email', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'email', 'AttributeType': 'S'}
                ],
                ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            )
            self.table.wait_until_exists()
            print(f"SUCCESS: DynamoDB table created successfully: {self.table.item_count}")
            return self.table
        except Exception as e:
            print(f"ERROR: Failed to create DynamoDB table: {str(e)}")
            raise e
    
    def insert_user_data(self, user: UserItem):
        """Insert a user item into the DynamoDB table."""
        try:
            print(f"INFO: Inserting User data for '{user.username}'")
            self.table = self.dynamodb.Table(self.table_name)
            item = {
                'username': user.username,
                'email': user.email,
                'password': user.password,
                'subscription': user.subscription
            }
            self.table.put_item(Item=item)
            print(f"SUCCESS: Inserted User data for '{user.username}'")
        except Exception as e:
            print(f"ERROR: Failed to insert User data: {str(e)}")
            raise e

def insert_sample_users(user_ops: UserDynamoDBOperations):
    sample_usernames = [
        "Prajwal Manjunath", "Emma Miller", "Krish Parekh", "Sophia Smith", "James Johnson",
        "Sophia Davis", "John Williams", "Michael Williams", "Divyam Juneja", "David Lee"
    ]

    sample_users = []
    base_id = 406250700  
    
    for i, username in enumerate(sample_usernames):
        student_id = base_id + i 
        email = f"s{student_id}@student.rmit.edu.au"
        full_username = f"{username}{i}"
        password = str(random.randint(100000, 999999))
        user = UserItem(username=full_username, email=email, password=password, subscription=[])
        sample_users.append(user)
    
    for user in sample_users:
        user_ops.insert_user_data(user)

if __name__ == "__main__":
    try:
        user_dynamo_db_ops = UserDynamoDBOperations()
        user_dynamo_db_ops.create_table()
        insert_sample_users(user_dynamo_db_ops)
    except Exception as e:
        print(f"ERROR: Failed in main execution: {str(e)}")
