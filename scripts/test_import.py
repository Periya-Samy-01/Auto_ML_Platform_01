import sys
import os

# Setup path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

print("Attempting to import User model...")
try:
    from packages.database.models import User
    print("Successfully imported User model!")
    print(f"User table: {User.__tablename__}")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Other Error: {e}")
