import boto3
from pydantic import BaseModel, Field
from botocore.exceptions import ClientError
from uuid import uuid4

AWS_REGION = "us-east-1"
SUBSCRIPTION_TABLE_NAME = "subscriptions"

class SubscriptionItem(BaseModel):
    subscription_id: str | None = Field(None, description="UUID for subscription")
    user_id: str = Field(..., description="User ID")
    music_id: str = Field(..., description="Music ID")

class SubscriptionDynamoDBOperations:

    def __init__(self, region_name: str = AWS_REGION):
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table_name = SUBSCRIPTION_TABLE_NAME
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

            print(f"INFO: Creating DynamoDB table '{SUBSCRIPTION_TABLE_NAME}'")
            self.table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {'AttributeName': 'subscription_id', 'KeyType': 'HASH'}  # Primary Key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'subscription_id', 'AttributeType': 'S'},
                    {'AttributeName': 'user_id', 'AttributeType': 'S'},     # For GSI
                    {'AttributeName': 'music_id', 'AttributeType': 'S'},    # For GSI
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'UserIdIndex',
                        'KeySchema': [{'AttributeName': 'user_id', 'KeyType': 'HASH'}],
                        'Projection': {'ProjectionType': 'ALL'},
                        'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                    },
                    {
                        'IndexName': 'MusicIdIndex',
                        'KeySchema': [{'AttributeName': 'music_id', 'KeyType': 'HASH'}],
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
    
    def insert_subscription_data(self, subscription: SubscriptionItem):
        """Insert a subscription item into the DynamoDB table."""
        try:
            print(f"INFO: Inserting Subscription data for subscription_id: '{subscription.subscription_id}'")
            self.table = self.dynamodb.Table(self.table_name)
            item = {
                'subscription_id': subscription.subscription_id,
                'user_id': subscription.user_id,
                'music_id': subscription.music_id
            }
            self.table.put_item(Item=item)
            print(f"SUCCESS: Inserted Subscription data for subscription_id: '{subscription.subscription_id}'")
        except Exception as e:
            print(f"ERROR: Failed to insert Subscription data: {str(e)}")
            raise e


if __name__ == "__main__":
    try:
        subscription_dynamo_db_ops = SubscriptionDynamoDBOperations()
        subscription_dynamo_db_ops.create_table()
    except Exception as e:
        print(f"ERROR: Failed in main execution: {str(e)}")