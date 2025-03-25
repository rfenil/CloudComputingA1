import boto3
from pydantic import BaseModel
from pydantic import BaseModel, Field

AWS_REGION = "us-east-1"
MUSIC_TABLE_NAME = "musics"

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

    def create_table(self):
        try:
            print("INFO: Creating DynamoDB table 'music'")
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
            print("SUCCESS: DynamoDB table created successfully")
            return self.table
        except Exception as e:
            print(f"ERROR: Failed to create DynamoDB table: {str(e)}")
            raise e
    
    def insert_music_data(self, music_item: MusicItem):
        try:
            print(f"INFO: Inserting music data for '{music_item.title}'")
            table = self.dynamodb.Table(self.table_name)
            table.put_item(Item={
                'id': music_item.id,
                'title': music_item.title,
                'artist': music_item.artist,
                'year': music_item.year,
                'album': music_item.album,
                's3_url': music_item.s3_url
            })
            print(f"SUCCESS: Inserted music data for '{music_item.title}'")
        except Exception as e:
            print(f"ERROR: Failed to insert music data: {str(e)}")
            raise e

if __name__ == "__main__":
    music_dynamo_db_ops = MusicDynamoDBOperations()
    music_dynamo_db_ops.create_table()