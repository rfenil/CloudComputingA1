import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
import logging
from typing import Optional, Dict, Any
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
music_table = dynamodb.Table('music')
users_table = dynamodb.Table('users')

def decimal_converter(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError

class MusicService:

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
            }, default=decimal_converter)
        }

    def _filter_search(
            self,
            table,
            title: Optional[str] = None,
            artist: Optional[str] = None,
            year: Optional[str] = None,
            album: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        response = None

        try:
            key_condition_expression = None
            filter_expression = None
            index_name = None
            query_kwargs: Dict[str, Any] = {}

            if artist and year:
                logger.info(f"ArtistYear Index selected.")
                index_name = 'ArtistYearIndex'
                key_condition_expression = Key('artist').eq(
                    artist) & Key('year').eq(int(year))
            elif title and album:
                logger.info(f"TitleAlbum Index selected.")
                index_name = 'TitleAlbumIndex'
                key_condition_expression = Key('title').eq(
                    title) & Key('album').eq(album)
            elif artist and album:
                logger.info(f"Base table PK and SK used.")
                key_condition_expression = Key('artist').eq(
                    artist) & Key('album#title').begins_with(album)

            if title and not (title and album):
                logger.info(f"Title based filter expression")
                filter_expression = Attr('title').eq(title)
            if album and not (title and album) and not (artist and album):
                logger.info(f"Album based filter expression")
                filter_expression = Attr('album#title').begins_with(album)
            if year and not (artist and year):
                logger.info(f"Year based filter expression")
                filter_expression = Attr('year').eq(int(year))
            if artist and not (artist and year) and not (artist and album):
                logger.info(f"Artist based filter expression")
                key_condition_expression = Key('artist').eq(artist)

            combined_filter_expression = None
            if filter_expression:
                combined_filter_expression = filter_expression

            if key_condition_expression:
                logger.info(f"Key condition expression filtering")
                query_kwargs = {
                    'KeyConditionExpression': key_condition_expression,
                }
                if index_name:
                    query_kwargs['IndexName'] = index_name
                if combined_filter_expression:
                    query_kwargs['FilterExpression'] = combined_filter_expression
                response = table.query(**query_kwargs)
            elif combined_filter_expression:
                logger.info(f"Combined expression filtering")
                scan_kwargs = {
                    'FilterExpression': combined_filter_expression
                }
                response = table.scan(**scan_kwargs)

            return {
                'Items': response.get('Items', []),
            } if response else {'Items': []}

        except Exception as e:
            logger.error(f"Error during DynamoDB operation: {e}")
            return None

    def get_songs(self):
        try:
            logger.info("Getting songs")
            query_params = self.event.get('queryStringParameters')
            title = query_params.get('title', None)
            album = query_params.get('album', None)
            artist = query_params.get('artist', None)
            year = query_params.get('year', None)
            logger.info(f"Query based on title={title} album={album} artist={artist} year={year}")
            search_response = self._filter_search(music_table, title, artist, year, album)
            logger.info(f"Song fetched after filtering {len(search_response['Items'])}")
            return self._generate_response(200, "Search results", search_response)

        except Exception as error:
            logger.error(f"Error while filtering the music {str(error)}")
            return self._generate_response(500, "Error while filtering the music")

    def get_subscribed_songs(self):
        try:
            query_params = self.event.get('queryStringParameters')
            user_id = query_params.get('user_id') if query_params else None

            if not user_id:
                logger.warning("user_id is missing")
                return self._generate_response(400, 'user_id is required')

            logger.info("Request body validation done")

            user_response = users_table.get_item(Key={'email': user_id})
            if 'Item' not in user_response:
                logger.warning(f"User with id {user_id} not found")
                return self._generate_response(400, 'User not found')

            logger.info(f"User with id {user_id} found")

            user = user_response['Item']
            subscriptions = user.get('subscription', set())

            if not subscriptions:
                logger.info("No subscribed songs found")
                return self._generate_response(200, 'No subscribed songs found', data=[])

            return self._generate_response(
                200,
                f"Successfully retrieved {len(subscriptions)} subscribed songs",
                data=subscriptions
            )

        except Exception as error:
            logger.error(f"Error in get_subscribed_songs: {error}")
            return self._generate_response(500, 'Internal server error')

    def subscribe(self):
        try:
            user_id: str = self.body['user_id']
            artist: str = self.body['artist']
            album: str = self.body['album']
            title: str = self.body['title']
            year: int = int(self.body.get('year'))
            img_url: str = self.body['img_url']

            if not user_id or not artist or not album or not title:
                logger.warning("user_id, artist, album, and title are required")
                return self._generate_response(400, 'user_id, artist, album, and title are required')

            logger.info("Request body validation")

            user_response = users_table.get_item(Key={'email': user_id})
            if 'Item' not in user_response:
                logger.warning(f"User with id {user_id} not found")
                return self._generate_response(400, 'User not found')

            logger.info(f"User with id {user_id} found")

            song_response = music_table.get_item(Key={'artist': artist, 'album#title': f"{album}#{title}"})
            if 'Item' not in song_response:
                logger.warning(f"Song with artist {artist}, album {album}, and title {title} not found")
                return self._generate_response(404, 'Song not found')

            logger.info(f"Song with artist {artist}, album {album}, and title {title} found")

            user = user_response['Item']
            subscriptions = user.get('subscription', [])

            song_identifier = {'artist': artist, 'album': album, 'title': title, 'year': year, 'img_url': img_url}

            if any(sub['artist'] == artist and sub['album'] == album and sub['title'] == title for sub in subscriptions):
                logger.warning("User is already subscribed to the music.")
                return self._generate_response(400, 'User is already subscribed to the music.')

            logger.info("Song not subscribed.")

            users_table.update_item(
                Key={'email': user_id},
                UpdateExpression='SET subscription = list_append(if_not_exists(subscription, :empty_list), :song_data)',
                ExpressionAttributeValues={
                    ':song_data': [song_identifier],
                    ':empty_list': []
                },
                ReturnValues='UPDATED_NEW'
            )

            logger.info(f"User {user_id} subscribed to song {artist} - {album} - {title}")

            return self._generate_response(200, 'Successfully subscribed user to the song')

        except Exception as error:
            logger.error(f"Error in subscribe: {error}")
            return self._generate_response(500, 'Internal server error')

    def unsubscribe(self):
        try:
            user_id: str = self.body['user_id']
            artist: str = self.body['artist']
            album: str = self.body['album']
            title: str = self.body['title']
            year: int = int(self.body['year'])

            if not user_id or not artist or not album or not title:
                logger.warning("user_id, artist, album, and title are required")
                return self._generate_response(400, 'user_id, artist, album, and title are required')

            logger.info("Request body validation done")

            user_response = users_table.get_item(Key={'email': user_id})
            if 'Item' not in user_response:
                logger.warning(f"User with id {user_id} not found")
                return self._generate_response(400, 'User not found')

            logger.info(f"User with id {user_id} found")

            song_response = music_table.get_item(Key={'artist': artist, 'album#title': f"{album}#{title}"})
            if 'Item' not in song_response:
                logger.warning(f"Song with artist {artist}, album {album}, and title {title} not found")
                return self._generate_response(404, 'Song not found')

            logger.info(f"Song with artist {artist}, album {album}, and title {title} found")

            user = user_response['Item']
            subscriptions = user.get('subscription', [])

            def matches(sub):
                return sub['artist'] == artist and sub['album'] == album and sub['title'] == title and sub['year'] == year

            try:
                matching_sub = next(sub for sub in subscriptions if matches(sub))
                subscriptions.remove(matching_sub)

                users_table.update_item(
                    Key={'email': user_id},
                    UpdateExpression='SET subscription = :subscriptions',
                    ExpressionAttributeValues={':subscriptions': subscriptions},
                    ReturnValues='UPDATED_NEW'
                )
                logger.info(f"User {user_id} unsubscribed from song {artist} - {album} - {title}")
                return self._generate_response(200, 'Successfully unsubscribed user from the song')

            except StopIteration:
                logger.info("User is not subscribed to the song")
                return self._generate_response(400, 'User is not subscribed to the song')

        except Exception as error:
            logger.error(f"Error in unsubscribe: {error}")
            return self._generate_response(500, 'Internal server error')

def lambda_handler(event, context):
    try:
        httpMethod = event.get('httpMethod', '')
        path = event.get('path')
        logger.info(f"PATH = {path}, HTTP_METHOD = {httpMethod}")
        raw_body = event.get('body')
        body = json.loads(raw_body) if isinstance(raw_body, str) else {}
        music = MusicService(event, context, body)

        if path == "/search" and httpMethod == 'GET':
            return music.get_songs()
        elif path == "/subscribe" and httpMethod == 'POST':
            return music.subscribe()
        elif path == "/unsubscribe" and httpMethod == 'POST':
            return music.unsubscribe()
        elif path == "/subscribed" and httpMethod == 'GET':
            return music.get_subscribed_songs()
        else:
            logger.warning("Invalid action type")
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