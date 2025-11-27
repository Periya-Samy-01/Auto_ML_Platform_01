#!/usr/bin/env python3
"""
Database Verification Script for AutoML Platform
Checks if all migrations are applied correctly to Neon PostgreSQL
"""

import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import Session
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from typing import List, Tuple

console = Console()

# Expected schema elements
EXPECTED_TABLES = [
    'users', 'datasets', 'workflows', 'workflow_snapshots',
    'jobs', 'job_nodes', 'models', 'credit_transactions',
    'credit_packages', 'experiments', 'experiment_runs',
    'tutorials', 'user_tutorial_progress', 'alembic_version'
]

EXPECTED_ENUMS = [
    'user_tier', 'file_format', 'problem_type', 'job_status',
    'node_type', 'node_status', 'transaction_type',
    'tutorial_difficulty', 'credit_tier_restriction'
]

CRITICAL_INDEXES = [
    ('jobs', 'idx_jobs_queue', 'CRITICAL - Powers job scheduling'),
    ('users', 'ux_users_email_ci', 'Case-insensitive unique email'),
    ('jobs', 'idx_jobs_user_id', 'Job queries by user'),
    ('credit_transactions', 'idx_credit_tx_user_id', 'Credit history'),
]

CRITICAL_TRIGGERS = [
    ('users', 'trg_users_updated_at', 'Updated timestamp'),
    ('credit_transactions', 'trg_credit_tx_before_insert', 'CRITICAL - Credit balance'),
    ('credit_transactions', 'trg_credit_tx_before_update', 'CRITICAL - Immutability'),
    ('credit_transactions', 'trg_credit_tx_before_delete', 'CRITICAL - Immutability'),
    ('datasets', 'trg_datasets_after_insert', 'Dataset counter'),
    ('workflows', 'trg_workflows_after_insert', 'Workflow counter'),
    ('models', 'trg_models_after_insert', 'Model counter'),
]


def get_database_url() -> str:
    """Get database URL from environment or prompt"""
    import os
    
    # Try to load from .env in apps/api
    try:
        from pathlib import Path
        env_path = Path(__file__).parent / 'apps' / 'api' / '.env'
        if env_path.exists():
            from dotenv import load_dotenv
            load_dotenv(env_path)
    except Exception:
        pass
    
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        console.print("[yellow]DATABASE_URL not found in environment.[/yellow]")
        console.print("Please provide your Neon PostgreSQL connection string:")
        db_url = input("DATABASE_URL: ").strip()
    
    return db_url


def check_tables(engine) -> Tuple[bool, List[str]]:
    """Check if all expected tables exist"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    missing = [t for t in EXPECTED_TABLES if t not in existing_tables]
    return len(missing) == 0, missing


def check_enums(engine) -> Tuple[bool, List[str]]:
    """Check if all expected enum types exist"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT typname 
            FROM pg_type 
            WHERE typtype = 'e'
        """))
        existing_enums = [row[0] for row in result]
    
    missing = [e for e in EXPECTED_ENUMS if e not in existing_enums]
    return len(missing) == 0, missing


def check_indexes(engine) -> Tuple[bool, List[Tuple[str, str]]]:
    """Check if critical indexes exist"""
    missing = []
    
    with engine.connect() as conn:
        for table, index_name, description in CRITICAL_INDEXES:
            result = conn.execute(text("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = :table AND indexname = :index
            """), {"table": table, "index": index_name})
            
            if result.fetchone() is None:
                missing.append((table, index_name, description))
    
    return len(missing) == 0, missing


def check_triggers(engine) -> Tuple[bool, List[Tuple[str, str]]]:
    """Check if critical triggers exist"""
    missing = []
    
    with engine.connect() as conn:
        for table, trigger_name, description in CRITICAL_TRIGGERS:
            result = conn.execute(text("""
                SELECT tgname 
                FROM pg_trigger 
                JOIN pg_class ON pg_trigger.tgrelid = pg_class.oid
                WHERE pg_class.relname = :table AND tgname = :trigger
            """), {"table": table, "trigger": trigger_name})
            
            if result.fetchone() is None:
                missing.append((table, trigger_name, description))
    
    return len(missing) == 0, missing


def check_extensions(engine) -> Tuple[bool, List[str]]:
    """Check if required PostgreSQL extensions are installed"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT extname FROM pg_extension
        """))
        extensions = [row[0] for row in result]
    
    required = ['uuid-ossp']
    missing = [e for e in required if e not in extensions]
    return len(missing) == 0, missing


def test_basic_operations(engine) -> Tuple[bool, str]:
    """Test basic CRUD operations"""
    try:
        with Session(engine) as session:
            # Try to query users table (should be empty, that's fine)
            result = session.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            return True, f"Users table accessible ({count} records)"
    except Exception as e:
        return False, str(e)


def test_credit_triggers(engine) -> Tuple[bool, str]:
    """Test if credit transaction triggers work (READ-ONLY test)"""
    try:
        with engine.connect() as conn:
            # Just verify the trigger function exists
            result = conn.execute(text("""
                SELECT proname 
                FROM pg_proc 
                WHERE proname = 'credit_tx_before_insert'
            """))
            
            if result.fetchone():
                return True, "Credit trigger functions exist"
            else:
                return False, "Credit trigger functions missing"
    except Exception as e:
        return False, str(e)


