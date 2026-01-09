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
PRESENTATION TEMPLATE (HTML) - PROFESSIONAL SLIDE DESIGN
═══════════════════════════════════════════════════════════════════════════════

CREATE VARIED, PROFESSIONAL SLIDES using these 8 SLIDE TYPES:

1. TITLE SLIDE - Use for: Opening slide
   - Large centered title with gradient text
   - Subtitle below, optional icon above title
   - Minimal content, high impact

2. CONTENT SLIDE (Standard) - Use for: Main information
   - Left-aligned title, bullet points below
   - Add an SVG icon next to title if topic has clear visual (e.g., shield for security)

3. TWO-COLUMN SLIDE - Use for: Comparisons, pros/cons, before/after
   - Title at top, two equal columns below
   - Great for contrasting information

4. THREE-CARD SLIDE - Use for: 3 related concepts, pillars, principles
   - Three cards in a row, each with icon, title, and brief description
   - Use for core concepts, benefits, or categories

5. QUOTE/HIGHLIGHT SLIDE - Use for: Key takeaways, important statements
   - Large centered quote or key message
   - Subtle background, emphasis styling
   - Use sparingly (1 per presentation max)

6. NUMBERED LIST SLIDE - Use for: Steps, processes, rankings
   - Large numbers (1, 2, 3...) with descriptions
   - Shows sequence or priority

7. STATISTICS/METRICS SLIDE - Use for: Data, percentages, numbers
   - Large bold numbers with labels
   - Visual impact for quantitative information

8. CONCLUSION SLIDE - Use for: Final slide, summary
   - Key takeaways as bullet points
   - Call-to-action or sources

SVG ICONS TO USE (inline, 48-64px, matching theme colors):
- 📋 Clipboard/Document: <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>
- 🛡️ Shield/Security: <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
- ⚡ Lightning/Fast: <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
- ✓ Check/Success: <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
- 🎯 Target/Goal: <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
- 📊 Chart/Analytics: <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
- 👥 Users/Team: <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>
- ⚙️ Settings/Process: <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
- 📦 Box/Package: <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
- 🔒 Lock/Privacy: <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
- 📝 Edit/Write: <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
- ⚠️ Warning/Alert: <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
- 🍽️ Food/Restaurant: <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8h1a4 4 0 010 8h-1"/><path d="M2 8h16v9a4 4 0 01-4 4H6a4 4 0 01-4-4V8z"/><line x1="6" y1="1" x2="6" y2="4"/><line x1="10" y1="1" x2="10" y2="4"/><line x1="14" y1="1" x2="14" y2="4"/></svg>
- 🏥 Medical/Health: <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
- 🌍 Globe/World: <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>
- 📖 Book/Education: <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg>

