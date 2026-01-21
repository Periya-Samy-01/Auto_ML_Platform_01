import re

file_path = r"c:\Folders\AutoML Platform 2.0\packages\database\models\dataset.py"

with open(file_path, 'r') as f:
    content = f.read()

# Add is_sample_dataset before the ML configuration comment
new_field = '''    # Sample dataset flag
    is_sample_dataset: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # ML configuration (user-defined at dataset level)'''

content = content.replace('    # ML configuration (user-defined at dataset level)', new_field)

with open(file_path, 'w') as f:
    f.write(content)

print("Successfully added is_sample_dataset to Dataset model!")
