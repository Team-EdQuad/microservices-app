import boto3
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from pathlib import Path

# Go up 2 levels from services/api/utils to reach project root
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

async def delete_medical_from_cloud(s3_url: str):
    try:
        parsed_url = urlparse(s3_url)
        key = parsed_url.path.lstrip('/')  # Remove leading '/'
        s3.delete_object(Bucket=BUCKET_NAME, Key=key)
    except Exception as e:
        raise Exception(f"Failed to delete file from S3: {str(e)}")

