"""add missing constraints triggers and functions

Revision ID: a1b2c3d4e5f6
Revises: 298fe3553ae6
Create Date: 2024-11-23 12:00:00.000000

This migration adds all the missing database features that Alembic autogenerate missed:
- PostgreSQL uuid-ossp extension
- Case-insensitive email unique index
- All trigger functions for credit system, counters, and timestamps
- All trigger attachments

IMPORTANT: This is safe to run on existing databases.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '298fe3553ae6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================================
    # 1. CREATE EXTENSION
    # ============================================================
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # ============================================================
    # 2. CREATE MISSING INDEXES
    # ============================================================
    # Case-insensitive unique email constraint
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ux_users_email_ci 
        ON users (lower(email))
    """)
    
    # ============================================================
    # 3. CREATE TRIGGER FUNCTIONS
    # ============================================================
    
    # Generic updated_at trigger
    op.execute("""
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
          NEW.updated_at := now();
          RETURN NEW;
        END;
        $$
    """)
    
    # Credit transaction INSERT trigger (with row locking)
    op.execute("""
        CREATE OR REPLACE FUNCTION credit_tx_before_insert()
        RETURNS trigger
        LANGUAGE plpgsql AS $$
        DECLARE
          cur_balance bigint;
          new_balance bigint;
        BEGIN
          -- Lock user row to prevent race conditions
          SELECT credit_balance INTO cur_balance 
          FROM users 
          WHERE id = NEW.user_id 
          FOR UPDATE;
          
          IF NOT FOUND THEN
            RAISE EXCEPTION 'User % not found for credit transaction', NEW.user_id;
          END IF;

          new_balance := cur_balance + NEW.amount;

          -- Enforce non-negative balance policy
          IF new_balance < 0 THEN
            RAISE EXCEPTION 'Insufficient credits for user %. Balance would become %.', NEW.user_id, new_balance;
          END IF;

          -- Update user balance
          UPDATE users 
          SET credit_balance = new_balance, 
              updated_at = now() 
          WHERE id = NEW.user_id;
          
          -- Set balance_after in transaction record
          NEW.balance_after := new_balance;
          
          RETURN NEW;
        END;
        $$
    """)
    
    # Prevent modifications to credit_transactions (immutability)
    op.execute("""
        CREATE OR REPLACE FUNCTION credit_tx_no_update_delete()
        RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
          RAISE EXCEPTION 'credit_transactions are immutable (id=%)', COALESCE(OLD.id, NEW.id);
        END;
        $$
    """)
    
    # Dataset count triggers
    op.execute("""
        CREATE OR REPLACE FUNCTION users_inc_dataset_count()
        RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
          UPDATE users 
          SET dataset_count = dataset_count + 1, 
              updated_at = now() 
          WHERE id = NEW.user_id;
          RETURN NEW;
        END;
        $$
    """)
    
    op.execute("""
        CREATE OR REPLACE FUNCTION users_dec_dataset_count()
        RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
          UPDATE users 
          SET dataset_count = GREATEST(dataset_count - 1, 0), 
              updated_at = now() 
          WHERE id = OLD.user_id;
          RETURN OLD;
        END;
        $$
    """)
    
    # Workflow count triggers
    op.execute("""
        CREATE OR REPLACE FUNCTION users_inc_workflow_count()
        RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
          UPDATE users 
          SET workflow_count = workflow_count + 1, 
              updated_at = now() 
          WHERE id = NEW.user_id;
          RETURN NEW;
        END;
        $$
    """)
    
    op.execute("""
        CREATE OR REPLACE FUNCTION users_dec_workflow_count()
        RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
          UPDATE users 
          SET workflow_count = GREATEST(workflow_count - 1, 0), 
              updated_at = now() 
          WHERE id = OLD.user_id;
          RETURN OLD;
        END;
        $$
    """)
    
    # Model count triggers
    op.execute("""
        CREATE OR REPLACE FUNCTION users_inc_model_count()
        RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
          UPDATE users 
          SET model_count = model_count + 1, 
              updated_at = now() 
          WHERE id = NEW.user_id;
          RETURN NEW;
        END;
        $$
    """)
    
    op.execute("""
        CREATE OR REPLACE FUNCTION users_dec_model_count()
        RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
          UPDATE users 
          SET model_count = GREATEST(model_count - 1, 0), 
              updated_at = now() 
          WHERE id = OLD.user_id;
          RETURN OLD;
        END;
        $$
    """)
    
    # Storage usage triggers
    op.execute("""
        CREATE OR REPLACE FUNCTION users_adjust_storage_on_dataset_ins()
        RETURNS trigger
        LANGUAGE plpgsql AS $$
        DECLARE
          delta bigint;
        BEGIN
          delta := COALESCE(NEW.parquet_size_bytes, NEW.original_size_bytes, 0);
          UPDATE users 
          SET storage_used_bytes = storage_used_bytes + delta, 
              updated_at = now()
          WHERE id = NEW.user_id;
          RETURN NEW;
        END;
        $$
    """)
    
    op.execute("""
        CREATE OR REPLACE FUNCTION users_adjust_storage_on_dataset_del()
        RETURNS trigger
        LANGUAGE plpgsql AS $$
        DECLARE
          delta bigint;
        BEGIN
          delta := COALESCE(OLD.parquet_size_bytes, OLD.original_size_bytes, 0);
          UPDATE users 
          SET storage_used_bytes = GREATEST(storage_used_bytes - delta, 0), 
              updated_at = now()
          WHERE id = OLD.user_id;
          RETURN OLD;
        END;
        $$
    """)
    
    op.execute("""
        CREATE OR REPLACE FUNCTION users_adjust_storage_on_dataset_upd()
        RETURNS trigger
        LANGUAGE plpgsql AS $$
        DECLARE
          old_sz bigint := COALESCE(OLD.parquet_size_bytes, OLD.original_size_bytes, 0);
          new_sz bigint := COALESCE(NEW.parquet_size_bytes, NEW.original_size_bytes, 0);
          delta bigint := new_sz - old_sz;
        BEGIN
          IF delta <> 0 THEN
            UPDATE users 
            SET storage_used_bytes = GREATEST(storage_used_bytes + delta, 0), 
                updated_at = now()
            WHERE id = NEW.user_id;
          END IF;
          RETURN NEW;
        END;
        $$
    """)
    
    # ============================================================
    # 4. ATTACH TRIGGERS
    # ============================================================
    
    # Updated_at triggers
    op.execute("""
        CREATE TRIGGER trg_users_updated_at
        BEFORE UPDATE ON users
        FOR EACH ROW EXECUTE PROCEDURE set_updated_at()
    """)
    
    op.execute("""
        CREATE TRIGGER trg_datasets_updated_at
        BEFORE UPDATE ON datasets
        FOR EACH ROW EXECUTE PROCEDURE set_updated_at()
    """)
    
    op.execute("""
        CREATE TRIGGER trg_experiments_updated_at
        BEFORE UPDATE ON experiments
        FOR EACH ROW EXECUTE PROCEDURE set_updated_at()
    """)
    
    op.execute("""
        CREATE TRIGGER trg_tutorials_updated_at
        BEFORE UPDATE ON tutorials
        FOR EACH ROW EXECUTE PROCEDURE set_updated_at()
    """)
    
    # Credit transaction triggers (CRITICAL)
    op.execute("""
        CREATE TRIGGER trg_credit_tx_before_insert
        BEFORE INSERT ON credit_transactions
        FOR EACH ROW EXECUTE PROCEDURE credit_tx_before_insert()
    """)
    
    op.execute("""
        CREATE TRIGGER trg_credit_tx_before_update
        BEFORE UPDATE ON credit_transactions
        FOR EACH ROW EXECUTE PROCEDURE credit_tx_no_update_delete()
    """)
    
    op.execute("""
        CREATE TRIGGER trg_credit_tx_before_delete
        BEFORE DELETE ON credit_transactions
        FOR EACH ROW EXECUTE PROCEDURE credit_tx_no_update_delete()
    """)
    
    # Counter triggers
    op.execute("""
        CREATE TRIGGER trg_datasets_after_insert
        AFTER INSERT ON datasets
        FOR EACH ROW EXECUTE PROCEDURE users_inc_dataset_count()
    """)
    
    op.execute("""
        CREATE TRIGGER trg_datasets_after_delete
        AFTER DELETE ON datasets
        FOR EACH ROW EXECUTE PROCEDURE users_dec_dataset_count()
    """)
    
    op.execute("""
        CREATE TRIGGER trg_workflows_after_insert
        AFTER INSERT ON workflows
        FOR EACH ROW EXECUTE PROCEDURE users_inc_workflow_count()
    """)
    
    op.execute("""
        CREATE TRIGGER trg_workflows_after_delete
        AFTER DELETE ON workflows
        FOR EACH ROW EXECUTE PROCEDURE users_dec_workflow_count()
    """)
    
    op.execute("""
        CREATE TRIGGER trg_models_after_insert
        AFTER INSERT ON models
        FOR EACH ROW EXECUTE PROCEDURE users_inc_model_count()
    """)
    
    op.execute("""
        CREATE TRIGGER trg_models_after_delete
        AFTER DELETE ON models
        FOR EACH ROW EXECUTE PROCEDURE users_dec_model_count()
    """)
    
    # Storage tracking triggers
    op.execute("""
        CREATE TRIGGER trg_datasets_after_insert_storage
        AFTER INSERT ON datasets
        FOR EACH ROW EXECUTE PROCEDURE users_adjust_storage_on_dataset_ins()
    """)
    
    op.execute("""
        CREATE TRIGGER trg_datasets_after_delete_storage
        AFTER DELETE ON datasets
        FOR EACH ROW EXECUTE PROCEDURE users_adjust_storage_on_dataset_del()
    """)
    
    op.execute("""
        CREATE TRIGGER trg_datasets_after_update_storage
        AFTER UPDATE OF parquet_size_bytes, original_size_bytes ON datasets
        FOR EACH ROW EXECUTE PROCEDURE users_adjust_storage_on_dataset_upd()
    """)


