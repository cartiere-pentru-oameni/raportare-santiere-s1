"""S3-compatible storage helper for Hetzner Object Storage"""

import boto3
from botocore.exceptions import ClientError
from botocore.config import Config as BotoConfig
from app.config import Config


class S3Storage:
    """S3-compatible storage client"""

    def __init__(self):
        """Initialize S3 client"""
        self.client = boto3.client(
            's3',
            endpoint_url=Config.S3_ENDPOINT,
            aws_access_key_id=Config.S3_ACCESS_KEY,
            aws_secret_access_key=Config.S3_SECRET_KEY,
            region_name=Config.S3_REGION,
            config=BotoConfig(signature_version='s3v4')
        )
        self.bucket = Config.S3_BUCKET

    def upload(self, key, data, content_type='image/jpeg'):
        """
        Upload file to S3

        Args:
            key: Storage path (e.g., "report_id/uuid.jpg")
            data: File data (bytes)
            content_type: Content type (default: image/jpeg)

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=data,
                ContentType=content_type
            )
            return True
        except ClientError as e:
            print(f"Error uploading to S3: {e}")
            return False

    def download(self, key):
        """
        Download file from S3

        Args:
            key: Storage path

        Returns:
            File data (bytes) or None if error
        """
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return response['Body'].read()
        except ClientError as e:
            print(f"Error downloading from S3: {e}")
            return None

    def delete(self, key):
        """
        Delete file from S3

        Args:
            key: Storage path

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as e:
            print(f"Error deleting from S3: {e}")
            return False

    def create_signed_url(self, key, expiration=3600):
        """
        Create a presigned URL for private bucket access

        Args:
            key: Storage path
            expiration: URL expiration time in seconds (default: 1 hour)

        Returns:
            Signed URL string or None if error
        """
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error creating signed URL: {e}")
            return None

    def exists(self, key):
        """
        Check if file exists in S3

        Args:
            key: Storage path

        Returns:
            True if exists, False otherwise
        """
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False


# Global storage instance
storage = S3Storage()
