import boto3
import logging
from botocore.exceptions import NoCredentialsError, ClientError
import uuid
import os
from dotenv import load_dotenv
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Validate required environment variables
required_env_vars = [
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_REGION",
    "AWS_BUCKET_NAME"
]

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Initialize S3 client
try:
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
    )
except Exception as e:
    logger.error(f"Failed to initialize S3 client: {str(e)}")
    raise

AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

def medical_upload_to_cloud(file_obj, filename, content_type):
    """
    Upload a medical file to AWS S3.
    
    Args:
        file_obj: File object to upload
        filename (str): Original filename
        content_type (str): MIME type of the file
        
    Returns:
        str: URL of the uploaded file in S3
        
    Raises:
        ValueError: If any required parameter is None
        Exception: If upload fails
    """
    if not all([file_obj, filename, content_type]):
        raise ValueError("All parameters (file_obj, filename, content_type) are required")

    try:
        unique_filename = f"{uuid.uuid4()}_{filename}"
        logger.info(f"Attempting to upload file: {filename} as {unique_filename}")

        s3.upload_fileobj(
            file_obj,
            AWS_BUCKET_NAME,
            unique_filename,
            ExtraArgs={"ContentType": content_type}
        )
        
        url = f"https://{AWS_BUCKET_NAME}.s3.amazonaws.com/{unique_filename}"
        logger.info(f"Successfully uploaded file to: {url}")
        return url

    except NoCredentialsError as e:
        error_message = "AWS credentials not found or invalid"
        logger.error(error_message)
        raise Exception(error_message)
    except ClientError as e:
        error_message = f"AWS S3 error: {str(e)}"
        logger.error(error_message)
        raise Exception(error_message)
    except Exception as e:
        error_message = f"Failed to upload file to S3: {str(e)}"
        logger.error(error_message)
        raise Exception(error_message)