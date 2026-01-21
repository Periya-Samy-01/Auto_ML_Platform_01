"""
Cloudflare R2 Service
Handles all R2 storage operations for dataset files
"""

import os
import hashlib
import logging
from typing import Optional, Tuple
from datetime import datetime, timedelta
import uuid

import boto3
from botocore.exceptions import ClientError
from botocore.client import Config

from app.core.config import settings

logger = logging.getLogger(__name__)


class R2Service:
    """Service for interacting with Cloudflare R2 storage"""
    
    def __init__(self):
        """Initialize R2 client with credentials from environment"""
        self.bucket_name = settings.R2_BUCKET_NAME
        
        # Create S3 client configured for R2
        self.client = boto3.client(
            's3',
            endpoint_url=settings.R2_ENDPOINT_URL,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            config=Config(signature_version='s3v4'),
            region_name='auto'  # R2 doesn't use regions, but boto3 requires it
        )
        
        # Ensure bucket exists
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self) -> None:
        """Create bucket if it doesn't exist and configure CORS"""
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"R2 bucket '{self.bucket_name}' verified")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                try:
                    self.client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"Created R2 bucket '{self.bucket_name}'")
                except Exception as create_error:
                    logger.error(f"Failed to create bucket: {create_error}")
                    raise
            else:
                logger.error(f"Error checking bucket: {e}")
                raise
        
        # Configure CORS for browser uploads
        self._configure_cors()
    
    def _configure_cors(self) -> None:
        """Configure CORS rules for browser-based uploads"""
        cors_configuration = {
            'CORSRules': [
                {
                    'AllowedHeaders': ['*'],
                    'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE', 'HEAD'],
                    'AllowedOrigins': ['http://localhost:3000', 'http://127.0.0.1:3000'],
                    'ExposeHeaders': ['ETag', 'Content-Length'],
                    'MaxAgeSeconds': 3600
                }
            ]
        }
        try:
            self.client.put_bucket_cors(
                Bucket=self.bucket_name,
                CORSConfiguration=cors_configuration
            )
            logger.info(f"CORS configured for bucket '{self.bucket_name}'")
        except Exception as e:
            logger.warning(f"Could not configure CORS (may already be set): {e}")
    
    def generate_presigned_upload_url(
        self, 
        upload_id: str,
        filename: str,
        content_type: str = 'application/octet-stream',
        expires_in: int = 3600
    ) -> Tuple[str, datetime]:
        """
        Generate a presigned URL for direct upload to R2
        
        Args:
            upload_id: Unique identifier for this upload
            filename: Original filename (for extension)
            content_type: MIME type of the file
            expires_in: URL expiration in seconds (default: 1 hour)
            
        Returns:
            Tuple of (presigned_url, expiration_datetime)
        """
        # Extract file extension
        extension = os.path.splitext(filename)[1].lower()
        
        # Create R2 key for temp upload
        key = f"uploads/temp/{upload_id}{extension}"
        
        try:
            # NOTE: We deliberately don't include ContentType in the signature
            # This allows the frontend to send any content-type
            url = self.client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key,
                },
                ExpiresIn=expires_in
            )
            
            expiration = datetime.utcnow() + timedelta(seconds=expires_in)
            logger.info(f"Generated presigned URL for upload: {key}")
            
            return url, expiration
            
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise
    
    def upload_file_to_r2(
        self,
        local_path: str,
        r2_key: str,
        content_type: str = 'application/octet-stream'
    ) -> int:
        """
        Upload a file from local filesystem to R2
        
        Args:
            local_path: Path to local file
            r2_key: Destination key in R2
            content_type: MIME type
            
        Returns:
            Size of uploaded file in bytes
        """
        try:
            # Get file size
            file_size = os.path.getsize(local_path)
            
            # Upload file
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
            logger.error(f"Failed to upload file to R2: {e}")
            raise
    
    def download_file_from_r2(
        self,
        r2_key: str,
        local_path: str
    ) -> str:
        """
        Download a file from R2 to local filesystem
        
        Args:
            r2_key: Source key in R2
            local_path: Destination local path
            
        Returns:
            Path to downloaded file
        """
        try:
            # Ensure local directory exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Download file
            self.client.download_file(
                self.bucket_name,
                r2_key,
                local_path
            )
            
            logger.info(f"Downloaded {r2_key} to {local_path}")
            return local_path
            
        except Exception as e:
            logger.error(f"Failed to download file from R2: {e}")
            raise
    
    def delete_file_from_r2(self, r2_key: str) -> None:
        """
        Delete a file from R2
        
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
            logger.error(f"Failed to delete file from R2: {e}")
            raise
    
    def move_to_deleted_folder(
        self,
        source_key: str,
        dataset_id: str
    ) -> str:
        """
        Move a file to the deleted folder (for soft delete)
        
        Args:
            source_key: Current key in R2
            dataset_id: Dataset ID for organizing deleted files
            
        Returns:
            New key in deleted folder
        """
        try:
            # Generate destination key
            filename = os.path.basename(source_key)
            dest_key = f"deleted/{dataset_id}/{filename}"
            
            # Copy to new location
            self.client.copy_object(
                Bucket=self.bucket_name,
                CopySource={'Bucket': self.bucket_name, 'Key': source_key},
                Key=dest_key
            )
            
            # Delete original
            self.delete_file_from_r2(source_key)
            
            logger.info(f"Moved {source_key} to {dest_key}")
            return dest_key
            
        except Exception as e:
            logger.error(f"Failed to move file to deleted folder: {e}")
            raise
    
    def check_file_exists(self, r2_key: str) -> bool:
        """
        Check if a file exists in R2
        
        Args:
            r2_key: Key to check
            
        Returns:
            True if file exists, False otherwise
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
    
    def get_file_size(self, r2_key: str) -> Optional[int]:
        """
        Get the size of a file in R2
        
        Args:
            r2_key: Key to check
            
        Returns:
            File size in bytes, or None if file doesn't exist
        """
        try:
            response = self.client.head_object(
                Bucket=self.bucket_name,
                Key=r2_key
            )
            return response['ContentLength']
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return None
            raise
    
    def compute_file_checksum(self, local_path: str) -> str:
        """
        Compute SHA-256 checksum of a local file
        
        Args:
            local_path: Path to local file
            
        Returns:
            SHA-256 hash as hex string
        """
        sha256_hash = hashlib.sha256()
        with open(local_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def generate_download_url(
        self,
        r2_key: str,
        expires_in: int = 3600
    ) -> str:
        """
        Generate a presigned URL for downloading a file
        
        Args:
            r2_key: Key to generate URL for
            expires_in: URL expiration in seconds (default: 1 hour)
            
        Returns:
            Presigned download URL
        """
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': r2_key,
                },
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate download URL: {e}")
            raise


# Singleton instance
r2_service = R2Service()
