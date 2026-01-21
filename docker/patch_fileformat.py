"""
Script to fix FileFormat enum values to use lowercase to match database
"""

file_path = r"c:\Folders\AutoML Platform 2.0\packages\database\models\enums.py"

with open(file_path, 'r') as f:
    content = f.read()

# Look for common patterns and fix them
# The enum likely has uppercase values like CSV = "CSV" that need to be csv = "csv"

# Fix FileFormat enum values to lowercase
# Pattern: CSV = "CSV" -> CSV = "csv"
replacements = [
    ('CSV = "CSV"', 'CSV = "csv"'),
    ('JSON = "JSON"', 'JSON = "json"'),
    ('PARQUET = "PARQUET"', 'PARQUET = "parquet"'),
    ('EXCEL = "EXCEL"', 'EXCEL = "excel"'),
    ('UNKNOWN = "UNKNOWN"', 'UNKNOWN = "unknown"'),
    # Also try with auto() pattern
    ("CSV = auto()", 'CSV = "csv"'),
    ("JSON = auto()", 'JSON = "json"'),
    ("PARQUET = auto()", 'PARQUET = "parquet"'),
    ("EXCEL = auto()", 'EXCEL = "excel"'),
    ("UNKNOWN = auto()", 'UNKNOWN = "unknown"'),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f"Replaced: {old} -> {new}")

with open(file_path, 'w') as f:
    f.write(content)

print("\nFileFormat enum values updated to lowercase!")
