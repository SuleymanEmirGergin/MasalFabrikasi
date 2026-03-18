# Hybrid AI Model Configuration Guide

## 🎯 Overview

Masal Fabrikası uses a **Hybrid AI** approach for cost optimization:

- **Wiro AI**: Story generation (cheap, Turkish-optimized)
- **OpenAI**: Image generation (DALL-E) and embeddings (semantic search)

---

## 📝 Configuration

### Required Environment Variables

```env
# Wiro AI - For story generation
OPENAI_API_KEY=wiro-api-key
OPENAI_BASE_URL=https://api.wiro.ai/v1

# OpenAI - For DALL-E and embeddings
DALLE_API_KEY=sk-openai-key
DALLE_BASE_URL=https://api.openai.com/v1
```

### Optional: Single Key Mode

If you want to use the same key for everything:

```env
OPENAI_API_KEY=your-key
OPENAI_BASE_URL=https://api.openai.com/v1
# Leave DALLE_API_KEY empty - will use OPENAI_API_KEY
```

---

## 💰 Cost Breakdown

### With Hybrid Model

| Feature | Provider | Cost (est.) |
|---------|----------|-------------|
| Story Generation | Wiro AI | ₺0.5-1 per story |
| Image Generation | OpenAI DALL-E | $0.02-0.04 per image |
| Embeddings | OpenAI | $0.0001 per 1K tokens |

**Monthly**: ~₺500-1000 for moderate usage

### Full OpenAI (comparison)

**Monthly**: $50-200+ (₺1,500-6,000)

---

## 🔧 How It Works

### Story Generation
```python
# Uses: OPENAI_API_KEY + OPENAI_BASE_URL (Wiro AI)
story = story_service.generate_story(theme="space cat")
```

### Image Generation
```python
# Uses: DALLE_API_KEY + DALLE_BASE_URL (OpenAI)
image = image_service.generate_image(prompt="cute cat in space")
```

### Semantic Search
```python
# Uses: DALLE_API_KEY + DALLE_BASE_URL (OpenAI embeddings)
results = search_service.search_stories(query="adventure")
```

---

## ⚙️ Fallback Behavior

If `DALLE_API_KEY` is not set:
- Falls back to `OPENAI_API_KEY`
- Uses `OPENAI_BASE_URL`

**Warning**: If using Wiro for `OPENAI_API_KEY`, DALL-E won't work without `DALLE_API_KEY`!

---

## 🚀 Getting Started

1. **Get API Keys**:
   - Wiro AI: https://wiro.ai
   - OpenAI: https://platform.openai.com

2. **Configure `.env`**:
   ```bash
   cp .env.example .env
   # Edit .env with your keys
   ```

3. **Verify**:
   ```bash
   python -c "from app.core.config import settings; print('Wiro:', settings.OPENAI_BASE_URL); print('DALL-E:', settings.DALLE_BASE_URL)"
   ```

4. **Start**:
   ```bash
   docker-compose up -d
   ```

---

## 📊 Features by Provider

### Wiro AI (OPENAI_API_KEY)
- ✅ Story generation
- ✅ Bedtime stories
- ✅ Character chat
- ✅ Story analysis
- ❌ Image generation (no DALL-E)
- ❌ Embeddings (might not have)

### OpenAI (DALLE_API_KEY)
- ✅ DALL-E image generation
- ✅ Text embeddings (semantic search)
- ✅ Can also do stories (but expensive)

---

## 🔄 Switching Modes

### Full Wiro (no images)
```env
OPENAI_API_KEY=wiro-key
OPENAI_BASE_URL=https://api.wiro.ai/v1
# No DALLE_API_KEY
```

### Full OpenAI (expensive)
```env
OPENAI_API_KEY=sk-openai-key
OPENAI_BASE_URL=https://api.openai.com/v1
# No DALLE_API_KEY needed
```

### Hybrid (Recommended)
```env
OPENAI_API_KEY=wiro-key
OPENAI_BASE_URL=https://api.wiro.ai/v1
DALLE_API_KEY=sk-openai-key
DALLE_BASE_URL=https://api.openai.com/v1
```

---

*Last Updated: 2026-01-02*