def check_alembic_version(engine) -> Tuple[bool, str]:
    """Check current Alembic migration version"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            version = result.scalar()
            if version:
                return True, f"Migration version: {version}"
            else:
                return False, "No migration version found"
    except Exception as e:
        return False, f"Alembic version table issue: {str(e)}"


def main():
    console.print("\n[bold cyan]🔍 AutoML Platform - Database Verification[/bold cyan]\n")
    
    try:
        db_url = get_database_url()
        console.print(f"[dim]Connecting to: {db_url[:30]}...[/dim]\n")
        
        engine = create_engine(db_url, echo=False)
        
        # Run all checks
        results = []
        
        # 1. Tables
        console.print("[bold]1. Checking Tables...[/bold]")
        tables_ok, missing_tables = check_tables(engine)
        if tables_ok:
            results.append(("✅", "Tables", f"All {len(EXPECTED_TABLES)} tables exist"))
            console.print(f"   [green]✅ All {len(EXPECTED_TABLES)} tables exist[/green]")
        else:
            results.append(("❌", "Tables", f"Missing: {', '.join(missing_tables)}"))
            console.print(f"   [red]❌ Missing tables: {', '.join(missing_tables)}[/red]")
        
        # 2. Enums
        console.print("\n[bold]2. Checking Enum Types...[/bold]")
        enums_ok, missing_enums = check_enums(engine)
        if enums_ok:
            results.append(("✅", "Enums", f"All {len(EXPECTED_ENUMS)} enums exist"))
            console.print(f"   [green]✅ All {len(EXPECTED_ENUMS)} enum types exist[/green]")
        else:
            results.append(("❌", "Enums", f"Missing: {', '.join(missing_enums)}"))
            console.print(f"   [red]❌ Missing enums: {', '.join(missing_enums)}[/red]")
        
        # 3. Extensions
        console.print("\n[bold]3. Checking PostgreSQL Extensions...[/bold]")
        ext_ok, missing_ext = check_extensions(engine)
        if ext_ok:
            results.append(("✅", "Extensions", "uuid-ossp installed"))
            console.print("   [green]✅ Required extensions installed[/green]")
        else:
            results.append(("❌", "Extensions", f"Missing: {', '.join(missing_ext)}"))
            console.print(f"   [red]❌ Missing extensions: {', '.join(missing_ext)}[/red]")
        
        # 4. Critical Indexes
        console.print("\n[bold]4. Checking Critical Indexes...[/bold]")
        idx_ok, missing_idx = check_indexes(engine)
        if idx_ok:
            results.append(("✅", "Indexes", f"All {len(CRITICAL_INDEXES)} critical indexes exist"))
            console.print(f"   [green]✅ All critical indexes exist[/green]")
        else:
            results.append(("❌", "Indexes", f"{len(missing_idx)} missing"))
            console.print(f"   [red]❌ Missing indexes:[/red]")
            for table, idx, desc in missing_idx:
                console.print(f"      • {table}.{idx} - {desc}")
        
        # 5. Critical Triggers
        console.print("\n[bold]5. Checking Critical Triggers...[/bold]")
        trig_ok, missing_trig = check_triggers(engine)
        if trig_ok:
            results.append(("✅", "Triggers", f"All {len(CRITICAL_TRIGGERS)} critical triggers exist"))
            console.print(f"   [green]✅ All critical triggers exist[/green]")
        else:
            results.append(("❌", "Triggers", f"{len(missing_trig)} missing"))
            console.print(f"   [red]❌ Missing triggers:[/red]")
            for table, trig, desc in missing_trig:
                console.print(f"      • {table}.{trig} - {desc}")
        
        # 6. Alembic Version
        console.print("\n[bold]6. Checking Migration Status...[/bold]")
        alembic_ok, alembic_msg = check_alembic_version(engine)
        if alembic_ok:
            results.append(("✅", "Migrations", alembic_msg))
            console.print(f"   [green]✅ {alembic_msg}[/green]")
        else:
            results.append(("❌", "Migrations", alembic_msg))
            console.print(f"   [red]❌ {alembic_msg}[/red]")
        
        # 7. Basic Operations
        console.print("\n[bold]7. Testing Basic Operations...[/bold]")
        ops_ok, ops_msg = test_basic_operations(engine)
        if ops_ok:
            results.append(("✅", "Operations", ops_msg))
            console.print(f"   [green]✅ {ops_msg}[/green]")
        else:
            results.append(("❌", "Operations", ops_msg))
            console.print(f"   [red]❌ {ops_msg}[/red]")
        
        # 8. Credit Triggers
        console.print("\n[bold]8. Checking Credit System Triggers...[/bold]")
        credit_ok, credit_msg = test_credit_triggers(engine)
        if credit_ok:
            results.append(("✅", "Credit System", credit_msg))
            console.print(f"   [green]✅ {credit_msg}[/green]")
        else:
            results.append(("❌", "Credit System", credit_msg))
            console.print(f"   [red]❌ {credit_msg}[/red]")
        
        # Summary
        console.print("\n" + "="*60)
        console.print("\n[bold]📊 VERIFICATION SUMMARY[/bold]\n")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Status", style="dim", width=6)
        table.add_column("Component", width=15)
        table.add_column("Details", width=35)
        
        for status, component, details in results:
            table.add_row(status, component, details)
        
        console.print(table)
        
        # Final verdict
        all_ok = all(r[0] == "✅" for r in results)
        
        if all_ok:
            console.print("\n[bold green]🎉 ALL CHECKS PASSED![/bold green]")
            console.print("\n[green]Your database is ready. You can proceed to JWT Authentication (Days 19-20).[/green]\n")
            return 0
        else:
            console.print("\n[bold red]⚠️  ISSUES FOUND[/bold red]")
            console.print("\n[yellow]Action required:[/yellow]")
            console.print("1. Run: [cyan]cd apps/api && alembic upgrade head[/cyan]")
            console.print("2. Re-run this verification script")
            console.print("3. If issues persist, check migration files\n")
            return 1
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {str(e)}[/bold red]\n")
        import traceback
        console.print("[dim]" + traceback.format_exc() + "[/dim]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
