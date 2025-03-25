import boto3
import requests
import json
from uuid import UUID, uuid4
from music_dynamo_table import MusicItem, MusicDynamoDBOperations

# AWS S3 Bucket Configuration
S3_BUCKET_NAME = "a1-projectgroup-31"
AWS_REGION = "us-east-1"

# JSON FILE
MUSIC_JSON_FILE_NAME = "../2025a1.json"

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
            return

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

        s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True,
            },
        )

        print(f"SUCCESS: Created private S3 bucket '{bucket_name}'")

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
            })
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

        print("INFO: Reading music JSON file")
        with open(MUSIC_JSON_FILE_NAME, "r", encoding="utf-8") as file:
            songs_data = json.load(file)

        print("SUCCESS: Music file parsed successfully")
        processed_url = set()

        for song_data in songs_data.get('songs', []):
            song = MusicItem(
                id=str(uuid4()),
                title=song_data.get('title', ''),
                artist=song_data.get('artist', ''),
                year=song_data.get('year', ''),
                album=song_data.get('album', ''),
                img_url=song_data.get('img_url', '')
            )

            try:
                print(f"INFO: Processing song '{song.title}' by {song.artist}")
                
                if song.img_url in processed_url:
                    print(f"INFO: Skipping duplicate image URL for '{song.title}'")
                    continue

                print(f"INFO: Downloading image for '{song.title}'")
                response = requests.get(song.img_url)
                
                if response.status_code == 200:
                    image_name = f"{song.artist}_{song.title}.jpg".replace(" ", "_")
                    print(f"INFO: Uploading image for '{song.title}'")
                    
                    s3_url = upload_image_to_s3_bucket(
                        S3_BUCKET_NAME, 
                        AWS_REGION,
                        response.content, 
                        image_name,
                        song
                    )
                    song.s3_url = s3_url
                    music_dynamo_db_ops.insert_music_data(song)
                    processed_url.add(song.img_url)
                    print(f"SUCCESS: Processed '{song.title}' successfully")
                else:
                    print(f"ERROR: Failed to download image for '{song.title}'")
            except Exception as e:
                print(f"ERROR: Failed to process '{song.title}': {str(e)}")
                raise e

    except Exception as e:
        print(f"ERROR: Failed to process songs file: {str(e)}")
        raise e


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
