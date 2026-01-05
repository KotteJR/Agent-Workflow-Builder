"""
Image Generator Agent - Generates images from text descriptions.

Uses DALL-E or Gemini to generate images based on prompts,
with support for different image types and styles.
"""

from typing import Any, Dict, List, Optional

import httpx

from agents.base import BaseAgent, AgentResult
from models import LLMClientProtocol
from config import config


class ImageGeneratorAgent(BaseAgent):
    """
    Image Generator Agent that creates images from text.
    
    Capabilities:
    - Generates images from text descriptions
    - Supports different image types (diagram, photo, artistic, etc.)
    - Uses DALL-E or Gemini as provider
    - Enhances prompts for better results
    """
    
    agent_id = "image_generator"
    display_name = "Image Generator"
    default_model = "dalle"  # Uses image generation model
    
    IMAGE_STYLES = {
        "diagram": "clean technical diagram, flowchart style, labeled components, white background, professional",
        "photo": "photorealistic, highly detailed, professional photography",
        "artistic": "digital art, artistic style, vibrant colors",
        "cartoon": "cartoon illustration style, colorful, friendly",
        "illustration": "professional illustration, detailed, clean lines",
    }

    async def execute(
        self,
        user_message: str,
        context: Dict[str, Any],
        settings: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
    ) -> AgentResult:
        """
        Generate an image based on the prompt.
        
        Args:
            user_message: User's query (used as base prompt)
            context: Contains 'orchestrator_result' with image_prompt if available
            settings: Contains 'imageType'
            model: Not used (uses IMAGE_PROVIDER from config)
            
        Returns:
            AgentResult with generated image
        """
        settings = settings or {}
        image_type = settings.get("imageType", "photo")
        
        # Get prompt from orchestrator if available, otherwise use user message
        orchestrator_result = context.get("orchestrator_result", {})
        prompt = orchestrator_result.get("image_prompt", user_message)
        style = orchestrator_result.get("image_type", image_type)
        
        # Generate image
        result = await self._generate_image(prompt, style)
        
        if result.get("success"):
            content = f"Generated image: {result.get('revised_prompt', prompt)}"
            success = True
        else:
            content = f"Image generation failed: {result.get('error', 'Unknown error')}"
            success = False
        
        return AgentResult(
            agent=self.agent_id,
            model=result.get("provider", "dalle"),
            action="generate",
            content=content,
            success=success,
            metadata={
                "prompt": prompt,
                "style": style,
                "url": result.get("url", ""),
                "success": result.get("success", False),
                "error": result.get("error"),
                "dimensions": result.get("dimensions", "1024x1024"),
            },
            context_updates={
                "images": [{
                    "prompt": prompt,
                    "url": result.get("url", ""),
                    "style": style,
                    "dimensions": result.get("dimensions", "1024x1024"),
                    "success": result.get("success", False),
                }],
                "context_snippets": [f"[IMAGE] Generated: {result.get('revised_prompt', prompt)}"],
            },
        )
    
    async def _generate_image(self, prompt: str, style: str) -> Dict[str, Any]:
        """Generate an image using the configured provider."""
        provider = config.IMAGE_PROVIDER
        
        if provider == "gemini":
            return await self._generate_gemini(prompt, style)
        else:
            return await self._generate_dalle(prompt, style)
    
    async def _generate_dalle(self, prompt: str, style: str) -> Dict[str, Any]:
        """Generate image using DALL-E."""
        if not config.OPENAI_API_KEY:
            return {
                "success": False,
                "error": "OPENAI_API_KEY not set",
                "url": "https://placehold.co/512x512/1a1a2e/eaeaea?text=No+API+Key",
                "provider": "dalle",
            }
        
        style_suffix = self.IMAGE_STYLES.get(style, self.IMAGE_STYLES["photo"])
        enhanced_prompt = f"{prompt}. Style: {style_suffix}"
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/images/generations",
                    headers={
                        "Authorization": f"Bearer {config.OPENAI_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "dall-e-3",
                        "prompt": enhanced_prompt,
                        "n": 1,
                        "size": "1024x1024",
                        "quality": "standard",
                    },
                )
                
                if response.status_code != 200:
                    error_msg = response.json().get("error", {}).get("message", response.text)
                    return {
                        "success": False,
                        "error": f"DALL-E API error: {error_msg}",
                        "url": "https://placehold.co/512x512/1a1a2e/ff6b6b?text=Generation+Failed",
                        "provider": "dalle",
                    }
                
                data = response.json()
                return {
                    "success": True,
                    "url": data["data"][0]["url"],
                    "revised_prompt": data["data"][0].get("revised_prompt", enhanced_prompt),
                    "dimensions": "1024x1024",
                    "provider": "dalle",
                }
                
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Image generation timed out",
                "url": "https://placehold.co/512x512/1a1a2e/ff6b6b?text=Timeout",
                "provider": "dalle",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": "https://placehold.co/512x512/1a1a2e/ff6b6b?text=Error",
                "provider": "dalle",
            }
    
    async def _generate_gemini(self, prompt: str, style: str) -> Dict[str, Any]:
        """Generate image using Gemini."""
        if not config.GOOGLE_API_KEY:
            # Fallback to DALL-E if available
            if config.OPENAI_API_KEY:
                result = await self._generate_dalle(prompt, style)
                result["fallback_from"] = "gemini: No API key"
                return result
            return {
                "success": False,
                "error": "GOOGLE_API_KEY not set",
                "url": "https://placehold.co/512x512/1a1a2e/eaeaea?text=No+API+Key",
                "provider": "gemini",
            }
        
        style_suffix = self.IMAGE_STYLES.get(style, self.IMAGE_STYLES["diagram"])
        enhanced_prompt = f"{prompt}. Style: {style_suffix}"
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={config.GOOGLE_API_KEY}",
                    json={
                        "contents": [{"parts": [{"text": enhanced_prompt}]}],
                        "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
                    },
                )
                
                if response.status_code != 200:
                    # Fallback to DALL-E
                    if config.OPENAI_API_KEY:
                        result = await self._generate_dalle(prompt, style)
                        result["fallback_from"] = f"gemini: API error {response.status_code}"
                        return result
                    return {
                        "success": False,
                        "error": f"Gemini API error: {response.status_code}",
                        "url": "https://placehold.co/512x512/1a1a2e/ff6b6b?text=Generation+Failed",
                        "provider": "gemini",
                    }
                
                data = response.json()
                
                # Extract image from response
                for candidate in data.get("candidates", []):
                    for part in candidate.get("content", {}).get("parts", []):
                        inline = part.get("inline_data") or part.get("inlineData")
                        if inline and inline.get("data"):
                            mime = inline.get("mime_type") or inline.get("mimeType") or "image/png"
                            return {
                                "success": True,
                                "url": f"data:{mime};base64,{inline['data']}",
                                "revised_prompt": enhanced_prompt,
                                "dimensions": "1024x1024",
                                "provider": "gemini",
                            }
                
                # No image in response - fallback
                if config.OPENAI_API_KEY:
                    result = await self._generate_dalle(prompt, style)
                    result["fallback_from"] = "gemini: No image in response"
                    return result
                    
                return {
                    "success": False,
                    "error": "Gemini did not return an image",
                    "url": "https://placehold.co/512x512/1a1a2e/ff6b6b?text=No+Image",
                    "provider": "gemini",
                }
                
        except httpx.TimeoutException:
            if config.OPENAI_API_KEY:
                result = await self._generate_dalle(prompt, style)
                result["fallback_from"] = "gemini: Timeout"
                return result
            return {
                "success": False,
                "error": "Image generation timed out",
                "url": "https://placehold.co/512x512/1a1a2e/ff6b6b?text=Timeout",
                "provider": "gemini",
            }
        except Exception as e:
            if config.OPENAI_API_KEY:
                result = await self._generate_dalle(prompt, style)
                result["fallback_from"] = f"gemini: {str(e)}"
                return result
            return {
                "success": False,
                "error": str(e),
                "url": "https://placehold.co/512x512/1a1a2e/ff6b6b?text=Error",
                "provider": "gemini",
            }


