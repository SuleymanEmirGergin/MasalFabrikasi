"""
Quick API Test Script
Run: python test_quick.py
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(name, method, endpoint, **kwargs):
    """Test a single endpoint"""
    print(f"\n{'='*50}")
    print(f"Testing: {name}")
    print(f"{'='*50}")
    
    url = f"{BASE_URL}{endpoint}"
    start = time.time()
    
    try:
        if method == "GET":
            response = requests.get(url, **kwargs)
        elif method == "POST":
            response = requests.post(url, **kwargs)
        
        duration = (time.time() - start) * 1000  # Convert to ms
        
        print(f"✅ Status: {response.status_code}")
        print(f"⏱️  Duration: {duration:.2f}ms")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📦 Response: {json.dumps(data, indent=2, ensure_ascii=False)[:200]}...")
        else:
            print(f"❌ Error: {response.text}")
        
        return response.status_code == 200
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("""
    ╔═══════════════════════════════════════╗
    ║   Masal Fabrikası API Test Suite    ║
    ╚═══════════════════════════════════════╝
    """)
    
    results = []
    
    # 1. Root endpoint
    results.append(test_endpoint(
        "Root Endpoint",
        "GET",
        "/"
    ))
    
    # 2. Health check
    results.append(test_endpoint(
        "Health Check",
        "GET",
        "/health"
    ))
    
    # 3. API Documentation
    results.append(test_endpoint(
        "API Docs",
        "GET",
        "/docs"
    ))
    
    # 4. Story Generation (Async)
    results.append(test_endpoint(
        "Story Generation (Async)",
        "POST",
        "/api/story/generate-story",
        json={
            "theme": "Test hikayesi",
            "language": "tr",
            "story_type": "masal",
            "use_async": True
        }
    ))
    
    # 5. Get Stories
    results.append(test_endpoint(
        "Get Stories",
        "GET",
        "/api/story/stories?limit=5"
    ))
    
    # 6. Get Characters
    results.append(test_endpoint(
        "Get Characters",
        "GET",
        "/api/character/characters"
    ))
    
    # Summary
    print(f"\n\n{'='*50}")
    print(f"📊 TEST SUMMARY")
    print(f"{'='*50}")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")

if __name__ == "__main__":
    main()
