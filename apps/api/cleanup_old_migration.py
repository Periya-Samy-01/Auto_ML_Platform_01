"""
Clean up duplicate enum types from old migration
Run this before applying the new migration
"""

import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings

print("=" * 70)
print("CLEANING UP OLD MIGRATION ARTIFACTS")
print("=" * 70)

# Connect to database
print("\n1. Connecting to database...")
try:
    engine = create_engine(settings.DATABASE_URL)
    print("   ✅ Connected!")
except Exception as e:
    print(f"   ❌ Connection failed: {e}")
    sys.exit(1)

# Drop old enum types
print("\n2. Dropping old enum types...")
cleanup_sql = """
-- Drop old enum types that conflict
DROP TYPE IF EXISTS file_format CASCADE;
DROP TYPE IF EXISTS ingestion_status CASCADE;
"""

try:
    with engine.connect() as conn:
        conn.execute(text(cleanup_sql))
        conn.commit()
    print("   ✅ Old enum types dropped!")
except Exception as e:
    print(f"   ❌ Failed to drop enums: {e}")
    sys.exit(1)

# Check remaining enum types
print("\n3. Checking remaining enum types...")
try:
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT typname FROM pg_type WHERE typtype = 'e' ORDER BY typname"
        ))
        enums = [row[0] for row in result]
        
    if enums:
        print("   Remaining enums:")
        for enum in enums:
            print(f"      - {enum}")
    else:
        print("   (No enum types in database)")
        
except Exception as e:
    print(f"   ⚠️  Could not check enums: {e}")

print("\n" + "=" * 70)
print("CLEANUP COMPLETE!")
print("=" * 70)
print("\n✅ Database is ready for new migration!")
print("\nNext step:")
print("  alembic upgrade head")
