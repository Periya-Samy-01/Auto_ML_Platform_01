"""Check workflow data from Redis to see config structure"""
import sys
import os
from pathlib import Path

# Add packages to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "packages"))

import json
from app.services.cache import cache_service

# List all workflow keys
keys = cache_service.redis_client.keys("workflow:*")
print(f"Found {len(keys)} workflow keys in Redis")

# Get the most recent one
if keys:
    for key in keys[:3]:  # Check up to 3
        print(f"\n{'='*50}")
        print(f"Key: {key}")
        print(f"{'='*50}")
        key_str = key.decode() if isinstance(key, bytes) else key
        data = cache_service.get(key_str)
        if data:
            workflow = json.loads(data)
            # Find dataset node
            for node in workflow.get("nodes", []):
                if node.get("type") == "dataset":
                    print(f"\nDataset Node Config:")
                    config = node.get("config", {})
                    for k, v in config.items():
                        print(f"  {k}: {v}")
else:
    print("No workflow keys found in Redis")
