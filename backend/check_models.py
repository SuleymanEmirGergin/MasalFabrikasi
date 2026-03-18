import sys
import os
import traceback

# Set up path
sys.path.append(os.getcwd())

from app.core.database import Base
print(f"Base ID: {id(Base)}")

def print_table_info(msg):
    print(f"\n--- {msg} ---")
    print(f"Tables in metadata: {list(Base.metadata.tables.keys())}")
    if 'user_profiles' in Base.metadata.tables:
        table = Base.metadata.tables['user_profiles']
        print(f"Table 'user_profiles' found!")
        # Try to find which class is mapped to it
        # In SQLAlchemy 2.0, we can check registries
        pass

print_table_info("Before Import")

try:
    print("\nImporting app.models...")
    import app.models
    print("app.models imported successfully")
except Exception as e:
    print(f"\nERROR DURING IMPORT: {type(e).__name__}: {e}")
    traceback.print_exc()

print_table_info("After Import")
