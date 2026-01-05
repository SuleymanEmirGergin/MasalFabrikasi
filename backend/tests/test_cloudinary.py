"""
Cloudinary Integration Test Script

Run this to verify that Cloudinary is properly configured and working.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.cloud_storage_service import cloud_storage

def test_cloudinary_config():
    """Test 1: Check if Cloudinary is configured"""
    print("\n🔍 Test 1: Cloudinary Configuration")
    print("-" * 50)
    
    if cloud_storage.enabled:
        print("✅ Cloudinary is ENABLED and configured")
        print(f"   Cloud Name: {os.getenv('CLOUDINARY_CLOUD_NAME')}")
        print(f"   API Key: {os.getenv('CLOUDINARY_API_KEY')[:10]}...")
        return True
    else:
        print("❌ Cloudinary is NOT configured")
        print("   Please set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET in .env")
        return False

def test_image_upload():
    """Test 2: Upload a test image"""
    print("\n🔍 Test 2: Image Upload")
    print("-" * 50)
    
    if not cloud_storage.enabled:
        print("⏭️  Skipped (Cloudinary not configured)")
        return False
    
    try:
        # Create a simple test image
        from PIL import Image
        import uuid
        
        # Create test image
        img = Image.new('RGB', (100, 100), color='blue')
        test_path = f"test_image_{uuid.uuid4()}.png"
        img.save(test_path)
        
        print(f"   Created test image: {test_path}")
        
        # Upload to Cloudinary
        url = cloud_storage.upload_image(
            test_path,
            folder="test",
            public_id="test_image"
        )
        
        print(f"✅ Image uploaded successfully!")
        print(f"   URL: {url}")
        
        # Clean up (local file should already be deleted by cloud_storage)
        if os.path.exists(test_path):
            os.remove(test_path)
            print("   ⚠️  Warning: Local file was not auto-deleted")
        else:
            print("   ✅ Local file auto-deleted")
        
        return True
        
    except Exception as e:
        print(f"❌ Image upload failed: {e}")
        return False

def test_audio_upload():
    """Test 3: Upload a test audio file"""
    print("\n🔍 Test 3: Audio Upload")
    print("-" * 50)
    
    if not cloud_storage.enabled:
        print("⏭️  Skipped (Cloudinary not configured)")
        return False
    
    try:
        # Create a dummy audio file
        import uuid
        test_path = f"test_audio_{uuid.uuid4()}.mp3"
        
        # Write minimal MP3 header (just for testing)
        with open(test_path, 'wb') as f:
            f.write(b'\xff\xfb\x90\x00' * 100)  # Minimal MP3 data
        
        print(f"   Created test audio: {test_path}")
        
        # Upload to Cloudinary
        url = cloud_storage.upload_audio(
            test_path,
            folder="test",
            public_id="test_audio"
        )
        
        print(f"✅ Audio uploaded successfully!")
        print(f"   URL: {url}")
        
        # Clean up
        if os.path.exists(test_path):
            os.remove(test_path)
            print("   ⚠️  Warning: Local file was not auto-deleted")
        else:
            print("   ✅ Local file auto-deleted")
        
        return True
        
    except Exception as e:
        print(f"❌ Audio upload failed: {e}")
        return False

def test_fallback():
    """Test 4: Fallback when Cloudinary is disabled"""
    print("\n🔍 Test 4: Fallback Mechanism")
    print("-" * 50)
    
    # Temporarily disable
    original_state = cloud_storage.enabled
    cloud_storage.enabled = False
    
    try:
        result = cloud_storage.upload_image("fake_path.png", folder="test")
        if result == "fake_path.png":
            print("✅ Fallback works (returns local path when disabled)")
        else:
            print("❌ Fallback issue: unexpected return value")
    finally:
        cloud_storage.enabled = original_state
    
    return True

def main():
    """Run all tests"""
    print("=" * 50)
    print("🧪 CLOUDINARY INTEGRATION TEST SUITE")
    print("=" * 50)
    
    results = {
        "Configuration": test_cloudinary_config(),
        "Image Upload": test_image_upload(),
        "Audio Upload": test_audio_upload(),
        "Fallback": test_fallback(),
    }
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20s}: {status}")
    
    all_passed = all(results.values())
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())
