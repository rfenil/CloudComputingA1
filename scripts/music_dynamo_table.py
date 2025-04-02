import boto3
from pydantic import BaseModel, Field
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from typing import Optional, Tuple, List

AWS_REGION = "us-east-1"
MUSIC_TABLE_NAME = "music"

class MusicItem(BaseModel):
    id: str | None = Field(None, description="UUID")
    title: str = Field(..., description="Title")
    artist: str = Field(..., description="Artist")
    year: str = Field(..., description="Year")
    album: str = Field(..., description="Album")
    img_url: str = Field(..., description="Image URL")
    s3_url: str | None = Field(None, description="S3 URL")

class MusicDynamoDBOperations:

    def __init__(self, region_name: str = AWS_REGION):
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table_name = MUSIC_TABLE_NAME
        self.table = None

    def table_exists(self):
        """Check if the table already exists."""
        try:
            table = self.dynamodb.Table(self.table_name)
            table.load()  # Raises an exception if the table doesn't exist
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return False
            raise

    def create_table(self):
        try:
            if self.table_exists():
                print(f"INFO: Table '{self.table_name}' already exists, using existing table")
                self.table = self.dynamodb.Table(self.table_name)
                return self.table

            print(f"INFO: Creating DynamoDB table '{MUSIC_TABLE_NAME}'")
            self.table = self.dynamodb.create_table(
                TableName=self.table_name,
                AttributeDefinitions=[
                    {"AttributeName": "artist", "AttributeType": "S"},
                    {"AttributeName": "album#title", "AttributeType": "S"},
                    {"AttributeName": "year", "AttributeType": "N"},
                    {"AttributeName": "title", "AttributeType": "S"},
                    {"AttributeName": "album", "AttributeType": "S"}
                ],
                KeySchema=[
                    {"AttributeName": "artist", "KeyType": "HASH"},  # Partition Key
                    {"AttributeName": "album#title",
                        "KeyType": "RANGE"}  # Sort Key
                ],
                LocalSecondaryIndexes=[
                    {
                        "IndexName": "ArtistYearIndex",
                        "KeySchema": [
                            # Same Partition Key
                            {"AttributeName": "artist", "KeyType": "HASH"},
                            # Sort Key for LSI
                            {"AttributeName": "year", "KeyType": "RANGE"}
                        ],
                        "Projection": {"ProjectionType": "ALL"}
                    }
                ],
                GlobalSecondaryIndexes=[
                    {
                        "IndexName": "TitleAlbumIndex",
                        "KeySchema": [
                            # Partition Key for GSI
                            {"AttributeName": "title", "KeyType": "HASH"},
                            # Sort Key for GSI
                            {"AttributeName": "album", "KeyType": "RANGE"}
                        ],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
                    }
                ],
                ProvisionedThroughput={
                    "ReadCapacityUnits": 5,
                    "WriteCapacityUnits": 5
                }
            )
            self.table.wait_until_exists()
            print(f"SUCCESS: DynamoDB table created successfully: {self.table.item_count}")
            return self.table
        except Exception as e:
            print(f"ERROR: Failed to create DynamoDB table: {str(e)}")
            raise e
    
    def insert_music_data(self, music: MusicItem):
        try:
            print(f"INFO: Inserting music data for '{music.title}'")
            self.table = self.dynamodb.Table(self.table_name)
            
            item = {
                "artist": music.artist,
                "album#title": f"{music.album}#{music.title}",
                "year": int(music.year),
                "album": music.album,
                "title": music.title,
                "img_url": music.s3_url
            }
            
            
            self.table.put_item(Item=item)
            print(f"SUCCESS: Inserted music data for '{music.title}'")
        except Exception as e:
            print(f"ERROR: Failed to insert music data: {str(e)}")
            raise e

if __name__ == "__main__":
    try:
        music_dynamo_db_ops = MusicDynamoDBOperations()
        music_dynamo_db_ops.create_table()
    except Exception as e:
        print(f"ERROR: Failed in main execution: {str(e)}")