FULL HTML TEMPLATE WITH SLIDE TYPES:

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
        .slide { width: 100%; height: 100%; display: none; flex-direction: column; justify-content: center; align-items: center; padding: 60px; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); }
        .slide.active { display: flex; animation: fadeIn 0.5s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        
        /* Typography */
        h1 { font-size: 3.5rem; font-weight: 700; margin-bottom: 1rem; background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }
        h2 { font-size: 2.5rem; font-weight: 600; margin-bottom: 2rem; color: #e2e8f0; }
        h3 { font-size: 1.5rem; font-weight: 600; color: #60a5fa; margin-bottom: 0.5rem; }
        p, li { font-size: 1.4rem; line-height: 1.8; color: #cbd5e1; }
        .subtitle { font-size: 1.5rem; color: #94a3b8; margin-top: 1rem; }
        
        /* Icons */
        .icon { width: 64px; height: 64px; stroke: #60a5fa; margin-bottom: 1rem; }
        .icon-sm { width: 32px; height: 32px; stroke: #60a5fa; }
        .icon-title { display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem; }
        .icon-title .icon { margin-bottom: 0; }
        
        /* Content layouts */
        .content-left { width: 100%; max-width: 1000px; text-align: left; }
        ul { list-style: none; }
        li { margin-bottom: 1rem; padding-left: 2rem; position: relative; }
        li::before { content: "→"; color: #60a5fa; position: absolute; left: 0; }
        
        /* Two columns */
        .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 60px; width: 100%; max-width: 1200px; }
        .col { background: rgba(30, 41, 59, 0.5); padding: 2rem; border-radius: 1rem; border: 1px solid #334155; }
        
        /* Three cards */
        .three-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; width: 100%; max-width: 1200px; }
        .card { background: rgba(30, 41, 59, 0.7); padding: 2rem; border-radius: 1rem; border: 1px solid #334155; text-align: center; transition: transform 0.3s, border-color 0.3s; }
        .card:hover { transform: translateY(-5px); border-color: #60a5fa; }
        .card .icon { stroke: #a78bfa; }
        .card h3 { margin-top: 1rem; }
        .card p { font-size: 1.1rem; color: #94a3b8; }
        
        /* Quote slide */
        .quote { font-size: 2.2rem; font-style: italic; color: #e2e8f0; max-width: 900px; text-align: center; line-height: 1.6; }
        .quote::before { content: '"'; font-size: 4rem; color: #60a5fa; display: block; margin-bottom: -1rem; }
        
        /* Stats */
        .stats { display: flex; gap: 60px; justify-content: center; }
        .stat { text-align: center; }
        .stat-number { font-size: 4rem; font-weight: 700; background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .stat-label { font-size: 1.2rem; color: #94a3b8; margin-top: 0.5rem; }
        
        /* Numbered list */
        .numbered-list { counter-reset: item; max-width: 800px; }
        .numbered-item { display: flex; align-items: flex-start; gap: 1.5rem; margin-bottom: 1.5rem; }
        .num { font-size: 2.5rem; font-weight: 700; color: #60a5fa; min-width: 60px; }
        .numbered-item p { font-size: 1.3rem; }
        
        /* Navigation */
        .nav { position: fixed; bottom: 30px; right: 30px; display: flex; gap: 10px; }
        .nav button { padding: 12px 24px; border: none; border-radius: 8px; background: #3b82f6; color: white; cursor: pointer; font-size: 1rem; transition: all 0.2s; }
        .nav button:hover { background: #2563eb; transform: scale(1.05); }
        .slide-number { position: fixed; bottom: 30px; left: 30px; color: #64748b; font-size: 1rem; }
        .progress { position: fixed; top: 0; left: 0; height: 3px; background: linear-gradient(90deg, #60a5fa, #a78bfa); transition: width 0.3s; }
    </style>
</head>
<body>
    <div class="progress" id="progress"></div>
    <div class="slide-container">
        <!-- EXAMPLE SLIDES - Mix these types for variety -->
        
        <!-- TYPE 1: Title Slide -->
        <div class="slide active">
            <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/></svg>
            <h1>Presentation Title</h1>
            <p class="subtitle">Subtitle or tagline goes here</p>
        </div>
        
        <!-- TYPE 2: Content with Icon -->
        <div class="slide">
            <div class="content-left">
                <div class="icon-title">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                    <h1>Section Title</h1>
                </div>
                <ul>
                    <li><strong>Point One</strong>: Description here</li>
                    <li><strong>Point Two</strong>: Description here</li>
                    <li><strong>Point Three</strong>: Description here</li>
                </ul>
            </div>
        </div>
        
        <!-- TYPE 3: Three Cards -->
        <div class="slide">
            <h1>Three Key Concepts</h1>
            <div class="three-cards">
                <div class="card">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
                    <h3>Concept One</h3>
                    <p>Brief description of this concept</p>
                </div>
                <div class="card">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                    <h3>Concept Two</h3>
                    <p>Brief description of this concept</p>
                </div>
                <div class="card">
                    <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
                    <h3>Concept Three</h3>
                    <p>Brief description of this concept</p>
                </div>
            </div>
        </div>
        
        <!-- TYPE 4: Two Columns -->
        <div class="slide">
            <h1>Comparison</h1>
            <div class="two-col">
                <div class="col">
                    <h3>Before / Option A</h3>
                    <ul>
                        <li>Point one</li>
                        <li>Point two</li>
                    </ul>
                </div>
                <div class="col">
                    <h3>After / Option B</h3>
                    <ul>
                        <li>Point one</li>
                        <li>Point two</li>
                    </ul>
                </div>
            </div>
        </div>
        
        <!-- TYPE 5: Quote/Highlight -->
        <div class="slide">
            <p class="quote">This is a key takeaway or important quote that deserves emphasis.</p>
        </div>
        
        <!-- TYPE 6: Stats -->
        <div class="slide">
            <h1>Key Metrics</h1>
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">85%</div>
                    <div class="stat-label">Metric Label</div>
                </div>
                <div class="stat">
                    <div class="stat-number">2.5M</div>
                    <div class="stat-label">Another Metric</div>
                </div>
                <div class="stat">
                    <div class="stat-number">99.9%</div>
                    <div class="stat-label">Third Metric</div>
                </div>
            </div>
        </div>
    </div>
    <div class="nav">
        <button onclick="prevSlide()">← Prev</button>
        <button onclick="nextSlide()">Next →</button>
    </div>
    <div class="slide-number">Slide <span id="current">1</span> of <span id="total">X</span></div>
    <script>
        let currentSlide = 0;
        const slides = document.querySelectorAll('.slide');
        const progress = document.getElementById('progress');
        document.getElementById('total').textContent = slides.length;
        function showSlide(n) {
            slides[currentSlide].classList.remove('active');
            currentSlide = (n + slides.length) % slides.length;
            slides[currentSlide].classList.add('active');
            document.getElementById('current').textContent = currentSlide + 1;
            progress.style.width = ((currentSlide + 1) / slides.length * 100) + '%';
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

SLIDE SELECTION GUIDELINES:
- Slide 1: Always use TITLE SLIDE
- Slide 2-3: Use CONTENT WITH ICON for main topics
- If 3 related items: Use THREE-CARD SLIDE
- If comparing: Use TWO-COLUMN SLIDE
- If process/steps: Use NUMBERED LIST SLIDE
- If data: Use STATISTICS SLIDE
- 1 per presentation max: QUOTE SLIDE for key message
- Final slide: CONCLUSION with sources

ICON SELECTION: Match icon to topic. Shield for security/compliance, Chart for data, Users for teams, Food icons for food topics, Medical for health, etc. NOT every slide needs an icon - use them for emphasis on key slides only.

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