def downgrade() -> None:
    # ============================================================
    # DROP TRIGGERS (reverse order)
    # ============================================================
    op.execute('DROP TRIGGER IF EXISTS trg_datasets_after_update_storage ON datasets')
    op.execute('DROP TRIGGER IF EXISTS trg_datasets_after_delete_storage ON datasets')
    op.execute('DROP TRIGGER IF EXISTS trg_datasets_after_insert_storage ON datasets')
    
    op.execute('DROP TRIGGER IF EXISTS trg_models_after_delete ON models')
    op.execute('DROP TRIGGER IF EXISTS trg_models_after_insert ON models')
    op.execute('DROP TRIGGER IF EXISTS trg_workflows_after_delete ON workflows')
    op.execute('DROP TRIGGER IF EXISTS trg_workflows_after_insert ON workflows')
    op.execute('DROP TRIGGER IF EXISTS trg_datasets_after_delete ON datasets')
    op.execute('DROP TRIGGER IF EXISTS trg_datasets_after_insert ON datasets')
    
    op.execute('DROP TRIGGER IF EXISTS trg_credit_tx_before_delete ON credit_transactions')
    op.execute('DROP TRIGGER IF EXISTS trg_credit_tx_before_update ON credit_transactions')
    op.execute('DROP TRIGGER IF EXISTS trg_credit_tx_before_insert ON credit_transactions')
    
    op.execute('DROP TRIGGER IF EXISTS trg_tutorials_updated_at ON tutorials')
    op.execute('DROP TRIGGER IF EXISTS trg_experiments_updated_at ON experiments')
    op.execute('DROP TRIGGER IF EXISTS trg_datasets_updated_at ON datasets')
    op.execute('DROP TRIGGER IF EXISTS trg_users_updated_at ON users')
    
    # ============================================================
    # DROP FUNCTIONS
    # ============================================================
    op.execute('DROP FUNCTION IF EXISTS users_adjust_storage_on_dataset_upd()')
    op.execute('DROP FUNCTION IF EXISTS users_adjust_storage_on_dataset_del()')
    op.execute('DROP FUNCTION IF EXISTS users_adjust_storage_on_dataset_ins()')
    op.execute('DROP FUNCTION IF EXISTS users_dec_model_count()')
    op.execute('DROP FUNCTION IF EXISTS users_inc_model_count()')
    op.execute('DROP FUNCTION IF EXISTS users_dec_workflow_count()')
    op.execute('DROP FUNCTION IF EXISTS users_inc_workflow_count()')
    op.execute('DROP FUNCTION IF EXISTS users_dec_dataset_count()')
    op.execute('DROP FUNCTION IF EXISTS users_inc_dataset_count()')
    op.execute('DROP FUNCTION IF EXISTS credit_tx_no_update_delete()')
    op.execute('DROP FUNCTION IF EXISTS credit_tx_before_insert()')
    op.execute('DROP FUNCTION IF EXISTS set_updated_at()')
    
    # ============================================================
    # DROP INDEX
    # ============================================================
    op.execute('DROP INDEX IF EXISTS ux_users_email_ci')
    
    # ============================================================
    # DROP EXTENSION (optional - may affect other databases)
    # ============================================================
    # NOTE: We don't drop the extension in downgrade because:
    # 1. It might be used by other apps on same database
    # 2. Tables still have UUID columns that depend on it
    # If you really need to drop it, uncomment:
    # op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')
