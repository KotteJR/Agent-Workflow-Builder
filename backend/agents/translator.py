"""
Translator Agent - Translates text between any languages.

Supports all major world languages with high-quality AI translation.
"""

from typing import Any, Dict, Optional

from agents.base import BaseAgent, AgentResult


class TranslatorAgent(BaseAgent):
    """
    Translator Agent that translates text between languages.
    
    Capabilities:
    - Translate between any language pair
    - Preserve formatting and structure
    - Handle technical terminology
    - Support document-level translation
    """
    
    agent_id = "translator"
    display_name = "Translator"
    default_model = "small"
    
    # Comprehensive list of supported languages
    SUPPORTED_LANGUAGES = {
        # Major world languages
        "en": "English",
        "ar": "Arabic",
        "zh": "Chinese (Simplified)",
        "zh-TW": "Chinese (Traditional)",
        "fr": "French",
        "de": "German",
        "es": "Spanish",
        "pt": "Portuguese",
        "ru": "Russian",
        "ja": "Japanese",
        "ko": "Korean",
        "it": "Italian",
        "nl": "Dutch",
        "pl": "Polish",
        "tr": "Turkish",
        "vi": "Vietnamese",
        "th": "Thai",
        "id": "Indonesian",
        "ms": "Malay",
        "hi": "Hindi",
        "bn": "Bengali",
        "ur": "Urdu",
        "fa": "Persian (Farsi)",
        "he": "Hebrew",
        "sv": "Swedish",
        "da": "Danish",
        "no": "Norwegian",
        "fi": "Finnish",
        "el": "Greek",
        "cs": "Czech",
        "ro": "Romanian",
        "hu": "Hungarian",
        "uk": "Ukrainian",
        "bg": "Bulgarian",
        "hr": "Croatian",
        "sk": "Slovak",
        "sl": "Slovenian",
        "sr": "Serbian",
        "mk": "Macedonian",
        "lt": "Lithuanian",
        "lv": "Latvian",
        "et": "Estonian",
        "tl": "Filipino (Tagalog)",
        "sw": "Swahili",
        "af": "Afrikaans",
        "am": "Amharic",
        "my": "Burmese",
        "km": "Khmer",
        "lo": "Lao",
        "ne": "Nepali",
        "si": "Sinhala",
        "ta": "Tamil",
        "te": "Telugu",
        "ml": "Malayalam",
        "kn": "Kannada",
        "gu": "Gujarati",
        "mr": "Marathi",
        "pa": "Punjabi",
        "auto": "Auto-detect",
    }
    
    SYSTEM_PROMPT = """You are a professional translator. Your ONLY job is to translate text while keeping the EXACT same format.

TASK: Translate from {source_lang} to {target_lang}.

CRITICAL RULES - YOU MUST FOLLOW:
1. KEEP THE EXACT SAME FORMAT - if input is CSV, output must be CSV. If JSON, output JSON. If markdown table, output markdown table.
2. ONLY translate the actual text/words - never change structure, delimiters, or formatting
3. Keep column headers, row structure, JSON keys, markdown syntax EXACTLY as they are (but translate the text values)
4. Numbers, dates, codes, IDs must stay UNCHANGED
5. DO NOT add any explanations, notes, or commentary
6. DO NOT wrap output in code blocks or add formatting that wasn't there

FORMAT-SPECIFIC RULES:
- CSV: Keep commas, quotes, newlines exactly. Only translate text inside cells.
- JSON: Keep all JSON syntax. Only translate string values (not keys).
- Markdown tables: Keep | and - characters. Only translate cell content.
- Plain text: Translate all text, keep paragraph breaks.
- Lists: Keep bullet points/numbers, translate the text.

OUTPUT: Return ONLY the translated content in the EXACT same format as input.
If source and target language are the same, return the input unchanged."""

    async def execute(
        self,
        user_message: str,
        context: Dict[str, Any],
        settings: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
    ) -> AgentResult:
        """
        Translate text between languages.
        
        Args:
            user_message: Original query
            context: Contains text to translate
            settings: Contains 'sourceLanguage' and 'targetLanguage'
            model: Model override
            
        Returns:
            AgentResult with translated text
        """
        settings = settings or {}
        source_lang = settings.get("sourceLanguage", "auto")
        target_lang = settings.get("targetLanguage", "en")
        
        # Get content to translate - check ALL possible sources from previous nodes
        # Priority: most specific output first, then general content
        content_to_translate = None
        content_source = None
        
        # Check in order of priority - what the previous node likely produced
        sources_to_check = [
            ("transformed_content", context.get("transformed_content")),  # From transformer
            ("synthesis_result", context.get("synthesis_result")),  # From synthesis
            ("sampler_best", context.get("sampler_best")),  # From sampler
            ("search_results", context.get("search_results")),  # From semantic search
            ("final_answer", context.get("final_answer")),  # General output
            ("input_content", context.get("input_content")),  # Passed through
            ("uploaded_file_content", context.get("uploaded_file_content")),  # From upload
        ]
        
        for source_name_key, content in sources_to_check:
            if content and len(str(content).strip()) > 0:
                content_to_translate = str(content)
                content_source = source_name_key
                break
        
        # Last resort: context snippets or user message
        if not content_to_translate:
            snippets = context.get("context_snippets", [])
            if snippets:
                content_to_translate = "\n\n".join(snippets)
                content_source = "context_snippets"
        
        if not content_to_translate:
            content_to_translate = user_message
            content_source = "user_message"
        
        # Detect format for logging
        detected_format = "text"
        if content_to_translate:
            first_line = content_to_translate.strip().split('\n')[0] if content_to_translate else ""
            if ',' in first_line and (first_line.count(',') >= 2 or '"' in first_line):
                detected_format = "CSV"
            elif content_to_translate.strip().startswith('{') or content_to_translate.strip().startswith('['):
                detected_format = "JSON"
            elif '|' in first_line and '-' in content_to_translate[:200]:
                detected_format = "markdown table"
        
        # Get language names
        source_name = self.SUPPORTED_LANGUAGES.get(source_lang, source_lang)
        target_name = self.SUPPORTED_LANGUAGES.get(target_lang, target_lang)
        
        print(f"[TRANSLATOR] Source: {content_source}")
        print(f"[TRANSLATOR] Detected format: {detected_format}")
        print(f"[TRANSLATOR] Translating from {source_name} to {target_name}")
        print(f"[TRANSLATOR] Content length: {len(content_to_translate) if content_to_translate else 0} chars")
        
        if not content_to_translate:
            return AgentResult(
                agent=self.agent_id,
                model="gpt-4o",
                action="translate",
                content="No content available to translate.",
                success=False,
                metadata={"error": "No input content"},
            )
        
        # Build system prompt
        system_prompt = self.SYSTEM_PROMPT.format(
            source_lang=source_name,
            target_lang=target_name
        )
        
        # Truncate if too long
        max_chars = 50000
        if len(content_to_translate) > max_chars:
            content_to_translate = content_to_translate[:max_chars] + "\n\n[Text truncated...]"
        
        # Add format hint to help preserve structure
        format_hint = ""
        if detected_format == "CSV":
            format_hint = "\n\nIMPORTANT: This is CSV data. Keep all commas, quotes, and row structure. Only translate the text content inside cells."
        elif detected_format == "JSON":
            format_hint = "\n\nIMPORTANT: This is JSON data. Keep all JSON syntax intact. Only translate string values, not keys."
        elif detected_format == "markdown table":
            format_hint = "\n\nIMPORTANT: This is a markdown table. Keep all | and - characters. Only translate the text in cells."
        
        user_prompt = f"""Translate the following from {source_name} to {target_name}.
Keep the EXACT same format - only translate the words/text.{format_hint}

{content_to_translate}

Output the translated version in the exact same format:"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        # Use the large model for better translation quality
        actual_model = model or "gpt-4o"
        
        translated = await self._chat(
            messages=messages,
            model=actual_model,
            temperature=0.3,  # Low temperature for consistent translations
            max_tokens=8000,
        )
        
        print(f"[TRANSLATOR] Translation complete: {len(translated)} chars")
        
        return AgentResult(
            agent=self.agent_id,
            model=actual_model,
            action="translate",
            content=translated,
            metadata={
                "source_language": source_lang,
                "target_language": target_lang,
                "source_name": source_name,
                "target_name": target_name,
                "original_length": len(content_to_translate),
                "translated_length": len(translated),
            },
            context_updates={
                "translated_content": translated,
                "input_content": translated,
                "final_answer": translated,
            },
        )

