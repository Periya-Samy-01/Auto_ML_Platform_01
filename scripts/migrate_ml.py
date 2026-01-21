
import shutil
import os
import sys

def migrate():
    # Paths
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    worker_ml_dir = os.path.join(project_root, "apps", "workers", "worker", "ml")
    api_ml_dir = os.path.join(project_root, "apps", "api", "app", "ml")
    
    worker_dir = os.path.join(project_root, "apps", "workers", "worker")
    
    # Files to move
    files_to_move = [
        ("constants.py", "constants.py"),
        ("utils.py", "worker_utils.py"),
        ("errors.py", "errors.py"),
        ("logging_config.py", "logging_config.py"),
    ]
    
    with open("migration.log", "w") as log:
        log.write(f"Migrating from {worker_ml_dir} to {api_ml_dir}\n")
        
        # 1. Create destination
        if not os.path.exists(api_ml_dir):
            log.write(f"Creating {api_ml_dir}\n")
            try:
                shutil.copytree(worker_ml_dir, api_ml_dir)
                log.write("Copied ml directory.\n")
            except FileExistsError:
                 log.write("Directory already exists (race condition?), skipping copytree\n")
        else:
            log.write("Target directory exists. Skipping copytree.\n")
            
        # 2. Copy individual files
        for src_name, dest_name in files_to_move:
            src_path = os.path.join(worker_dir, src_name)
            dest_path = os.path.join(api_ml_dir, dest_name)
            
            if os.path.exists(src_path):
                log.write(f"Copying {src_name} -> {dest_name}\n")
                shutil.copy2(src_path, dest_path)
            else:
                log.write(f"Warning: Source {src_name} not found!\n")

        log.write("Migration file operations complete.\n")

if __name__ == "__main__":
    migrate()
