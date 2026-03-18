# Cloudinary Test Guide

## Automated Tests

### 1. Run Test Script

```bash
cd backend
python tests/test_cloudinary.py
```

**Expected Output:**
```
🧪 CLOUDINARY INTEGRATION TEST SUITE
==================================================
🔍 Test 1: Cloudinary Configuration
--------------------------------------------------
✅ Cloudinary is ENABLED and configured
   Cloud Name: your-cloud-name
   API Key: 1234567890...

🔍 Test 2: Image Upload
--------------------------------------------------
   Created test image: test_image_xxx.png
✅ Image uploaded successfully!
   URL: https://res.cloudinary.com/...
   ✅ Local file auto-deleted

🔍 Test 3: Audio Upload
--------------------------------------------------
   Created test audio: test_audio_xxx.mp3
✅ Audio uploaded successfully!
   URL: https://res.cloudinary.com/...
   ✅ Local file auto-deleted

🔍 Test 4: Fallback Mechanism
--------------------------------------------------
✅ Fallback works (returns local path when disabled)

==================================================
📊 TEST RESULTS
==================================================
Configuration       : ✅ PASS
Image Upload        : ✅ PASS
Audio Upload        : ✅ PASS
Fallback            : ✅ PASS

==================================================
🎉 ALL TESTS PASSED!
==================================================
```

---

## Manual Tests

### Test 1: Story Generation (E2E Test)

1. **Start Backend:**
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. **Generate Story via API:**
   ```bash
   curl -X POST http://localhost:8000/api/stories/generate-story \
     -H "Content-Type: application/json" \
     -d '{
       "theme": "space adventure",
       "language": "en",
       "story_type": "masal",
       "save": true
     }'
   ```

3. **Check Response:**
   ```json
   {
     "story_id": "...",
     "image_url": "https://res.cloudinary.com/...",  // Should be Cloudinary URL
     "audio_url": "https://res.cloudinary.com/...",  // Should be Cloudinary URL
     ...
   }
   ```

4. **Verify:**
   - ✅ `image_url` starts with `https://res.cloudinary.com/`
   - ✅ `audio_url` starts with `https://res.cloudinary.com/`
   - ✅ URLs are accessible (click them in browser)
   - ✅ Local `data/images/` folder does NOT have new files (auto-deleted)

### Test 2: Cloudinary Dashboard

1. Login to Cloudinary: https://console.cloudinary.com/
2. Go to **Media Library**
3. Check folders:
   - `/stories/` - Should have new images
   - `/audio/` - Should have new audio files
4. Click on a file to preview
5. Check file size (should be optimized)

### Test 3: Fallback Test (Without Cloudinary)

1. **Disable Cloudinary:**
   ```bash
   # In backend/.env, comment out:
   # CLOUDINARY_CLOUD_NAME=...
   # CLOUDINARY_API_KEY=...
   # CLOUDINARY_API_SECRET=...
   ```

2. **Restart Backend**

3. **Generate Story Again**

4. **Check Response:**
   ```json
   {
     "image_url": "/storage/images/...",  // Should be local path
     "audio_url": "/storage/audio/...",   // Should be local path
   }
   ```

5. **Verify:**
   - ✅ Local files ARE created in `data/images/` and `data/audio/`
   - ✅ No errors (graceful fallback)

6. **Re-enable Cloudinary** (uncomment .env variables)

---

## Troubleshooting

### ❌ "Cloudinary is NOT configured"

**Solution:**
1. Check `backend/.env` file exists
2. Verify credentials:
   ```env
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=123456789012345
   CLOUDINARY_API_SECRET=abcdefghijklmnop
   ```
3. Restart backend

### ❌ "Upload failed: Authentication error"

**Solution:**
- Credentials are wrong
- Copy-paste again from Cloudinary Dashboard
- Ensure no extra spaces

### ❌ "Upload failed: Invalid image"

**Solution:**
- OpenAI might have returned invalid image
- Check OpenAI API quota
- Try with different theme

### ❌ Local files not deleted

**Solution:**
- This is expected if Cloudinary upload fails
- Check Cloudinary dashboard for errors
- Manually delete test files

---

## Success Criteria

All of these should be ✅:

- [x] Test script passes all 4 tests
- [x] Story generation returns Cloudinary URLs
- [x] Images visible in Cloudinary dashboard
- [x] Audio files visible in Cloudinary dashboard
- [x] Local files auto-deleted after upload
- [x] URLs are publicly accessible
- [x] Fallback to local storage works when disabled

---

## Performance Check

### Before Cloudinary
- Image size: ~200-500 KB (PNG)
- Audio size: ~100-300 KB (MP3)
- **Storage:** Local disk
- **Delivery:** Backend server
- **Speed:** Depends on server bandwidth

### After Cloudinary
- Image size: ~50-150 KB (WebP auto-conversion)
- Audio size: Same (~100-300 KB)
- **Storage:** Cloudinary cloud
- **Delivery:** CDN (fast worldwide)
- **Speed:** 2-3x faster load times

---

## Next Steps After Tests Pass

1. ✅ Verify all tests pass
2. Update frontend to handle Cloudinary URLs
3. Test on mobile app
4. Monitor Cloudinary usage dashboard
5. Proceed to Phase 2 (PostgreSQL)

---

**Ready to test? Run:**
```bash
cd backend
python tests/test_cloudinary.py
```
