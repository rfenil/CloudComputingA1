
import pydantic
import boto3
import requests
import json
from pydantic import BaseModel

# AWS S3 Configuration
S3_BUCKET_NAME = "a1-projectgroup-31"
s3_client = boto3.client("s3")


json_file_name = "2025a1.json"
with open(json_file_name, "r", encoding="utf-8") as file:
    data = json.load(file)

# To enforece data consistency and type saftey so that data follows the expected format
class Song(BaseModel):
    title: str
    artist: str
    year: str
    album: str
    img_url: str

# Function to upload images to s3
def upload_image_to_s3(image_content, image_name):
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=f"artist_images/{image_name}",
            Body=image_content,
            ContentType="image/jpeg"
        )
        print(f"Uploaded: {image_name} to S3.")
    except Exception as e:
        print(f"Error uploading {image_name}: {e}")

# Function to check for duplicate url's
def process_images():
    unique_urls = set()  

    for song_data in data.get("songs", []):
        try:
            song = Song(**song_data) 
            img_url = song.img_url

            # Check for duplicate URLs
            if img_url in unique_urls:
                print(f" Duplicate image URL found: {img_url}. Skipping upload.")
                continue
            unique_urls.add(img_url)
            img_name = img_url.split("/")[-1]
            response = requests.get(img_url, stream=True)
            if response.status_code == 200:
                upload_image_to_s3(response.content, img_name)
            else:
                print(f"Failed to download image: {img_name}")
        except Exception as e:
            print(f"Error processing {song.title}: {e}")

if __name__ == "__main__":
    process_images()
    print("All unique images processed and uploaded to S3!")
