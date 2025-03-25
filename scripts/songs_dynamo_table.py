import boto3
from pydantic import BaseModel, Field
from botocore.exceptions import ClientError

AWS_REGION = "us-east-1"
SONG_TABLE_NAME = "songs"

class SongItem(BaseModel):
    id: str | None = Field(None, description="UUID")
    title: str = Field(..., description="Title")
    artist: str = Field(..., description="Artist")
    year: str = Field(..., description="Year")
    album: str = Field(..., description="Album")
    img_url: str = Field(..., description="Image URL")
    s3_url: str | None = Field(None, description="S3 URL")

class SongDynamoDBOperations:

    def __init__(self, region_name: str = AWS_REGION):
        self.dynamodb = boto3.resource('dynamodb', region_name=region_name)
        self.table_name = SONG_TABLE_NAME
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

            print(f"INFO: Creating DynamoDB table '{SONG_TABLE_NAME}'")
            self.table = self.dynamodb.create_table(
                TableName=self.table_name,
                KeySchema=[
                    {'AttributeName': 'id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                    {'AttributeName': 'title', 'AttributeType': 'S'},
                    {'AttributeName': 'artist', 'AttributeType': 'S'},
                    {'AttributeName': 'year', 'AttributeType': 'S'},
                    {'AttributeName': 'album', 'AttributeType': 'S'},
                ],
                GlobalSecondaryIndexes=[
                    {
                        'IndexName': 'TitleIndex',
                        'KeySchema': [{'AttributeName': 'title', 'KeyType': 'HASH'}],
                        'Projection': {'ProjectionType': 'ALL'},
                        'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                    },
                    {
                        'IndexName': 'ArtistIndex',
                        'KeySchema': [{'AttributeName': 'artist', 'KeyType': 'HASH'}],
                        'Projection': {'ProjectionType': 'ALL'},
                        'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                    },
                    {
                        'IndexName': 'YearIndex',
                        'KeySchema': [{'AttributeName': 'year', 'KeyType': 'HASH'}],
                        'Projection': {'ProjectionType': 'ALL'},
                        'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
                    },
                    {
                        'IndexName': 'AlbumIndex',
                        'KeySchema': [{'AttributeName': 'album', 'KeyType': 'HASH'}],
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
    
    def insert_song_data(self, song: SongItem):
        try:
            print(f"INFO: Inserting Song data for '{song.title}'")
            self.table = self.dynamodb.Table(self.table_name)
            item = {
                'id': song.id,
                'title': song.title,
                'artist': song.artist,
                'year': song.year,
                'album': song.album,
                'img_url': song.img_url
            }
            if song.s3_url:     
                item['s3_url'] = song.s3_url
            
            self.table.put_item(Item=item)
            print(f"SUCCESS: Inserted Song data for '{song.title}'")
        except Exception as e:
            print(f"ERROR: Failed to insert Song data: {str(e)}")
            raise e

if __name__ == "__main__":
    try:
        song_dynamo_db_ops = SongDynamoDBOperations()
        song_dynamo_db_ops.create_table()
    except Exception as e:
        print(f"ERROR: Failed in main execution: {str(e)}")