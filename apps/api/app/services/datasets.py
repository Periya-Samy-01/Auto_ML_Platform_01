"""
Dataset Service
Business logic for dataset operations
"""

import uuid
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import Session, selectinload

from packages.database.models import (
    Dataset, 
    DatasetVersion, 
    DatasetProfile,
    IngestionJob,
    User
)
from packages.database.models.enums import FileFormat, ProblemType, UserTier
from app.core.config import settings
from app.services.cache import cache_service

logger = logging.getLogger(__name__)


class DatasetService:
    """Service for dataset CRUD operations and version management"""
    
    @staticmethod
    def create_dataset(
        db: Session,
        user_id: uuid.UUID,
        name: str,
        description: Optional[str] = None,
        problem_type: Optional[ProblemType] = None,
        target_column: Optional[str] = None
    ) -> Dataset:
        """
        Create a new dataset container
        
        Args:
            db: Database session
            user_id: Owner user ID
            name: Dataset name
            description: Optional description
            problem_type: ML problem type
            target_column: Target column for ML
            
        Returns:
            Created dataset
        """
        # Check if dataset with same name exists for user
        existing = db.query(Dataset).filter(
            and_(
                Dataset.user_id == user_id,
                Dataset.name == name
            )
        ).first()
        
        if existing:
            raise ValueError(f"Dataset with name '{name}' already exists")
        
        # Check user's dataset limit
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Count user's existing datasets (triggers will maintain dataset_count)
        dataset_count = db.query(func.count(Dataset.id)).filter(
            Dataset.user_id == user_id
        ).scalar()
        
        # Check tier limits
        limits = {
            UserTier.FREE: settings.FREE_TIER_DATASET_LIMIT,
            UserTier.PRO: 100,  # Pro tier limits
            UserTier.ENTERPRISE: 1000  # Enterprise limits
        }
        
        if dataset_count >= limits.get(user.tier, 10):
            raise ValueError(f"Dataset limit reached for {user.tier} tier")
        
        # Create dataset (minimal container)
        dataset = Dataset(
            id=uuid.uuid4(),
            user_id=user_id,
            name=name,
            description=description,
            problem_type=problem_type,
            target_column=target_column,
            is_sample_dataset=False  # User-uploaded datasets are not samples
            # current_version_id will be set when first version completes
        )
        
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        
        # Invalidate user's dataset cache
        cache_service.invalidate_user_dataset_cache(str(user_id))
        
        logger.info(f"Created dataset {dataset.id} for user {user_id}")
        return dataset
    
    @staticmethod
    def get_dataset(
        db: Session,
        dataset_id: uuid.UUID,
        user_id: uuid.UUID,
        include_versions: bool = False
    ) -> Optional[Dataset]:
        """
        Get a dataset by ID
        
        Args:
            db: Database session
            dataset_id: Dataset ID
            user_id: User ID (for ownership check)
            include_versions: Whether to include version list
            
        Returns:
            Dataset or None if not found
        """
        query = db.query(Dataset).filter(
            and_(
                Dataset.id == dataset_id,
                Dataset.user_id == user_id
            )
        )
        
        if include_versions:
            query = query.options(selectinload(Dataset.versions))
        
        # Load current version (not latest_version)
        query = query.options(selectinload(Dataset.current_version))
        
        dataset = query.first()
        return dataset
    
    @staticmethod
    def list_user_datasets(
        db: Session,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
        problem_type: Optional[ProblemType] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> tuple[List[Dataset], int]:
        """
        List user's datasets with pagination
        
        Args:
            db: Database session
            user_id: User ID
            skip: Offset for pagination
            limit: Number of results
            problem_type: Filter by problem type
            search: Search in name/description
            sort_by: Sort field
            sort_order: asc or desc
            
        Returns:
            Tuple of (datasets, total_count)
        """
        # Check cache first
        cache_key = f"user:{user_id}:datasets:page:{skip//limit}"
        cached = cache_service.get_cached_user_datasets(str(user_id), skip//limit)
        
        if cached and not search and not problem_type:
            # Return cached if no filters
            total = cached.get('total', 0)
            return cached.get('datasets', []), total
        
        # Build query (no soft delete filtering since we removed those fields)
        query = db.query(Dataset).filter(
            Dataset.user_id == user_id
        )
        
        # Apply filters
        if problem_type:
            query = query.filter(Dataset.problem_type == problem_type)
        
        if search:
            search_filter = or_(
                Dataset.name.ilike(f"%{search}%"),
                Dataset.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Get total count
        total = query.count()
        
        # Apply sorting
        sort_column = getattr(Dataset, sort_by, Dataset.created_at)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(sort_column)
        
        # Apply pagination
        datasets = query.offset(skip).limit(limit).all()
        
        # Cache results if no filters
        # TODO: Fix caching - SQLAlchemy models need custom serialization
        # if not search and not problem_type:
        #     cache_data = {
        #         'datasets': [d.__dict__ for d in datasets],
        #         'total': total
        #     }
        #     cache_service.cache_user_datasets(
        #         str(user_id), 
        #         skip//limit, 
        #         cache_data
        #     )
        
        return datasets, total
    
    @staticmethod
    def delete_dataset(
        db: Session,
        dataset_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """
        Hard delete a dataset (CASCADE will handle versions, profiles, jobs)
        
        Args:
            db: Database session
            dataset_id: Dataset ID
            user_id: User ID (for ownership check)
            
        Returns:
            True if deleted, False if not found
        """
        dataset = db.query(Dataset).filter(
            and_(
                Dataset.id == dataset_id,
                Dataset.user_id == user_id
            )
        ).first()
        
        if not dataset:
            return False
        
        # Hard delete (CASCADE handles cleanup)
        db.delete(dataset)
        db.commit()
        
        # Invalidate caches
        cache_service.invalidate_dataset_cache(str(dataset_id))
        cache_service.invalidate_user_dataset_cache(str(user_id))
        
        logger.info(f"Deleted dataset {dataset_id}")
        return True
    
    @staticmethod
    def create_dataset_version(
        db: Session,
        dataset_id: uuid.UUID,
        upload_id: uuid.UUID,
        original_filename: str,
        original_size_bytes: int,
        original_format: FileFormat = FileFormat.CSV,
        version_label: Optional[str] = None
    ) -> DatasetVersion:
        """
        Create a new dataset version (pending processing)
        
        Args:
            db: Database session
            dataset_id: Parent dataset ID
            upload_id: Upload tracking ID
            original_filename: Original file name
            original_size_bytes: Original file size
            original_format: File format
            version_label: Optional version label
            
        Returns:
            Created dataset version
        """
        # Get dataset
        dataset = db.query(Dataset).filter(
            Dataset.id == dataset_id
        ).first()
        
        if not dataset:
            raise ValueError("Dataset not found")
        
        # Count existing versions to determine next version number
        version_count = db.query(func.count(DatasetVersion.id)).filter(
            DatasetVersion.dataset_id == dataset_id
        ).scalar()
        
        next_version = version_count + 1
        
        # Create version record (s3_path for S3-compatible R2)
        version = DatasetVersion(
            id=uuid.uuid4(),
            dataset_id=dataset_id,
            version_number=next_version,
            s3_path="",  # Will be updated after processing: datasets/<user_id>/<version_id>.parquet
            original_filename=original_filename,
            original_format=original_format,
            original_size_bytes=original_size_bytes,
            parquet_size_bytes=None,  # Will be updated
            row_count=None,  # Will be updated
            column_count=None,  # Will be updated
            columns_metadata=None,  # Will be updated with schema
            processing_status="pending"
        )
        
        db.add(version)
        db.commit()
        db.refresh(version)
        
        logger.info(f"Created version {version.id} (v{next_version}) for dataset {dataset_id}")
        return version
    
    @staticmethod
    def get_dataset_version(
        db: Session,
        version_id: uuid.UUID,
        include_profile: bool = False
    ) -> Optional[DatasetVersion]:
        """
        Get a specific dataset version
        
        Args:
            db: Database session
            version_id: Version ID
            include_profile: Whether to include profile
            
        Returns:
            DatasetVersion or None
        """
        query = db.query(DatasetVersion).filter(
            DatasetVersion.id == version_id
        )
        
        if include_profile:
            query = query.options(selectinload(DatasetVersion.profile))
        
        return query.first()
    
    @staticmethod
    def update_dataset_version_status(
        db: Session,
        version_id: uuid.UUID,
        status: str,
        s3_path: Optional[str] = None,
        parquet_size_bytes: Optional[int] = None,
        row_count: Optional[int] = None,
        column_count: Optional[int] = None,
        columns_metadata: Optional[dict] = None
    ) -> None:
        """
        Update dataset version after processing
        
        Args:
            db: Database session
            version_id: Version ID
            status: New status (pending, processing, completed, failed)
            s3_path: Path to parquet file in R2
            parquet_size_bytes: Size of parquet file
            row_count: Number of rows
            column_count: Number of columns
            columns_metadata: Schema information (architecture doc format)
        """
        version = db.query(DatasetVersion).filter(
            DatasetVersion.id == version_id
        ).first()
        
        if not version:
            raise ValueError("Version not found")
        
        # Update fields
        version.processing_status = status
        
        if s3_path:
            version.s3_path = s3_path
        if parquet_size_bytes is not None:
            version.parquet_size_bytes = parquet_size_bytes
        if row_count is not None:
            version.row_count = row_count
        if column_count is not None:
            version.column_count = column_count
        if columns_metadata:
            version.columns_metadata = columns_metadata
        
        db.commit()
        
        # If completed, update dataset's current_version_id
        if status == "completed":
            dataset = db.query(Dataset).filter(
                Dataset.id == version.dataset_id
            ).first()
            
            if dataset:
                dataset.current_version_id = version_id
                db.commit()
                
                logger.info(f"Set dataset {dataset.id} current version to {version_id}")
        
        # Cache schema if completed
        if status == "completed" and columns_metadata:
            cache_service.cache_schema(
                str(version.dataset_id),
                str(version_id),
                columns_metadata
            )
        
        logger.info(f"Updated version {version_id} status to {status}")
    
    @staticmethod
    def check_storage_quota(
        db: Session,
        user_id: uuid.UUID,
        additional_bytes: int
    ) -> bool:
        """
        Check if user has storage quota for upload
        
        Args:
            db: Database session
            user_id: User ID
            additional_bytes: Size of new upload
            
        Returns:
            True if within quota, False otherwise
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Get storage limits by tier (in bytes)
        limits = {
            UserTier.FREE: settings.MAX_UPLOAD_SIZE_MB_FREE * 1024 * 1024,
            UserTier.PRO: settings.MAX_UPLOAD_SIZE_MB_PRO * 1024 * 1024,
            UserTier.ENTERPRISE: settings.MAX_UPLOAD_SIZE_MB_ENTERPRISE * 1024 * 1024
        }
        
        max_storage = limits.get(user.tier, limits[UserTier.FREE])
        
        # Check current usage + new file
        new_total = user.storage_used_bytes + additional_bytes
        
        return new_total <= max_storage
    
    @staticmethod
    def list_dataset_versions(
        db: Session,
        dataset_id: uuid.UUID,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[DatasetVersion], int]:
        """
        List versions for a dataset
        
        Args:
            db: Database session
            dataset_id: Dataset ID
            user_id: User ID (for ownership check)
            skip: Offset
            limit: Page size
            
        Returns:
            Tuple of (versions, total_count)
        """
        # Verify ownership
        dataset = db.query(Dataset).filter(
            and_(
                Dataset.id == dataset_id,
                Dataset.user_id == user_id
            )
        ).first()
        
        if not dataset:
            raise ValueError("Dataset not found or access denied")
        
        # Query versions
        query = db.query(DatasetVersion).filter(
            DatasetVersion.dataset_id == dataset_id
        )
        
        total = query.count()
        
        # Order by version number descending (newest first)
        versions = query.order_by(
            desc(DatasetVersion.version_number)
        ).offset(skip).limit(limit).all()
        
        return versions, total


# Singleton instance
dataset_service = DatasetService()
