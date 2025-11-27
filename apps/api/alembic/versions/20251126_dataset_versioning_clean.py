"""dataset versioning clean (architecture aligned)

Revision ID: 20251126_dataset_versioning_clean
Revises: a1b2c3d4e5f6_add_missing_constraints_triggers
Create Date: 2025-11-26

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers
revision = '20251126_dataset_vers_clean'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add dataset versioning tables (aligned with architecture doc models)"""
    
    # Drop old enum types from previous migration (if they exist)
    # This handles the case where old migration was partially applied
    op.execute("DROP TYPE IF EXISTS fileformat CASCADE")
    op.execute("DROP TYPE IF EXISTS processingstatus CASCADE")
    op.execute("DROP TYPE IF EXISTS ingestion_status CASCADE")  # Old name variant
    
    # Create enum type objects (they'll be created automatically when first used)
    # We create them here so they can be reused in multiple column definitions
    file_format_enum = sa.Enum('csv', 'json', 'parquet', 'excel', 'unknown', name='fileformat')
    processing_status_enum = sa.Enum('pending', 'processing', 'completed', 'failed', name='processingstatus')
    
    # =============================================================================
    # 1. CREATE DATASET_VERSIONS TABLE
    # =============================================================================
    op.create_table(
        'dataset_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        
        # Storage paths (using s3_path for S3-compatible R2)
        sa.Column('s3_path', sa.Text(), nullable=False,
                  comment='Path in R2: datasets/<user_id>/<version_id>.parquet'),
        
        # Original file info
        sa.Column('original_filename', sa.Text(), nullable=False),
        sa.Column('original_format', file_format_enum, nullable=False),
        
        # Size metrics
        sa.Column('original_size_bytes', sa.BigInteger(), nullable=True),
        sa.Column('parquet_size_bytes', sa.BigInteger(), nullable=True),
        
        # Data shape (NULL until processing completes)
        sa.Column('row_count', sa.BigInteger(), nullable=True),
        sa.Column('column_count', sa.Integer(), nullable=True),
        
        # Schema (using columns_metadata per architecture doc)
        sa.Column('columns_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True,
                  comment='Structural schema: {columns: [{name, dtype, null_count}]}'),
        
        # Processing state
        sa.Column('processing_status', processing_status_enum,
                  nullable=False, 
                  server_default='pending'),
        
        # Timestamp
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, 
                  server_default=sa.func.now()),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('dataset_id', 'version_number', name='ux_dataset_version_number'),
        sa.CheckConstraint('original_size_bytes IS NULL OR original_size_bytes >= 0', 
                         name='ck_dataset_versions_original_size'),
        sa.CheckConstraint('parquet_size_bytes IS NULL OR parquet_size_bytes >= 0', 
                         name='ck_dataset_versions_parquet_size'),
        sa.CheckConstraint('row_count IS NULL OR row_count >= 0', 
                         name='ck_dataset_versions_row_count'),
        sa.CheckConstraint('column_count IS NULL OR column_count >= 0', 
                         name='ck_dataset_versions_column_count'),
    )
    
    # Indexes
    op.create_index('idx_dataset_versions_dataset_id', 'dataset_versions', ['dataset_id'])
    op.create_index('idx_dataset_versions_status', 'dataset_versions', ['processing_status'])
    op.create_index('idx_dataset_versions_created_at', 'dataset_versions', ['created_at'])
    op.create_index('idx_dataset_versions_metadata_gin', 'dataset_versions', ['columns_metadata'], 
                    postgresql_using='gin')
    
    # =============================================================================
    # 2. CREATE DATASET_PROFILES TABLE
    # =============================================================================
    op.create_table(
        'dataset_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        
        # FK to dataset_versions (using dataset_version_id per architecture doc)
        sa.Column('dataset_version_id', postgresql.UUID(as_uuid=True), nullable=False),
        
        # Profile data (using profile_data per architecture doc)
        sa.Column('profile_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False,
                  comment='Statistical profile following architecture doc format'),
        
        # Timestamp
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, 
                  server_default=sa.func.now()),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['dataset_version_id'], ['dataset_versions.id'], 
                               ondelete='CASCADE'),
        sa.UniqueConstraint('dataset_version_id', name='ux_profile_dataset_version'),
    )
    
    # Indexes
    op.create_index('idx_profiles_dataset_version_id', 'dataset_profiles', 
                    ['dataset_version_id'])
    
    # =============================================================================
    # 3. CREATE INGESTION_JOBS TABLE
    # =============================================================================
    op.create_table(
        'ingestion_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        
        # References
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('dataset_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('dataset_version_id', postgresql.UUID(as_uuid=True), nullable=True,
                  comment='FK to dataset_versions (not version_id for consistency)'),
        
        # Upload info
        sa.Column('upload_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('original_filename', sa.Text(), nullable=False),
        sa.Column('original_size_bytes', sa.BigInteger(), nullable=False),
        
        # Job state
        sa.Column('status', sa.Text(), nullable=False, server_default='pending'),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        
        # Error tracking
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_traceback', sa.Text(), nullable=True),
        
        # Task tracking
        sa.Column('celery_task_id', sa.Text(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, 
                  server_default=sa.func.now()),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['dataset_id'], ['datasets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['dataset_version_id'], ['dataset_versions.id'], 
                               ondelete='SET NULL'),
        sa.CheckConstraint("status IN ('pending', 'processing', 'completed', 'failed')", 
                         name='chk_ingestion_status'),
        sa.CheckConstraint('original_size_bytes >= 0', name='ck_ingestion_jobs_size'),
        sa.CheckConstraint('retry_count >= 0', name='ck_ingestion_jobs_retry')
    )
    
    # Indexes
    op.create_index('idx_ingestion_jobs_user_id', 'ingestion_jobs', ['user_id'])
    op.create_index('idx_ingestion_jobs_dataset_id', 'ingestion_jobs', ['dataset_id'])
    op.create_index('idx_ingestion_jobs_dataset_version_id', 'ingestion_jobs', 
                    ['dataset_version_id'])
    op.create_index('idx_ingestion_jobs_status', 'ingestion_jobs', ['status'])
    op.create_index('idx_ingestion_jobs_created_at', 'ingestion_jobs', ['created_at'])
    
    # =============================================================================
    # 4. UPDATE DATASETS TABLE
    # =============================================================================
    
    # Add current_version_id FK (points to latest completed version)
    op.add_column('datasets', 
                  sa.Column('current_version_id', postgresql.UUID(as_uuid=True), 
                           nullable=True))
    
    # Add foreign key constraint
    op.create_foreign_key('fk_datasets_current_version', 
                         'datasets', 'dataset_versions', 
                         ['current_version_id'], ['id'], 
                         ondelete='SET NULL')
    
    # Add indexes
    op.create_index('idx_datasets_current_version', 'datasets', ['current_version_id'])
    op.create_index('idx_datasets_problem_type', 'datasets', ['problem_type'])
    
    # =============================================================================
    # 5. ADD TABLE COMMENTS
    # =============================================================================
    op.execute("""
        COMMENT ON TABLE datasets IS 
        'Dataset containers (minimal). Each dataset can have multiple versions.';
    """)
    
    op.execute("""
        COMMENT ON TABLE dataset_versions IS 
        'Immutable dataset versions. Each row points to a Parquet file in R2.';
    """)
    
    op.execute("""
        COMMENT ON TABLE dataset_profiles IS 
        'Statistical profiles computed during ingestion.';
    """)
    
    op.execute("""
        COMMENT ON TABLE ingestion_jobs IS 
        'Tracks async dataset processing jobs. Source of truth for job status.';
    """)


def downgrade() -> None:
    """Remove dataset versioning support"""
    
    # Drop foreign key and indexes on datasets
    op.drop_constraint('fk_datasets_current_version', 'datasets', type_='foreignkey')
    op.drop_index('idx_datasets_current_version', table_name='datasets')
    op.drop_index('idx_datasets_problem_type', table_name='datasets')
    
    # Remove column from datasets
    op.drop_column('datasets', 'current_version_id')
    
    # Drop tables (cascade will handle FKs)
    op.drop_table('ingestion_jobs')
    op.drop_table('dataset_profiles')
    op.drop_table('dataset_versions')
    
    # Drop enum types (only if not used elsewhere)
    op.execute('DROP TYPE IF EXISTS processingstatus CASCADE')
    op.execute('DROP TYPE IF EXISTS fileformat CASCADE')
