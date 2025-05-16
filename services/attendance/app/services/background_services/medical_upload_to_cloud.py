import boto3
from botocore.exceptions import NoCredentialsError
import uuid, os
from dotenv import load_dotenv
from pathlib import Path

# Go up 2 levels from services/api/utils to reach project root
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

def medical_upload_to_cloud(file_obj, filename, content_type):
    unique_filename = f"{uuid.uuid4()}_{filename}"
    try:
        s3.upload_fileobj(
            file_obj,
            AWS_BUCKET_NAME,
            unique_filename,
            ExtraArgs={"ContentType": content_type}
        )
        url = f"https://{AWS_BUCKET_NAME}.s3.amazonaws.com/{unique_filename}"
        return url
    except NoCredentialsError:
        return None