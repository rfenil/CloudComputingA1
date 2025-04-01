import json
import hashlib
import boto3
from uuid import uuid4
from boto3.dynamodb.conditions import Key, Attr
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
songs_table = dynamodb.Table('songs')
users_table = dynamodb.Table('users')

class SongService:

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

    def get_songs(self):
        try:
            params = self.event.get('queryStringParameters') or {}
            artist = params.get('artist')
            title = params.get('title')
            year = params.get('year')
            album = params.get('album')
            limit = int(params.get('limit', 10))
            last_evaluated_key = params.get('last_evaluated_key')

            logger.info(f"Filter params: artist={artist}, title={title}, year={year}, album={album}")

            exclusive_start_key = json.loads(last_evaluated_key) if last_evaluated_key else None

            if artist and year:
                response = songs_table.query(
                    IndexName='ArtistYearIndex',
                    KeyConditionExpression=Key('artist').eq(artist) & Key('year').eq(year),
                    Limit=limit,
                    ExclusiveStartKey=exclusive_start_key
                )

            elif artist and album:
                response = songs_table.query(
                    IndexName='ArtistAlbumIndex',
                    KeyConditionExpression=Key('artist').eq(artist) & Key('album').eq(album),
                    Limit=limit,
                    ExclusiveStartKey=exclusive_start_key
                )

            elif title:
                response = songs_table.query(
                    IndexName='TitleIndex',
                    KeyConditionExpression=Key('title').eq(title),
                    Limit=limit,
                    ExclusiveStartKey=exclusive_start_key
                )

            elif album:
                response = songs_table.query(
                    IndexName='AlbumIndex',
                    KeyConditionExpression=Key('album').eq(album),
                    Limit=limit,
                    ExclusiveStartKey=exclusive_start_key
                )
            
            else:
                scan_kwargs = {'Limit': limit}
                if exclusive_start_key:
                    scan_kwargs['ExclusiveStartKey'] = exclusive_start_key
                response = songs_table.scan(**scan_kwargs)

            response_data = {
                'songs': response.get('Items', [])
            }
            if 'LastEvaluatedKey' in response:
                response_data['last_evaluated_key'] = response['LastEvaluatedKey']

            return self._generate_response(200, 'Songs fetched successfully', response_data)

        except Exception as e:
            logger.error(f"Error in get_songs: {e}")
            return self._generate_response(500, 'Internal Server Error')

            
            


    def get_subscribed_songs():
        pass

    def subscribe(self):
        try:
            user_id: str = self.body['user_id']
            song_id: str = self.body['song_id'] 

            # Validate input
            if not user_id or not song_id:
                return  self._generate_response(400, 'user_id and song_id are required')
            
            logger.info("Request body validation done")

            user_response = users_table.get_item(Key={'id': user_id})
            if 'Item' not in user_response:
                return  self._generate_response(400, 'User not found')
            
            logger.info(f"User with id {user_id} found")

            song_response = songs_table.get_item(Key={'id': song_id})
            if 'Item' not in song_response:
                return self._generate_response(404, 'Song not found')
            
            logger.info(f"Song with id {song_id} found")

            user = user_response['Item']
            subscriptions = user.get('subscription', set())
            if song_id in subscriptions:
                return self._generate_response(400, 'User is already subscribed to the music.')
            
            logger.info("Song not subscribed.")

            users_table.update_item(
                Key={'id': user_id},
                UpdateExpression='SET subscription = list_append(if_not_exists(subscription, :empty_list), :song_id)',
                ExpressionAttributeValues={
                    ':song_id': [song_id],
                    ':empty_list': []
                },
                ReturnValues='UPDATED_NEW'
            )

            logger.info(f"User {user_id} subscribed to song {song_id}")

            return self._generate_response(200, 'Successfully subscribed user to the song')

        except Exception as error:
            logging.error(f"Error in subscribe: {error}")
            return self._generate_response(500, 'Internal server error')

    def unsubscribe(self):
        try:
            user_id: str = self.body['user_id']
            song_id: str = self.body['song_id']

            if not user_id or not song_id:
                return self._generate_response(400, 'user_id and song_id are required')
            
            logger.info("Request body validation done")

            user_response = users_table.get_item(Key={'id': user_id})
            if 'Item' not in user_response:
                return self._generate_response(400, 'User not found')

            logger.info(f"User with id {user_id} found")

            song_response = songs_table.get_item(Key={'id': song_id})
            if 'Item' not in song_response:
                return self._generate_response(404, 'Song not found')

            logger.info(f"Song with id {user_id} found")

            user = user_response['Item']
            subscriptions = user.get('subscription', set())
            if song_id not in subscriptions:
                return self._generate_response(400, 'User is not subscribed to the song')

            logger.info("Song already subscribed")

            subscriptions.remove(song_id)
        
            users_table.update_item(
                Key={'id': user_id},
                UpdateExpression='SET subscription = :subscriptions',
                ExpressionAttributeValues={':subscriptions': subscriptions},
                ReturnValues='UPDATED_NEW'
            )

            logger.info(f"User {user_id} unsubscribed from song {song_id}")
            return self._generate_response(200, 'Successfully unsubscribed user from the song') 

        except Exception as error:
            logging.error(f"Error in unsubscribe: {error}")
            return self._generate_response(500, 'Internal server error')


def lambda_handler(event, context):
    try:
        httpMethod = event['httpMethod']
        path = event['path']
        body = json.loads(event['body'])
        song = SongService(event, context, body)

        if path == "/" and httpMethod == 'GET':
            return song.get_songs()
        elif path == "/subscribe" and httpMethod == 'POST':
            return song.subscribe()
        elif path == "/unsubscribe" and httpMethod == 'POST':
            return song.unsubscribe()
        else:
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

"""
{
    "user_id": "e3f4fa5d-6ffa-4496-8bc3-ee28dbc3f46b",
    "song_id": "68d6059b-74f6-41ea-b3af-fa11fa9a813e"
}
"""

