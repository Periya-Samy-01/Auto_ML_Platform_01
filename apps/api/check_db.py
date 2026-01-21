"""Quick script to check database records for Jobs and Models"""
from app.core.database import SessionLocal
from database.models import Job, Model

db = SessionLocal()

print("=" * 50)
print("LATEST MODEL (Debug)")
print("=" * 50)

model = db.query(Model).order_by(Model.created_at.desc()).first()
if model:
    print(f"ID: {model.id}")
    print(f"Name: {model.name}")
    print(f"Model Type: {model.model_type}")
    print(f"Dataset ID: {model.dataset_id}")
    print(f"Version (stored dataset name): {model.version}")
    print(f"Created: {model.created_at}")
else:
    print("No models found")

db.close()
