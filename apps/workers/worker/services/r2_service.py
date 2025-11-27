"""
R2 Service for Workers
Handles Cloudflare R2 operations in worker context
"""

import os
import hashlib
import logging
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from botocore.client import Config

logger = logging.getLogger(__name__)


class R2Service:
    """R2 service for worker operations"""
    
    def __init__(self):
        """Initialize R2 client from environment"""
        # Get credentials from environment
        self.account_id = os.getenv("R2_ACCOUNT_ID", "")
        self.access_key = os.getenv("R2_ACCESS_KEY_ID", "")
        self.secret_key = os.getenv("R2_SECRET_ACCESS_KEY", "")
        self.bucket_name = os.getenv("R2_BUCKET_NAME", "automl-datasets-production")
        
        # Build endpoint URL
        if self.account_id:
            self.endpoint_url = f"https://{self.account_id}.r2.cloudflarestorage.com"
        else:
            self.endpoint_url = os.getenv("R2_ENDPOINT_URL", "")
        
        # Create S3 client
        self.client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )
    
    def download_file_from_r2(self, r2_key: str, local_path: str) -> str:
        """
        Download file from R2 to local filesystem
        
        Args:
            r2_key: Source key in R2
            local_path: Destination local path
            
        Returns:
            Path to downloaded file
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Download file
            self.client.download_file(
                self.bucket_name,
                r2_key,
                local_path
            )
            
            logger.info(f"Downloaded {r2_key} to {local_path}")
            return local_path
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                raise FileNotFoundError(f"File not found in R2: {r2_key}")
            logger.error(f"Failed to download from R2: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to download from R2: {e}")
            raise
    
    def upload_file_to_r2(
        self,
        local_path: str,
        r2_key: str,
        content_type: str = 'application/octet-stream'
    ) -> int:
        """
        Upload file to R2
        
        Args:
            local_path: Local file path
            r2_key: Destination key in R2
            content_type: MIME type
            
        Returns:
            File size in bytes
        """
        try:
            file_size = os.path.getsize(local_path)
            
            with open(local_path, 'rb') as f:
                self.client.put_object(
                    Bucket=self.bucket_name,
                    Key=r2_key,
                    Body=f,
                    ContentType=content_type
                )
            
            logger.info(f"Uploaded {file_size} bytes to {r2_key}")
            return file_size
            
        except Exception as e:
            logger.error(f"Failed to upload to R2: {e}")
            raise
    
    def delete_file_from_r2(self, r2_key: str) -> None:
        """
        Delete file from R2
        
        Args:
            r2_key: Key to delete
        """
        try:
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=r2_key
            )
            logger.info(f"Deleted {r2_key} from R2")
            
        except Exception as e:
            logger.error(f"Failed to delete from R2: {e}")
            # Don't raise - deletion failures shouldn't stop processing
    
    def compute_file_checksum(self, local_path: str) -> str:
        """
        Compute SHA-256 checksum of file
        
        Args:
            local_path: Path to file
            
        Returns:
            SHA-256 hash as hex string
        """
        sha256_hash = hashlib.sha256()
        with open(local_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def check_file_exists(self, r2_key: str) -> bool:
        """
        Check if file exists in R2
        
        Args:
            r2_key: Key to check
            
        Returns:
            True if exists, False otherwise
        """
        try:
            self.client.head_object(
                Bucket=self.bucket_name,
                Key=r2_key
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise
