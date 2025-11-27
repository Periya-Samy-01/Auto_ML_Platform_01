"""add_oauth_fields

Revision ID: 298fe3553ae6
Revises: a4ea1226660c
Create Date: 2025-11-22 23:40:19.515408

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '298fe3553ae6'
down_revision: Union[str, None] = 'a4ea1226660c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create the OAuth provider enum type
    oauth_provider_enum = sa.Enum('GOOGLE', 'GITHUB', 'EMAIL', name='oauthprovider')
    oauth_provider_enum.create(op.get_bind(), checkfirst=True)
    
    # Add OAuth columns to users table
    op.add_column('users', sa.Column('oauth_provider', oauth_provider_enum, nullable=True))
    op.add_column('users', sa.Column('oauth_id', sa.String(length=255), nullable=True))
    
    # Make password_hash nullable (for OAuth users)
    op.alter_column('users', 'password_hash',
               existing_type=sa.TEXT(),
               nullable=True)
    
    # Create index for OAuth lookups
    op.create_index('idx_users_oauth', 'users', ['oauth_provider', 'oauth_id'], unique=False)


def downgrade() -> None:
    """Downgrade database schema."""
    # Drop the OAuth index
    op.drop_index('idx_users_oauth', table_name='users')
    
    # Make password_hash required again
    op.alter_column('users', 'password_hash',
               existing_type=sa.TEXT(),
               nullable=False)
    
    # Drop OAuth columns
    op.drop_column('users', 'oauth_id')
    op.drop_column('users', 'oauth_provider')
    
    # Drop the OAuth provider enum type
    oauth_provider_enum = sa.Enum('GOOGLE', 'GITHUB', 'EMAIL', name='oauthprovider')
    oauth_provider_enum.drop(op.get_bind(), checkfirst=True)
