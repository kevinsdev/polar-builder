"""
Cloud Storage Module for Polar Builder API
Provides S3-compatible cloud storage functionality for file operations
"""

import boto3
import os
import io
import logging
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional, BinaryIO

logger = logging.getLogger(__name__)

class CloudStorage:
    """S3-compatible cloud storage handler"""
    
    def __init__(self):
        """Initialize cloud storage client"""
        self.bucket_name = os.getenv('S3_BUCKET_NAME', 'polar-builder-files')
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            logger.info(f"Cloud storage initialized for bucket: {self.bucket_name}")
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            self.s3_client = None
    
    def upload_file(self, file_data: BinaryIO, key: str, content_type: str = 'application/octet-stream') -> bool:
        """
        Upload file data to cloud storage
        
        Args:
            file_data: File-like object containing the data
            key: Storage key/path for the file
            content_type: MIME type of the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.s3_client:
            logger.error("S3 client not initialized")
            return False
            
        try:
            # Reset file pointer to beginning
            file_data.seek(0)
            
            self.s3_client.upload_fileobj(
                file_data,
                self.bucket_name,
                key,
                ExtraArgs={'ContentType': content_type}
            )
            logger.info(f"Successfully uploaded file: {key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to upload file {key}: {e}")
            return False
    
    def download_file(self, key: str) -> Optional[bytes]:
        """
        Download file from cloud storage
        
        Args:
            key: Storage key/path of the file
            
        Returns:
            bytes: File content if successful, None otherwise
        """
        if not self.s3_client:
            logger.error("S3 client not initialized")
            return None
            
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            content = response['Body'].read()
            logger.info(f"Successfully downloaded file: {key}")
            return content
            
        except ClientError as e:
            logger.error(f"Failed to download file {key}: {e}")
            return None
    
    def download_file_stream(self, key: str) -> Optional[io.BytesIO]:
        """
        Download file as stream from cloud storage
        
        Args:
            key: Storage key/path of the file
            
        Returns:
            io.BytesIO: File stream if successful, None otherwise
        """
        content = self.download_file(key)
        if content:
            return io.BytesIO(content)
        return None
    
    def delete_file(self, key: str) -> bool:
        """
        Delete file from cloud storage
        
        Args:
            key: Storage key/path of the file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.s3_client:
            logger.error("S3 client not initialized")
            return False
            
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"Successfully deleted file: {key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete file {key}: {e}")
            return False
    
    def file_exists(self, key: str) -> bool:
        """
        Check if file exists in cloud storage
        
        Args:
            key: Storage key/path of the file
            
        Returns:
            bool: True if file exists, False otherwise
        """
        if not self.s3_client:
            logger.error("S3 client not initialized")
            return False
            
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False
    
    def list_files(self, prefix: str = '') -> list:
        """
        List files in cloud storage with optional prefix
        
        Args:
            prefix: Optional prefix to filter files
            
        Returns:
            list: List of file keys
        """
        if not self.s3_client:
            logger.error("S3 client not initialized")
            return []
            
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            files = []
            if 'Contents' in response:
                files = [obj['Key'] for obj in response['Contents']]
            
            logger.info(f"Listed {len(files)} files with prefix: {prefix}")
            return files
            
        except ClientError as e:
            logger.error(f"Failed to list files with prefix {prefix}: {e}")
            return []
    
    def get_file_url(self, key: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate presigned URL for file access
        
        Args:
            key: Storage key/path of the file
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            str: Presigned URL if successful, None otherwise
        """
        if not self.s3_client:
            logger.error("S3 client not initialized")
            return None
            
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expiration
            )
            logger.info(f"Generated presigned URL for: {key}")
            return url
            
        except ClientError as e:
            logger.error(f"Failed to generate URL for {key}: {e}")
            return None

# Global cloud storage instance
cloud_storage = CloudStorage()

