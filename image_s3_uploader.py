import boto3
import requests
import json
import os

# AWS S3 Configuration and s3 initialization
S3_BUCKET_NAME = "a1-projectgroup-31"  
s3_client_initialize = boto3.client("s3")

json_file_path = r"C:\Users\prajw\OneDrive\Desktop\RMIT_SEM3\CloudComputing\Cloud_A1\2025a1.json"

with open(json_file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Creating a directory to store downloaded images
image_dir = r"C:\Users\prajw\OneDrive\Pictures\artist_images"
os.makedirs(image_dir, exist_ok=True)

# Process each song entry
for song in data.get("songs", []):  
    if "img_url" in song and song["img_url"]:  
        img_url = song["img_url"]
        img_name = img_url.split("/")[-1]  
        img_path = os.path.join(image_dir, img_name)
        try:
            response = requests.get(img_url, stream=True)
            if response.status_code == 200:
                with open(img_path, "wb") as img_file:
                    for chunk in response.iter_content(1024):
                        img_file.write(chunk)
                print(f"Downloaded: {img_name}")

                s3_client_initialize.upload_file(img_path, S3_BUCKET_NAME, f"artist_images/{img_name}")
                print(f"Uploaded to S3: s3://{S3_BUCKET_NAME}/artist_images/{img_name}")

        except Exception as e:
            print(f"Error downloading {img_url}: {e}")

print("All images processed successfully!") 
