import boto3
import requests
import json
from uuid import uuid4
from typing import Dict
from music_dynamo_table import MusicDynamoDBOperations, MusicItem

# AWS S3 Bucket Configuration
S3_BUCKET_NAME = "a1-projectgroup-31-group"
AWS_REGION = "us-east-1"

# JSON FILE
SONG_JSON_FILE_NAME = "./2025a1.json"

def create_private_s3_bucket(bucket_name: str, region_name: str):
    try:
        s3 = boto3.client("s3", region_name=region_name)

        # Check if the bucket already exists
        response = s3.list_buckets()
        bucket_exists = any(
            bucket['Name'] == bucket_name for bucket in response['Buckets']
        )

        if bucket_exists:
            print(f"INFO: S3 bucket '{bucket_name}' already exists")
        else:
            if region_name == "us-east-1":
                s3.create_bucket(
                    Bucket=bucket_name,
                    ACL='private',
                )
            else:
                location = {'LocationConstraint': region_name}
                s3.create_bucket(
                    Bucket=bucket_name,
                    ACL='private',
                    CreateBucketConfiguration=location
                )

            print(f"SUCCESS: Created private S3 bucket '{bucket_name}'")

        # Ensure public access block allows public reads
        s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,  # Allow public read access via policy
                'RestrictPublicBuckets': False, 
            },
        )

        # Apply a bucket policy to allow public reads on objects
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }

        s3.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )

        print(f"SUCCESS: Public read access enabled for objects in '{bucket_name}'")

    except Exception as e:
        print(f"ERROR: Failed to create S3 bucket '{bucket_name}': {str(e)}")
        raise e



def upload_image_to_s3_bucket(
        bucket_name: str, 
        region_name: str,
        image_content: bytes, 
        image_name: str, 
        song: MusicItem
) -> str:
    try:
        s3 = boto3.client("s3", region_name=region_name)
        key = f"artist_images/{image_name}"
        s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=image_content,
            ContentType="image/jpeg",
            Metadata={
                'title': song.title,
                'year': song.year,
                'artist': song.artist
            },
        )

        s3_url = f"https://{bucket_name}.s3.{region_name}.amazonaws.com/{key}"
        print(f"SUCCESS: Uploaded '{image_name}' to S3")
        return s3_url
    except Exception as e:
        print(f"ERROR: Failed to upload '{image_name}': {str(e)}")
        raise e


def process_songs_json():
    try:
        songs_data = {}
        music_dynamo_db_ops = MusicDynamoDBOperations()
        raw_s3_url_lookup: Dict[str, str] = {}

        print("INFO: Reading music JSON file from {}".format(SONG_JSON_FILE_NAME))
        with open(SONG_JSON_FILE_NAME, "r", encoding="utf-8") as file:
            songs_data = json.load(file)

        print("SUCCESS: Music file parsed successfully. Found {} songs.".format(len(songs_data.get('songs', []))))
        processed_url = set()

        for song_index, song_data in enumerate(songs_data.get('songs', []), start=1):
            print(f"INFO: Processing song {song_index}/{len(songs_data.get('songs', []))}: {song_data.get('title', 'Unknown Title')}")

            song = MusicItem(
                id=str(uuid4()),
                title=song_data.get('title', ''),
                artist=song_data.get('artist', ''),
                year=song_data.get('year', ''),
                album=song_data.get('album', ''),
                img_url=song_data.get('img_url', '')
            )

            primary_key = f"{song.artist}#{song.album}#{song.title}"
            if primary_key not in processed_url:
                print(f"INFO: Processing unique song: {song.title} by {song.artist}, album: {song.album}")

                if song.img_url in raw_s3_url_lookup.keys():
                    print("INFO: Image URL found in lookup, using cached S3 URL.")
                    song.s3_url = raw_s3_url_lookup[song.img_url]  
                else:
                    try:
                        print(f"INFO: Downloading image from {song.img_url}")
                        response = requests.get(song.img_url, timeout=10) 
                        response.raise_for_status() 

                        image_name = f"{song.artist}_{song.album}_{song.title}.jpg".replace(" ", "_")
                        print(f"INFO: Uploading image for '{song.title}' as '{image_name}' to S3 bucket '{S3_BUCKET_NAME}'")
                        s3_url = upload_image_to_s3_bucket(
                            S3_BUCKET_NAME,
                            AWS_REGION,
                            response.content,
                            image_name,
                            song
                        )
                        song.s3_url = s3_url
                        raw_s3_url_lookup[song.img_url] = s3_url 
                        print(f"SUCCESS: Image uploaded to S3: {s3_url}")

                    except requests.exceptions.RequestException as e:
                        print(f"ERROR: Failed to download image from {song.img_url}: {str(e)}")
                        song.s3_url = None
                    except Exception as e:
                        print(f"ERROR: Failed to upload image to S3: {str(e)}")
                        song.s3_url = None 

                try:
                    music_dynamo_db_ops.insert_music_data(song)
                    print(f"SUCCESS: Song data inserted into DynamoDB for: {song.title}")
                except Exception as e:
                    print(f"ERROR: Failed to insert song data into DynamoDB: {str(e)}")

                processed_url.add(primary_key)
            else:
                print(f"INFO: Skipping duplicate song: {song.title} by {song.artist}, album: {song.album}")


    except FileNotFoundError:
        print(f"ERROR: Music JSON file not found at {SONG_JSON_FILE_NAME}")
        raise
    except json.JSONDecodeError:
        print(f"ERROR: Failed to decode JSON from {SONG_JSON_FILE_NAME}. Invalid JSON format.")
        raise
    except Exception as e:
        print(f"ERROR: Failed to process songs file: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        print("INFO: Starting song processing application")
        print(f"INFO: Creating/verifying S3 bucket '{S3_BUCKET_NAME}' in {AWS_REGION}")
        create_private_s3_bucket(S3_BUCKET_NAME, AWS_REGION)
        
        print("INFO: Starting song JSON processing")
        process_songs_json()
        print("SUCCESS: Application completed successfully")
        
    except Exception as e:
        print(f"ERROR: Application failed with error: {str(e)}")
        raise e
