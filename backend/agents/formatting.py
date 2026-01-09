"""
Formatting Agent - Advanced Code & Content Generation.

Generates production-quality code, presentations, documents,
and structured outputs in various formats.
"""

from typing import Any, Dict, List, Optional

from agents.base import BaseAgent, AgentResult
from models import LLMClientProtocol


class FormattingAgent(BaseAgent):
    """
    Advanced Formatting Agent for code and content generation.
    
    Capabilities:
    - Generates complete HTML presentations with animations
    - Creates React/TypeScript components
    - Produces styled HTML documents
    - Converts to JSON, XML, Markdown, CSV, YAML
    - Generates interactive code with CSS styling
    """
    
    agent_id = "formatting"
    display_name = "Formatting Agent"
    default_model = "large"  # Use large model for better code generation
    
    SYSTEM_PROMPT = """You are an Expert Code Generator and Formatter. You create production-quality, visually stunning code outputs.

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT DETECTION
═══════════════════════════════════════════════════════════════════════════════

Based on the request, generate the appropriate format:

**PRESENTATION/SLIDES:**
→ Generate complete HTML with embedded CSS
→ Include slide navigation, transitions, animations
→ Modern design with gradients, shadows, typography
→ Self-contained (no external dependencies)

**REACT/TYPESCRIPT COMPONENT:**
→ Generate complete TSX component
→ Include Tailwind CSS classes or inline styles
→ Proper TypeScript types
→ Export as default component

**HTML DOCUMENT:**
→ Complete HTML5 document
→ Embedded CSS in <style> tags
→ Modern, responsive design
→ Clean semantic markup

**DATA FORMATS (JSON/XML/CSV/YAML):**
→ Properly structured data
→ Consistent formatting
→ Valid syntax

═══════════════════════════════════════════════════════════════════════════════
PRESENTATION TEMPLATE (HTML)
═══════════════════════════════════════════════════════════════════════════════

When creating presentations, use this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Presentation Title]</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0f172a; color: #f8fafc; }
        .slide-container { width: 100vw; height: 100vh; overflow: hidden; position: relative; }
        .slide { 
            width: 100%; height: 100%; 
            display: none; 
            flex-direction: column; 
            justify-content: center; 
            align-items: center;
            padding: 60px;
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        }
        .slide.active { display: flex; animation: fadeIn 0.5s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        h1 { font-size: 3.5rem; font-weight: 700; margin-bottom: 1rem; background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        h2 { font-size: 2.5rem; font-weight: 600; margin-bottom: 2rem; color: #e2e8f0; }
        p, li { font-size: 1.5rem; line-height: 1.8; color: #cbd5e1; }
        ul { list-style: none; }
        li::before { content: "→ "; color: #60a5fa; }
        .nav { position: fixed; bottom: 30px; right: 30px; display: flex; gap: 10px; }
        .nav button { padding: 12px 24px; border: none; border-radius: 8px; background: #3b82f6; color: white; cursor: pointer; font-size: 1rem; transition: all 0.2s; }
        .nav button:hover { background: #2563eb; transform: scale(1.05); }
        .slide-number { position: fixed; bottom: 30px; left: 30px; color: #64748b; font-size: 1rem; }
    </style>
</head>
<body>
    <div class="slide-container">
        <!-- Slides go here -->
        <div class="slide active">
            <h1>Title Slide</h1>
            <p>Subtitle or description</p>
        </div>
        <!-- More slides... -->
    </div>
    <div class="nav">
        <button onclick="prevSlide()">← Prev</button>
        <button onclick="nextSlide()">Next →</button>
    </div>
    <div class="slide-number">Slide <span id="current">1</span> of <span id="total">X</span></div>
    <script>
        let currentSlide = 0;
        const slides = document.querySelectorAll('.slide');
        document.getElementById('total').textContent = slides.length;
        function showSlide(n) {
            slides[currentSlide].classList.remove('active');
            currentSlide = (n + slides.length) % slides.length;
            slides[currentSlide].classList.add('active');
            document.getElementById('current').textContent = currentSlide + 1;
        }
        function nextSlide() { showSlide(currentSlide + 1); }
        function prevSlide() { showSlide(currentSlide - 1); }
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight' || e.key === ' ') nextSlide();
            if (e.key === 'ArrowLeft') prevSlide();
        });
    </script>
</body>
</html>
```

═══════════════════════════════════════════════════════════════════════════════
REACT/TSX COMPONENT TEMPLATE
═══════════════════════════════════════════════════════════════════════════════

When creating React components:

```tsx
import React, { useState } from 'react';

interface SlideData {
  title: string;
  content: string[];
}

const Presentation: React.FC = () => {
  const [currentSlide, setCurrentSlide] = useState(0);
  
  const slides: SlideData[] = [
    { title: "Title", content: ["Point 1", "Point 2"] },
    // More slides...
  ];
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white">
      {/* Slide content */}
    </div>
  );
};

export default Presentation;
```

═══════════════════════════════════════════════════════════════════════════════
QUALITY REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════

1. **Complete & Runnable**: Code must work without modifications
2. **Modern Design**: Use gradients, shadows, animations, good typography
3. **Self-Contained**: No external dependencies (inline CSS, no CDN links)
4. **Responsive**: Works on different screen sizes
5. **Interactive**: Include navigation, hover effects, transitions
6. **Clean Code**: Well-structured, commented where needed

Output ONLY the code. No explanations before or after."""

    FORMAT_CONFIGS = {
        "html": {
            "hint": "Generate complete, styled HTML5 document",
            "wrapper": None,
        },
        "presentation": {
            "hint": "Generate interactive HTML presentation with slides, navigation, and animations",
            "wrapper": None,
        },
        "tsx": {
            "hint": "Generate complete React TypeScript component with Tailwind CSS",
            "wrapper": None,
        },
        "react": {
            "hint": "Generate complete React component with inline styles",
            "wrapper": None,
        },
        "json": {
            "hint": "Generate valid JSON with proper structure",
            "wrapper": None,
        },
        "xml": {
            "hint": "Generate valid XML with proper tags and nesting",
            "wrapper": None,
        },
        "markdown": {
            "hint": "Generate formatted Markdown with headers, lists, code blocks",
            "wrapper": None,
        },
        "csv": {
            "hint": "Generate CSV with headers in first row",
            "wrapper": None,
        },
        "yaml": {
            "hint": "Generate valid YAML with proper indentation",
            "wrapper": None,
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
        Generate formatted code or content.
        
        Args:
            user_message: Original query
            context: Contains content to format
            settings: Contains 'outputFormat'
            model: Model to use
            
        Returns:
            AgentResult with generated code/content
        """
        settings = settings or {}
        output_format = settings.get("outputFormat", "html").lower()
        
        # Detect if user wants a presentation
        user_lower = user_message.lower()
        if any(word in user_lower for word in ["presentation", "slides", "slideshow", "ppt", "powerpoint"]):
            output_format = "presentation"
        
        # Get content/topic to work with
        content = self._get_content(context, user_message)
        
        # Get supervisor guidance
        supervisor_guidance = context.get("supervisor_guidance", "")
        
        # Build the prompt
        format_config = self.FORMAT_CONFIGS.get(output_format, self.FORMAT_CONFIGS["html"])
        
        user_prompt = f"""Create a {output_format.upper()} output for the following:

═══════════════════════════════════════════════════════════════════════════════
CONTENT/TOPIC
═══════════════════════════════════════════════════════════════════════════════

{content}

═══════════════════════════════════════════════════════════════════════════════
USER REQUEST
═══════════════════════════════════════════════════════════════════════════════

{user_message}

═══════════════════════════════════════════════════════════════════════════════
FORMAT REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════

{format_config['hint']}

{f"Additional guidance: {supervisor_guidance}" if supervisor_guidance else ""}

Generate the complete {output_format.upper()} now. Output ONLY the code, no explanations."""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        
        # Use large model for quality
        actual_model = model or "gpt-4o"
        
        print(f"[FORMATTING] Output format: {output_format}")
        print(f"[FORMATTING] Content length: {len(content)}")
        
        result = await self._chat(
            messages=messages,
            model=actual_model,
            temperature=0.3,  # Slightly higher for creativity
            max_tokens=4096,
        )
        
        # Clean up response
        result = self._clean_output(result, output_format)
        
        # Determine the code language for the viewer
        code_language = self._get_code_language(output_format)
        
        return AgentResult(
            agent=self.agent_id,
            model=actual_model,
            action="format",
            content=result,
            metadata={
                "output_format": output_format,
                "code_language": code_language,
                "content_length": len(result),
                "is_code": output_format in ["html", "presentation", "tsx", "react", "json", "xml", "yaml"],
            },
            context_updates={
                "formatted_content": result,
                "code_content": result,
                "code_language": code_language,
                "output_format": output_format,  # Pass format for code_viewer
                "input_content": result,
                "final_answer": result,
            },
        )
    
    def _get_content(self, context: Dict[str, Any], user_message: str) -> str:
        """Get content to format from context."""
        # Check various context sources
        sources = [
            "input_content",
            "final_answer",
            "search_results",
            "synthesis_content",
        ]
        
        for source in sources:
            content = context.get(source)
            if content and len(str(content).strip()) > 10:
                return str(content)
        
        # Check snippets
        snippets = context.get("context_snippets", [])
        if snippets:
            return "\n\n".join(snippets)
        
        # Use user message as topic
        return user_message
    
    def _clean_output(self, output: str, format_type: str) -> str:
        """Clean up LLM output, removing markdown code blocks."""
        output = output.strip()
        
        # Remove markdown code blocks
        if output.startswith("```"):
            lines = output.split("\n")
            # Remove first line (```html, ```tsx, etc.)
            if lines[0].startswith("```"):
                lines = lines[1:]
            # Remove last line if it's closing ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            output = "\n".join(lines)
        
        return output.strip()
    
    def _get_code_language(self, format_type: str) -> str:
        """Map format type to code language for syntax highlighting."""
        mapping = {
            "html": "html",
            "presentation": "html",
            "tsx": "typescript",
            "react": "typescript",
            "json": "json",
            "xml": "xml",
            "markdown": "markdown",
            "csv": "csv",
            "yaml": "yaml",
        }
        return mapping.get(format_type, "text")
