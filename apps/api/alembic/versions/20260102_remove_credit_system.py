"""Remove credit system

Revision ID: remove_credit_system
Revises: a1b2c3d4e5f6
Create Date: 2026-01-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'remove_credit_system'
down_revision: Union[str, None] = '20251126_dataset_vers_clean'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove credit-related columns, tables, and constraints."""
    
    # Drop credit-related triggers first (if they exist)
    op.execute("DROP TRIGGER IF EXISTS update_user_balance_trigger ON credit_transactions")
    op.execute("DROP FUNCTION IF EXISTS update_user_credit_balance()")
    
    # Drop credit_transactions table if exists
    op.execute("DROP TABLE IF EXISTS credit_transactions CASCADE")
    
    # Drop credit_packages table if exists
    op.execute("DROP TABLE IF EXISTS credit_packages CASCADE")
    
    # Drop credit_balance constraint from users table
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS ck_users_credit_balance")
    
    # Drop credits_cost column from jobs table if exists
    op.execute("ALTER TABLE jobs DROP COLUMN IF EXISTS credits_cost")
    
    # Drop credit_balance column from users table
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS credit_balance")


def downgrade() -> None:
    """Re-add credit system (not recommended)."""
    # Add credit_balance back to users
    op.add_column('users', sa.Column('credit_balance', sa.BigInteger(), nullable=False, server_default='0'))
    op.create_check_constraint('ck_users_credit_balance', 'users', 'credit_balance >= 0')
    
    # Add credits_cost back to jobs
    op.add_column('jobs', sa.Column('credits_cost', sa.Integer(), nullable=False, server_default='0'))
