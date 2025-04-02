import json
import hashlib
import boto3
from uuid import uuid4
from boto3.dynamodb.conditions import Key, Attr
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
music_table = dynamodb.Table('music')
users_table = dynamodb.Table('users')


class MusicSearvice:

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

    def _filter_search(
            self,
            table,
            title: Optional[str] = None,
            artist: Optional[str] = None,
            year: Optional[int] = None,
            album: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        response = None

        try:
            key_condition_expression = None
            filter_expression = None
            index_name = None  
            query_kwargs: Dict[str, Any] = {}  

            if artist and year:
                index_name = 'ArtistYearIndex'  # Use LSI
                key_condition_expression = Key('artist').eq(
                    artist) & Key('year').eq(year)
            elif title and album:
                index_name = 'TitleAlbumIndex'  # Use GSI
                key_condition_expression = Key('title').eq(
                    title) & Key('album').eq(album)
            elif artist and album:
                key_condition_expression = Key('artist').eq(
                    artist) & Key('album#title').begins_with(album)

            if title and not (title and album):  # avoid duplicate filter
                filter_expression = Attr('title').eq(title)
            if album and not (title and album) and not (artist and album):
                filter_expression = Attr('album#title').begins_with(album)
            if year and not (artist and year):  # avoid duplicate filter
                filter_expression = Attr('year').eq(year)
            if artist and not (artist and year) and not (artist and album):
                key_condition_expression = Key('artist').eq(artist)

            combined_filter_expression = None
            if filter_expression:
                combined_filter_expression = filter_expression

            if key_condition_expression:  
                query_kwargs = {
                    'KeyConditionExpression': key_condition_expression,
                }
                if index_name:
                    query_kwargs['IndexName'] = index_name
                if combined_filter_expression:
                    query_kwargs['FilterExpression'] = combined_filter_expression
                response = table.query(**query_kwargs)
            elif combined_filter_expression:  
                scan_kwargs = {
                    'FilterExpression': combined_filter_expression
                }
                response = table.scan(**scan_kwargs)
            else:
                print(
                    "No specific criteria provided.  Performing a full table scan.  This is inefficient for large tables.")
                scan_kwargs = {}
                response = table.scan(**scan_kwargs)

            return {
                'Items': response.get('Items', []),
            } if response else {'Items': []}
        except Exception as e:
            print(f"Error during DynamoDB operation: {e}")
            return None

    def get_songs(self):
        try:
            query_params = self.event.get('queryStringParameters')
            title = query_params.get('title', None)
            album = query_params.get('album', None)
            artist = query_params.get('artist', None)
            year = query_params.get('year', None)

            search_response = self._filter_search(music_table, title, artist, year, album)
            self._generate_response(200, "Got it", search_response)

        except Exception as error:
            print(error)
    def get_subscribed_songs(self):
        try:
            query_params = self.event.get('queryStringParameters')
            user_id = query_params.get('user_id') if query_params else None

            if not user_id:
                return self._generate_response(400, 'user_id is required')

            logger.info("Request body validation done")

            user_response = users_table.get_item(Key={'id': user_id})
            if 'Item' not in user_response:
                return self._generate_response(400, 'User not found')

            logger.info(f"User with id {user_id} found")

            user = user_response['Item']
            subscriptions = user.get('subscription', set())

            if not subscriptions:
                return self._generate_response(200, 'No subscribed songs found', data=[])

            subscribed_songs = []
            for song_id in subscriptions:
                song_response = music_table.get_item(Key={'id': song_id})
                if 'Item' in song_response:
                    song = song_response['Item']
                    subscribed_songs.append({
                        'id': song.get('id'),
                        'title': song.get('title'),
                        'artist': song.get('artist'),
                        'album': song.get('album'),
                        'img_url': song.get('img_url'),
                        'year': song.get('year')
                    })
                else:
                    logger.warning(
                        f"Song {song_id} in subscriptions not found in songs table")

            logger.info(
                f"Retrieved {len(subscribed_songs)} subscribed songs for user {user_id}")

            return self._generate_response(
                200,
                f"Successfully retrieved {len(subscribed_songs)} subscribed songs",
                data=subscribed_songs
            )

        except Exception as error:
            logging.error(f"Error in get_subscribed_songs: {error}")
            return self._generate_response(500, 'Internal server error')

    def subscribe(self):
        try:
            user_id: str = self.body['user_id']
            song_id: str = self.body['song_id']

            # Validate input
            if not user_id or not song_id:
                return self._generate_response(400, 'user_id and song_id are required')

            logger.info("Request body validation")

            user_response = users_table.get_item(Key={'id': user_id})
            if 'Item' not in user_response:
                return self._generate_response(400, 'User not found')

            logger.info(f"User with id {user_id} found")

            song_response = music_table.get_item(Key={'id': song_id})
            if 'Item' not in song_response:
                return self._generate_response(404, 'Song not found')

            logger.info("Song with id {song_id} found")

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

            song_response = music_table.get_item(Key={'id': song_id})
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
        httpMethod = event.get('httpMethod', '')
        path = event.get('path')
        logger.info(f"PATH = {path}, HTTP_METHOD = {httpMethod}")
        raw_body = event.get('body')
        body = json.loads(raw_body) if isinstance(raw_body, str) else {}
        music = MusicSearvice(event, context, body)

        if path == "/" and httpMethod == 'GET':
            return music.get_songs()
        elif path == "/subscribe" and httpMethod == 'POST':
            return music.subscribe()
        elif path == "/unsubscribe" and httpMethod == 'POST':
            return music.unsubscribe()
        elif path == "/subscribed" and httpMethod == 'GET':
            return music.get_subscribed_songs()
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
