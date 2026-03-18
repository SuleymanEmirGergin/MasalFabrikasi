
import sys
import os

# Add the current directory to sys.path to make imports work
sys.path.append(os.getcwd())

from main import app

def check_routers():
    print("Checking registered routers...")
    
    expected_tags = {
        "Analytics", "Social", "Media", "AI Tools", 
        "Story Features", "Story Advanced Analysis", 
        "User Features", "Platform", "Quiz", "Story", 
        "Character", "User", "Health"
    }
    
    found_tags = set()
    
    route_counts = {}

    for route in app.routes:
        if hasattr(route, "tags"):
            for tag in route.tags:
                found_tags.add(tag)
                route_counts[tag] = route_counts.get(tag, 0) + 1
    
    print("\nFound Router Tags:")
    print("-" * 30)
    for tag in sorted(found_tags):
        print(f"[{tag}]: {route_counts[tag]} endpoints")
    
    print("-" * 30)
    
    missing = expected_tags - found_tags
    if missing:
        print(f"\n❌ MISSING ROUTERS: {missing}")
        sys.exit(1)
    else:
        print("\n✅ ALL EXPECTED ROUTERS FOUND")
        print("Backend structure is healthy!")

if __name__ == "__main__":
    check_routers()
