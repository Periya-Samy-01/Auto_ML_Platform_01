"""
Script to fix DatasetVersion model Enum definition to use values_callable
"""

file_path = r"c:\Folders\AutoML Platform 2.0\packages\database\models\dataset_version.py"

with open(file_path, 'r') as f:
    content = f.read()

# The issue is Enum(FileFormat) uses the enum name by default
# Fix: add native_enum=True and values_callable
# But actually for PostgreSQL with native enum, we need to pass the value

# Actually the simplest fix is to use the enum value directly
# Replace Enum(FileFormat) with Enum(FileFormat, native_enum=True, create_type=False)

old = "Enum(FileFormat),"
new = 'Enum(FileFormat, native_enum=True, create_type=False, values_callable=lambda x: [e.value for e in x]),'

if old in content:
    content = content.replace(old, new)
    print(f"Fixed FileFormat enum column")

# Also fix ProcessingStatus
old2 = "Enum(ProcessingStatus),"
new2 = 'Enum(ProcessingStatus, native_enum=True, create_type=False, values_callable=lambda x: [e.value for e in x]),'

if old2 in content:
    content = content.replace(old2, new2)
    print(f"Fixed ProcessingStatus enum column")

with open(file_path, 'w') as f:
    f.write(content)

print("\nDatasetVersion model enum columns fixed!")
