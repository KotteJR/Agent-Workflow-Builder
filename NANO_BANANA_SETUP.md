# Nano Banana Pro (Gemini 3 Pro Image) Setup

## Overview

Nano Banana Pro is Google's advanced AI image generation model built on Gemini 3 Pro architecture. It offers:
- **Up to 4K resolution** image generation
- **Advanced text rendering** with accurate, legible text in multiple languages
- **Real-world data integration** via Google Search
- **Studio-quality controls** (focus, lighting, camera angles, color grading)

## Configuration

### 1. Update `.env` file

Add or update these variables in `backend/.env`:

```bash
# Image Generation Provider
IMAGE_PROVIDER=nano-banana

# Google API Key (required for Nano Banana Pro)
GOOGLE_API_KEY=your-google-api-key-here

# Optional: Specify the exact Gemini model (defaults to gemini-3.0-pro)
GEMINI_IMAGE_MODEL=gemini-3.0-pro
```

### 2. Get Google API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API Key" or go to [API Keys page](https://aistudio.google.com/app/apikey)
4. Create a new API key
5. Copy the key to your `.env` file

### 3. Usage Limits

**Free Tier:**
- Limited to **2 image generations per day**
- Good for testing

**Paid Plans:**
- Google AI Pro Plan: Higher daily quotas
- Check [Google AI Studio pricing](https://ai.google.dev/pricing) for current rates

## How It Works

When `IMAGE_PROVIDER=nano-banana` is set:

1. The image generator uses Gemini 3 Pro Image model
2. Generates images at **2048x2048** resolution (vs 1024x1024 for standard Gemini)
3. Falls back to DALL-E if Google API key is missing or errors occur
4. Supports all image styles: diagram, photo, artistic, cartoon, illustration

## Comparison with Other Providers

| Provider | Cost per Image | Max Resolution | Text Rendering | Notes |
|----------|---------------|----------------|---------------|-------|
| **Nano Banana Pro** | Free (2/day) or paid | 4K (2048x2048+) | Excellent | Best for text in images |
| **DALL-E 3** | $0.04/image | 1024x1024 | Good | OpenAI, reliable |
| **Gemini 2.0** | Varies | 1024x1024 | Good | Older model |

## Testing

1. Set `IMAGE_PROVIDER=nano-banana` in `.env`
2. Add your `GOOGLE_API_KEY`
3. Restart the backend server
4. Run a workflow with an image generator node
5. Check logs to confirm it's using Nano Banana Pro

## Troubleshooting

**"GOOGLE_API_KEY not set"**
- Make sure the key is in your `.env` file
- Restart the server after adding the key

**"API error 429" (Rate Limit)**
- You've exceeded the free tier limit (2/day)
- Wait 24 hours or upgrade to a paid plan

**"No image in response"**
- The model might not have generated an image
- Check the prompt - make sure it's clear and descriptive
- System will automatically fallback to DALL-E if configured

**Model not found errors**
- Try updating `GEMINI_IMAGE_MODEL` to:
  - `gemini-3.0-pro`
  - `gemini-3-pro`
  - `gemini-pro-3.0`
- Check [Google AI Studio](https://aistudio.google.com/) for latest model names

## Benefits for Your Workflow

✅ **Better text rendering** - Perfect for diagrams with labels  
✅ **Higher resolution** - 4K images for professional use  
✅ **Real-world context** - Uses Google Search for accurate visuals  
✅ **Cost-effective** - Free tier for testing, competitive paid pricing  

## Switching Back

To use a different provider, just change `IMAGE_PROVIDER` in `.env`:
- `IMAGE_PROVIDER=dalle` - Use DALL-E 3
- `IMAGE_PROVIDER=gemini` - Use standard Gemini
- `IMAGE_PROVIDER=nano-banana` - Use Nano Banana Pro (default)

