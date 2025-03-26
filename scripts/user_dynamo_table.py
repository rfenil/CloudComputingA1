import boto3
from pydantic import BaseModel, Field
from botocore.exceptions import ClientError
from uuid import uuid4

AWS_REGION = "us-east-1"
USER_TABLE_NAME = "users"

class UserItem(BaseModel):
    id: str | None = Field(None, description="UUID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email")
    password: str = Field(..., description="Password")

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
                    {'AttributeName': 'id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                    {'AttributeName': 'email', 'AttributeType': 'S'},  # For GSI
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'EmailIndex',
                        'KeySchema': [{'AttributeName': 'email', 'KeyType': 'HASH'}],
                        'Projection': {'ProjectionType': 'ALL'},
                        'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                    }
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
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'password': user.password
            }
            self.table.put_item(Item=item)
            print(f"SUCCESS: Inserted User data for '{user.username}'")
        except Exception as e:
            print(f"ERROR: Failed to insert User data: {str(e)}")
            raise e

def insert_sample_users(user_ops: UserDynamoDBOperations):
    sample_users = [
        UserItem(id=str(uuid4()), username="john_doe", email="john.doe@example.com", password="pass123"),
        UserItem(id=str(uuid4()), username="jane_smith", email="jane.smith@example.com", password="secure456"),
        UserItem(id=str(uuid4()), username="alice_w", email="alice.w@example.com", password="alice789"),
        UserItem(id=str(uuid4()), username="bob_jones", email="bob.jones@example.com", password="bob101"),
        UserItem(id=str(uuid4()), username="emma_k", email="emma.k@example.com", password="emma202"),
        UserItem(id=str(uuid4()), username="mike_brown", email="mike.brown@example.com", password="mike303"),
        UserItem(id=str(uuid4()), username="sarah_p", email="sarah.p@example.com", password="sarah404"),
        UserItem(id=str(uuid4()), username="david_lee", email="david.lee@example.com", password="david505"),
        UserItem(id=str(uuid4()), username="lisa_m", email="lisa.m@example.com", password="lisa606"),
        UserItem(id=str(uuid4()), username="tom_h", email="tom.h@example.com", password="tom707")
    ]
    
    for user in sample_users:
        user_ops.insert_user_data(user)

if __name__ == "__main__":
    try:
        user_dynamo_db_ops = UserDynamoDBOperations()
        user_dynamo_db_ops.create_table()
        insert_sample_users(user_dynamo_db_ops)
    except Exception as e:
        print(f"ERROR: Failed in main execution: {str(e)}")