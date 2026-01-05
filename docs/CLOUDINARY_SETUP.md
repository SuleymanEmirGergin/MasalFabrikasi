# Cloudinary Setup Guide

## Step 1: Create Cloudinary Account

1. Go to https://cloudinary.com/users/register/free
2. Sign up for free account
3. Email verification

## Step 2: Get Credentials

1. Login to dashboard: https://console.cloudinary.com/
2. Navigate to Dashboard (default page)
3. Find "Account Details" section
4. Copy these values:
   - **Cloud Name**
   - **API Key**
   - **API Secret**

## Step 3: Configure Backend

1. Open `backend/.env` (or create from `.env.example`)
2. Add credentials:

```env
CLOUDINARY_CLOUD_NAME=your-cloud-name-here
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=your-secret-here
```

3. Save and restart backend

## Step 4: Test Upload

```bash
# Install dependencies
cd backend
pip install cloudinary

# Test with Python
python
>>> from app.services.cloud_storage_service import cloud_storage
>>> cloud_storage.enabled
True  # Should return True if configured
```

## Free Tier Limits

Cloudinary Free Plan includes:
- ✅ 25 GB storage
- ✅ 25 GB bandwidth/month
- ✅ 25,000 transformations/month
- ✅ Unlimited images
- ✅ Video support (up to 500 MB)

**Enough for ~5,000-10,000 users!**

## Folder Structure

Your files will be organized as:
```
/stories/          - Story images
/audio/            - Story audio files
/avatars/          - User avatars
/characters/       - Character images
```

## Optimization Features

Cloudinary automatically:
- Converts to WebP/AVIF (smaller files)
- Auto quality adjustment
- Responsive images
- CDN delivery (fast worldwide)
- Lazy loading support

## Migration from Local Storage

The service automatically:
1. Uploads new files to Cloudinary
2. Returns Cloudinary URL
3. Deletes local file after upload
4. Falls back to local if Cloudinary fails

**Existing local files:** Will remain local until regenerated

## Monitoring Usage

1. Dashboard: https://console.cloudinary.com/
2. Check "Analytics" tab
3. Monitor:
   - Storage usage
   - Bandwidth
   - Transformations count

## Upgrade Path

When you exceed free tier:

**Cloudinary Plus:** $89/month
- 100 GB storage
- 150 GB bandwidth
- 250,000 transformations

**Alternative: AWS S3**
- Cheaper storage ($0.023/GB)
- Need CloudFront for CDN
- More complex setup

## Security

- ✅ Credentials in `.env` (gitignored)
- ✅ Secure HTTPS delivery
- ✅ Signed URLs (optional)
- ✅ Upload presets (optional)

## Next Steps

After setup:
1. Test image upload
2. Test audio upload
3. Verify URLs work in app
4. Monitor usage dashboard

---

**You're all set! Cloud storage is ready.** ☁️
