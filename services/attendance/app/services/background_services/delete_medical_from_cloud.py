import boto3
import os
import logging
from urllib.parse import urlparse
from dotenv import load_dotenv
from pathlib import Path
from botocore.exceptions import ClientError

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

BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

async def delete_medical_from_cloud(s3_url: str):
    """
    Delete a medical file from AWS S3.
    
    Args:
        s3_url (str): The S3 URL of the file to delete
        
    Raises:
        ValueError: If s3_url is None or empty
        Exception: If deletion fails
    """
    if not s3_url:
        raise ValueError("S3 URL cannot be None or empty")

    try:
        parsed_url = urlparse(s3_url)
        if not parsed_url.path:
            raise ValueError("Invalid S3 URL format")
            
        key = parsed_url.path.lstrip('/')  # Remove leading '/'
        logger.info(f"Attempting to delete file with key: {key} from bucket: {BUCKET_NAME}")
        
        response = s3.delete_object(Bucket=BUCKET_NAME, Key=key)
        
        # Check if deletion was successful
        if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 204:
            logger.info(f"Successfully deleted file: {key}")
            return True
        else:
            raise Exception(f"Unexpected response from S3: {response}")
            
    except ClientError as e:
        error_message = f"AWS S3 error: {str(e)}"
        logger.error(error_message)
        raise Exception(error_message)
    except Exception as e:
        error_message = f"Failed to delete file from S3: {str(e)}"
        logger.error(error_message)
        raise Exception(error_message)

