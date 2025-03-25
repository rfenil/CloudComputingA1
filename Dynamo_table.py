import boto3
import uuid
import json
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Logger function for tracking 
def log(message, level="INFO"):
    print(f"[{level}] {message}")

def table_exists(table_name):
    try:
        table = dynamodb.Table(table_name)
        table.load()
        return True
    except ClientError:
        return False

# Function to create DynamoDB tables 
def create_tables():
    try:
        if not table_exists('music'):
            log("Creating music table.")
            music_table = dynamodb.create_table(
                TableName='music',
                KeySchema=[
                    {'AttributeName': 'id', 'KeyType': 'HASH'},  
                ],
                AttributeDefinitions=[
                    # Defining attribute types for the table music
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                    {'AttributeName': 'artist', 'AttributeType': 'S'},
                    {'AttributeName': 'album', 'AttributeType': 'S'},
                    {'AttributeName': 'title', 'AttributeType': 'S'},
                    {'AttributeName': 'year', 'AttributeType': 'N'}
                ],
                GlobalSecondaryIndexes=[
                    # Global Secondary Index to query by artist
                    {
                        'IndexName': 'artist_index',
                        'KeySchema': [{'AttributeName': 'artist', 'KeyType': 'HASH'}],
                        'Projection': {'ProjectionType': 'ALL'},
                    },
                    # Global Secondary Index to query by album
                    {
                        'IndexName': 'album_index',
                        'KeySchema': [{'AttributeName': 'album', 'KeyType': 'HASH'}],
                        'Projection': {'ProjectionType': 'ALL'},
                    },
                    # Global Secondary Index to query by title
                    {
                        'IndexName': 'title_index',
                        'KeySchema': [{'AttributeName': 'title', 'KeyType': 'HASH'}],
                        'Projection': {'ProjectionType': 'ALL'},
                    },
                    # Global Secondary Index to query by year
                    {
                        'IndexName': 'year_index',
                        'KeySchema': [{'AttributeName': 'year', 'KeyType': 'HASH'}],
                        'Projection': {'ProjectionType': 'ALL'},
                    }
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            music_table.wait_until_exists()
            log("Music table created successfully!")
        else:
            log("Music Table exists")

        if not table_exists('user'):
            
            log("Creating user table.")
            # Creating user table
            user_table = dynamodb.create_table(
                TableName='user',
                KeySchema=[
                    {'AttributeName': 'user_id', 'KeyType': 'HASH'},  #PartitionKey
                    {'AttributeName': 'email', 'KeyType': 'RANGE'}    #SortKey
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'user_id', 'AttributeType': 'S'},
                    {'AttributeName': 'email', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            user_table.wait_until_exists()
            log("User table created successfully!")
        else:
            log("Table already Present")
        

        if not table_exists('subscription'):

            log("Creating subscription table.")
            # Creating Subscription Table
            subscription_table = dynamodb.create_table(
                TableName='subscription',
                KeySchema=[
                    {'AttributeName': 'sub_id', 'KeyType': 'HASH'},   #Primary Key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'sub_id', 'AttributeType': 'S'},
                    {'AttributeName': 'user_id', 'AttributeType': 'S'},
                    {'AttributeName': 'music_id', 'AttributeType': 'S'}
                ],
                GlobalSecondaryIndexes=[
                    {
                        #Global Secondary Index to efficiently query user-music combinations
                        'IndexName': 'user_music_index',
                        'KeySchema': [
                            {'AttributeName': 'user_id', 'KeyType': 'HASH'},  # Partition Key for user ID
                            {'AttributeName': 'music_id', 'KeyType': 'RANGE'}  # Sort Key for music ID
                        ],
                        #Include all attributes from the base table
                        'Projection': {'ProjectionType': 'ALL'},
                    }
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            subscription_table.wait_until_exists()
            log("Subscription table created successfully!")
        else:
            log("subscription table exists")

    except ClientError as e:
        log(f"Error creating tables: {e.response['Error']['Message']}", level="ERROR")

def is_duplicate_user(user_id, email):
    try:
        user_table = dynamodb.Table('user')
        response = user_table.get_item(
            Key={
                'user_id': user_id,
                'email': email
            }
        )
        return 'Item' in response
    except ClientError as e:
        log(f"Error checking for duplicate user: {e.response['Error']['Message']}", level="ERROR")
        return False


def populate_user_table():
    try:
        user_table = dynamodb.Table('user')
        users = [
            ("Prajwal", "Manjunath", "s40625070"),
            ("Krish", "Parekh", "s40432811"),
            ("Divyam", "Juneja", "s40178982"),
            ("John", "Williams", "s44165573"),
            ("Michael", "Williams", "s41396854"),
            ("Emma", "Miller", "s41334695"),
            ("Sophia", "Smith", "s44757456"),
            ("James", "Johnson", "s48970117"),
            ("Sophia", "Davis", "s47859568"),
            ("Emma", "Miller", "s41805389")
        ]

        for idx, (first_name, last_name, student_id) in enumerate(users):
            email = f"{student_id}{idx}@student.rmit.edu.au"
            user_name = f"{first_name} {last_name}{idx}"
            password = str(uuid.uuid4().int)[:6]
            user_id = str(uuid.uuid4())

            # Check for duplicate user
            if is_duplicate_user(user_id, email):
                log(f"Duplicate user found: {user_name} with email {email}. Skipping.", level="WARNING")
                continue
            
            user_table.put_item(
                Item={
                    'user_id': user_id,
                    'email': email,
                    'user_name': user_name,
                    'password': password
                }
            )
            log(f"Added user: {user_name} with email: {email}")

    except ClientError as e:
        log(f"Error populating user table: {e.response['Error']['Message']}", level="ERROR")

# Function to check for duplicate songs
def is_duplicate_song(title, artist, album, year):
    try:
        music_table = dynamodb.Table('music')
        response = music_table.query(
            IndexName='title_index',
            KeyConditionExpression=Key('title').eq(title)
        )
        for item in response.get('Items', []):
            if item.get('artist') == artist and item.get('album') == album and item.get('year') == year:
                return True
        return False
    except ClientError as e:
        log(f"Error checking for duplicate song: {e.response['Error']['Message']}", level="ERROR")
        return False

# Function to batch insert songs into the Music table with duplicate check
def populate_music_table():
    try:
        music_table = dynamodb.Table('music')
        with open('2025a1.json', 'r') as file:
            data = json.load(file)

        with music_table.batch_writer() as batch:
            for song in data['songs']:
                try:
                    title = song['title']
                    artist = song['artist']
                    album = song['album']
                    year = int(song['year'])

                    # Check for duplicates
                    if is_duplicate_song(title, artist, album, year):
                        log(f"Duplicate song found: {title} by {artist}. Skipping upload.", level="WARNING")
                        continue

                    music_id = str(uuid.uuid4())
                    batch.put_item(
                        Item={
                            'id': music_id,
                            'title': title,
                            'artist': artist,
                            'year': year,
                            'album': album,
                            'image_url': song['img_url']
                        }
                    )
                    log(f"Added song: {title} by {artist}")
                except ClientError as e:
                    log(f"Error adding song {title}: {e.response['Error']['Message']}", level="ERROR")
    except FileNotFoundError:
        log("Error: The file '2025a1.json' was not found. Please make sure it is in the same directory.", level="ERROR")
    except json.JSONDecodeError:
        log("Error: Failed to decode JSON from the file. Please check the file format.", level="ERROR")
    except Exception as e:
        log(f"Unexpected error: {str(e)}", level="ERROR")

# Main function to orchestrate table creation and data population
def main():
    try:
        create_tables()
        populate_music_table()
        populate_user_table()
    except Exception as e:
        log(f"Critical error: {str(e)}", level="ERROR")

if __name__ == "__main__":
    main()

#Resources refered: 
# Boto3 Documentation https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html
# For Global Secondary Indexes: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GSI.html
# Create Global Secondary Index (GSI) for DynamoDB using Boto3 in Python: https://stackoverflow.com/questions/72133092/create-global-secondary-index-gsi-for-dynamodb-using-boto3-in-python
# Handling JSON Error: https://stackoverflow.com/questions/8381193/handle-json-decode-error-when-nothing-returned
# Using batch_writer: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/table/batch_writer.html
