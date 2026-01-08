"""
Image Generator Agent - Generates images from text descriptions.

Uses DALL-E, Gemini, or Nano Banana Pro (Gemini 3 Pro Image) to generate images 
based on prompts, with support for different image types and styles.
Nano Banana Pro supports up to 4K resolution and advanced text rendering.
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
    - Uses DALL-E, Gemini, or Nano Banana Pro (Gemini 3 Pro Image) as provider
    - Nano Banana Pro supports up to 4K resolution and advanced text rendering
    - Enhances prompts for better results
    """
    
    agent_id = "image_generator"
    display_name = "Image Generator"
    default_model = "nano-banana"  # Uses image generation model
    
    # Base style templates - these are the foundation for each style
    # Users can override or enhance with their own instructions
    IMAGE_STYLE_BASES = {
        "diagram": {
            "base": "technical diagram, structured layout, clean lines",
            "professional": "business presentation style, white background, corporate design, suitable for boardroom presentations",
            "minimal": "simple diagram, basic shapes, clear labels",
            "detailed": "comprehensive diagram, detailed annotations, multiple components",
        },
        "infographic": {
            "base": "infographic style, visual data representation",
            "professional": "corporate infographic, data visualization, clear hierarchy",
            "minimal": "simple infographic, key points only",
            "detailed": "comprehensive infographic, statistics, icons, visual flow",
        },
        "flowchart": {
            "base": "flowchart, process diagram, connected nodes",
            "professional": "business process flowchart, decision points, clear flow direction",
            "minimal": "simple flowchart, basic shapes",
            "detailed": "detailed process map, all steps, conditions, loops",
        },
        "photo": {
            "base": "photorealistic image",
            "professional": "professional photography, high quality, studio lighting",
            "minimal": "simple photo, clean background",
            "detailed": "highly detailed photograph, intricate details",
        },
        "illustration": {
            "base": "digital illustration",
            "professional": "professional illustration, clean lines, polished",
            "minimal": "simple illustration, flat design",
            "detailed": "detailed illustration, rich textures, depth",
        },
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
            settings: Contains 'imageType', 'stylePreset', 'customInstructions', 'imageDetailLevel'
            model: Not used (uses IMAGE_PROVIDER from config)
            
        Returns:
            AgentResult with generated image
        """
        settings = settings or {}
        image_type = settings.get("imageType", "diagram")
        style_preset = settings.get("stylePreset", "professional")  # professional, minimal, detailed
        custom_instructions = settings.get("customInstructions", "")  # User's custom style instructions
        detail_level = settings.get("imageDetailLevel", 50)  # 0-100 slider value
        
        # Get prompt from orchestrator if available, otherwise use user message
        orchestrator_result = context.get("orchestrator_result", {})
        prompt = orchestrator_result.get("image_prompt", user_message)
        style = orchestrator_result.get("image_type", image_type)
        
        # Auto-detect diagram requests
        prompt_lower = prompt.lower()
        if any(keyword in prompt_lower for keyword in ["diagram", "flowchart", "chart", "graph", "principle", "process", "workflow", "system"]):
            if style == "photo":  # Only override if default
                style = "diagram"
        
        # Build the style string from components
        style_config = self.IMAGE_STYLE_BASES.get(style, self.IMAGE_STYLE_BASES["diagram"])
        base_style = style_config.get("base", "")
        preset_style = style_config.get(style_preset, style_config.get("professional", ""))
        
        # Adjust detail based on slider (0-100)
        detail_modifier = ""
        if detail_level < 30:
            detail_modifier = "simple, minimal details"
        elif detail_level > 70:
            detail_modifier = "highly detailed, comprehensive, intricate"
        
        # Combine all style components
        style_parts = [base_style, preset_style]
        if detail_modifier:
            style_parts.append(detail_modifier)
        if custom_instructions:
            style_parts.append(custom_instructions)
        
        final_style = ", ".join(filter(None, style_parts))
        
        # Generate image with the composed style
        result = await self._generate_image(prompt, style, final_style)
        
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
    
    async def _generate_image(self, prompt: str, style: str, style_instructions: str) -> Dict[str, Any]:
        """Generate an image using the configured provider."""
        provider = config.IMAGE_PROVIDER
        
        if provider == "gemini" or provider == "nano-banana":
            return await self._generate_gemini(prompt, style, style_instructions)
        else:
            return await self._generate_dalle(prompt, style, style_instructions)
    
    async def _generate_dalle(self, prompt: str, style: str, style_instructions: str) -> Dict[str, Any]:
        """Generate image using DALL-E."""
        if not config.OPENAI_API_KEY:
            return {
                "success": False,
                "error": "OPENAI_API_KEY not set",
                "url": "https://placehold.co/512x512/1a1a2e/eaeaea?text=No+API+Key",
                "provider": "dalle",
            }
        
        # Build enhanced prompt with user-provided or computed style instructions
        if style in ["diagram", "flowchart", "infographic"]:
            enhanced_prompt = f"Create a {style}: {prompt}. Style requirements: {style_instructions}"
        else:
            enhanced_prompt = f"{prompt}. Style: {style_instructions}"
        
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
    
    async def _generate_gemini(self, prompt: str, style: str, style_instructions: str) -> Dict[str, Any]:
        """Generate image using Gemini (supports Nano Banana Pro / Gemini 3 Pro Image)."""
        if not config.GOOGLE_API_KEY:
            return {
                "success": False,
                "error": "GOOGLE_API_KEY not set. Nano Banana Pro requires a Google API key.",
                "url": "https://placehold.co/512x512/1a1a2e/eaeaea?text=No+API+Key",
                "provider": "nano-banana" if config.IMAGE_PROVIDER == "nano-banana" else "gemini",
            }
        
        # Use configured model, with fallback options
        primary_model = config.GEMINI_IMAGE_MODEL
        # Fallback models that support image generation
        fallback_models = ["gemini-3-pro-image-preview", "gemini-1.5-pro", "gemini-1.5-flash"]
        models_to_try = [primary_model] + [m for m in fallback_models if m != primary_model]
        
        provider_name = "nano-banana" if config.IMAGE_PROVIDER == "nano-banana" else "gemini"
        
        # Build enhanced prompt with user-provided or computed style instructions
        if style in ["diagram", "flowchart", "infographic"]:
            enhanced_prompt = f"Create a {style}: {prompt}. Style requirements: {style_instructions}"
        else:
            enhanced_prompt = f"{prompt}. Style: {style_instructions}"
        
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            logger.info(f"Generating image with {provider_name}")
            logger.debug(f"Enhanced prompt: {enhanced_prompt[:200]}...")
            
            async with httpx.AsyncClient(timeout=90.0) as client:  # Increased timeout for 4K generation
                # Try each model until one works
                last_error = None
                response = None
                successful_model = None
                
                for model_name in models_to_try:
                    try:
                        logger.info(f"Trying model: {model_name}")
                        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={config.GOOGLE_API_KEY}"
                        
                        # Try with image generation config
                        request_payload = {
                            "contents": [{"parts": [{"text": enhanced_prompt}]}],
                            "generationConfig": {
                                "responseModalities": ["IMAGE"],
                                "temperature": 0.4,  # Lower temperature for more consistent professional output
                            },
                        }
                        
                        response = await client.post(api_url, json=request_payload)
                        
                        if response.status_code == 200:
                            # Success! Break out of the loop
                            successful_model = model_name
                            break
                        else:
                            # Try next model
                            error_data = {}
                            try:
                                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                            except:
                                error_data = {"text": response.text[:500]}
                            
                            error_msg = error_data.get("error", {}).get("message", f"API error {response.status_code}")
                            logger.warning(f"Model {model_name} failed: {error_msg}")
                            last_error = error_msg
                            continue
                            
                    except Exception as e:
                        logger.warning(f"Model {model_name} exception: {str(e)}")
                        last_error = str(e)
                        continue
                
                # Check if we got a successful response
                if not response or response.status_code != 200:
                    # All models failed
                    error_msg = last_error or "All models failed - no successful response"
                    logger.error(f"{provider_name} API error: All models failed. Last error: {error_msg}")
                    logger.error(f"Tried models: {models_to_try}")
                    
                    return {
                        "success": False,
                        "error": f"{provider_name.title()} API error: All models failed. Last error: {error_msg}. Tried: {', '.join(models_to_try)}",
                        "url": "https://placehold.co/512x512/1a1a2e/ff6b6b?text=Generation+Failed",
                        "provider": provider_name,
                    }
                
                # Success - process the response
                logger.info(f"Successfully got response from model: {successful_model}")
                
                data = response.json()
                logger.debug(f"Response data keys: {list(data.keys())}")
                
                # Extract image from response
                image_found = False
                for candidate in data.get("candidates", []):
                    logger.debug(f"Candidate keys: {list(candidate.keys())}")
                    content = candidate.get("content", {})
                    logger.debug(f"Content keys: {list(content.keys())}")
                    
                    for part in content.get("parts", []):
                        logger.debug(f"Part keys: {list(part.keys())}")
                        inline = part.get("inline_data") or part.get("inlineData")
                        if inline and inline.get("data"):
                            mime = inline.get("mime_type") or inline.get("mimeType") or "image/png"
                            # Support higher resolutions for Nano Banana Pro (up to 4K)
                            dimensions = "2048x2048" if provider_name == "nano-banana" else "1024x1024"
                            logger.info(f"Successfully generated image with {provider_name}")
                            return {
                                "success": True,
                                "url": f"data:{mime};base64,{inline['data']}",
                                "revised_prompt": enhanced_prompt,
                                "dimensions": dimensions,
                                "provider": provider_name,
                            }
                
                # No image in response - log the actual response structure
                logger.warning(f"No image found in {provider_name} response")
                logger.debug(f"Full response structure: {str(data)[:1000]}")
                    
                return {
                    "success": False,
                    "error": f"{provider_name.title()} did not return an image. Check API response structure.",
                    "url": "https://placehold.co/512x512/1a1a2e/ff6b6b?text=No+Image",
                    "provider": provider_name,
                }
                
        except httpx.TimeoutException:
            logger.error(f"{provider_name} request timed out after 90 seconds")
            return {
                "success": False,
                "error": f"{provider_name.title()} image generation timed out. The request took longer than 90 seconds.",
                "url": "https://placehold.co/512x512/1a1a2e/ff6b6b?text=Timeout",
                "provider": provider_name,
            }
        except Exception as e:
            logger.error(f"{provider_name} error: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": f"{provider_name.title()} error: {str(e)}",
                "url": "https://placehold.co/512x512/1a1a2e/ff6b6b?text=Error",
                "provider": provider_name,
            }


