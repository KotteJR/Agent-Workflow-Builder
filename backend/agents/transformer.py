"""
Transformer Agent - Deep document analysis and data transformation.

Converts data between formats with comprehensive document understanding,
entity extraction, and structured data generation.
"""

from typing import Any, Dict, List, Optional

from agents.base import BaseAgent, AgentResult
from models import LLMClientProtocol


class TransformerAgent(BaseAgent):
    """
    Transformer Agent that performs deep document analysis and format conversion.
    
    Capabilities:
    - Deep document understanding using GPT-4
    - Comprehensive entity extraction
    - Intelligent table structure generation
    - Multi-pass analysis for complex documents
    """
    
    agent_id = "transformer"
    display_name = "Transformer Agent"
    default_model = "large"  # Use large model by default for better understanding
    
    SYSTEM_PROMPT_COMPREHENSIVE = """You are an expert Data Analyst and Transformer Agent. Your task is to deeply analyze a document and extract ALL meaningful structured data into {to_format} format.

DOCUMENT ANALYSIS APPROACH:
1. First, thoroughly read and understand the entire document
2. Identify ALL entities: people, organizations, dates, numbers, concepts, relationships
3. Find ALL structured data: tables, lists, key-value pairs, metadata
4. Extract implicit information and relationships
5. Organize into a comprehensive, well-structured output

{custom_columns_instruction}

EXTRACTION REQUIREMENTS ({extraction_depth} depth):
{depth_instructions}

CSV OUTPUT REQUIREMENTS:
- First row MUST be descriptive column headers
- Each row represents one entity/record/item
- Use proper CSV escaping (quotes around text with commas)
- Include ALL relevant data points, not just surface-level information
- If document has multiple sections, extract data from ALL sections
- Create logical groupings - if a paper, extract: title, authors (each author), affiliations, abstract, key findings, methodology, citations, dates, etc.
- For academic papers: extract research questions, hypotheses, conclusions, limitations
- For reports: extract executive summary, key metrics, recommendations, timelines
- For documents with tables: preserve table structure in CSV format

{supervisor_guidance}

OUTPUT FORMAT: {to_format}
Output ONLY the structured data. No explanations, no markdown code blocks."""

    DEPTH_BASIC = """- Extract main entities and primary data points
- Focus on clearly stated information
- Create 5-10 columns of key data"""

    DEPTH_DETAILED = """- Extract main and secondary entities
- Include context and relationships
- Create 10-20 columns covering major aspects
- Include metadata (dates, sources, references)"""

    DEPTH_COMPREHENSIVE = """- Extract EVERYTHING: main entities, secondary entities, relationships, metadata
- Analyze implicit information and connections
- Create 20+ columns when data supports it
- Include: identifiers, names, descriptions, categories, dates, quantities, sources, relationships, status, notes
- For each entity, capture ALL available attributes
- Extract structured data from any tables, lists, or formatted sections
- Identify and capture hierarchical relationships
- Include citation information, references, and cross-references"""

    async def execute(
        self,
        user_message: str,
        context: Dict[str, Any],
        settings: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
    ) -> AgentResult:
        """
        Transform data with deep document analysis.
        
        Args:
            user_message: Original query (for context)
            context: Contains 'input_content' to transform
            settings: Contains 'fromFormat', 'toFormat', 'useAdvancedModel', 
                     'customColumns', 'extractionDepth'
            model: Model override
            
        Returns:
            AgentResult with comprehensively extracted/transformed data
        """
        settings = settings or {}
        from_format = settings.get("fromFormat", "text")
        to_format = settings.get("toFormat", "csv")
        use_advanced = settings.get("useAdvancedModel", True)
        custom_columns = settings.get("customColumns", "")
        extraction_depth = settings.get("extractionDepth", "comprehensive")
        
        # Get spreadsheet node settings from context if available
        spreadsheet_settings = context.get("spreadsheet_settings", {})
        if not custom_columns and spreadsheet_settings:
            custom_columns = spreadsheet_settings.get("customColumns", "")
        if spreadsheet_settings.get("extractionDepth"):
            extraction_depth = spreadsheet_settings.get("extractionDepth", extraction_depth)
        
        # Get content to transform - check multiple sources
        content_to_transform = context.get("input_content")
        if not content_to_transform:
            content_to_transform = context.get("uploaded_file_content")
        if not content_to_transform:
            content_to_transform = context.get("final_answer")
        if not content_to_transform:
            snippets = context.get("context_snippets", [])
            content_to_transform = "\n\n".join(snippets) if snippets else ""
        if not content_to_transform:
            content_to_transform = context.get("user_message", "")
        
        if not content_to_transform:
            return AgentResult(
                agent=self.agent_id,
                model="gpt-4o",
                action="transform",
                content="No content available to transform.",
                success=False,
                metadata={"error": "No input content"},
            )
        
        # Determine model based on settings
        actual_model = "gpt-4o" if use_advanced else "gpt-4o-mini"
        if model:
            actual_model = model
        
        # Build custom columns instruction
        if custom_columns and custom_columns.strip():
            columns_list = [c.strip() for c in custom_columns.split(",") if c.strip()]
            custom_columns_instruction = f"""
REQUIRED COLUMNS (user specified):
The output MUST include these columns: {', '.join(columns_list)}
You may add additional relevant columns, but these must be present."""
        else:
            custom_columns_instruction = """
COLUMNS: Determine the optimal column structure based on the document content.
Include all relevant data dimensions. Aim for comprehensive coverage."""
        
        # Get depth-specific instructions
        if extraction_depth == "basic":
            depth_instructions = self.DEPTH_BASIC
        elif extraction_depth == "detailed":
            depth_instructions = self.DEPTH_DETAILED
        else:
            depth_instructions = self.DEPTH_COMPREHENSIVE
        
        # Get supervisor guidance
        supervisor_guidance = context.get("supervisor_guidance", "")
        if supervisor_guidance:
            supervisor_guidance = f"\nADDITIONAL GUIDANCE:\n{supervisor_guidance}"
        
        system_prompt = self._build_system_prompt(
            self.SYSTEM_PROMPT_COMPREHENSIVE,
            to_format=to_format.upper(),
            custom_columns_instruction=custom_columns_instruction,
            extraction_depth=extraction_depth,
            depth_instructions=depth_instructions,
            supervisor_guidance=supervisor_guidance,
        )
        
        # For large documents, chunk the content
        max_content_length = 25000 if use_advanced else 10000
        if len(content_to_transform) > max_content_length:
            content_to_transform = content_to_transform[:max_content_length] + "\n\n[Document truncated for processing...]"
        
        user_prompt = f"""Analyze this {from_format.upper()} document and extract ALL structured data into {to_format.upper()} format:

=== DOCUMENT START ===
{content_to_transform}
=== DOCUMENT END ===

Perform deep analysis and create a comprehensive {to_format.upper()} output with all extractable data."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        # Use higher max_tokens for comprehensive extraction
        max_tokens = 4000 if extraction_depth == "comprehensive" else 2000
        
        transformed = await self._chat(
            messages=messages,
            model=actual_model,
            temperature=0.1,
            max_tokens=max_tokens,
        )
        
        # Clean up response (remove markdown code blocks if present)
        if transformed.startswith("```"):
            lines = transformed.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            transformed = "\n".join(lines)
        
        # Clean any trailing whitespace
        transformed = transformed.strip()
        
        return AgentResult(
            agent=self.agent_id,
            model=actual_model,
            action="transform",
            content=transformed,
            metadata={
                "from_format": from_format,
                "to_format": to_format,
                "extraction_depth": extraction_depth,
                "used_advanced_model": use_advanced,
                "original_length": len(content_to_transform),
                "transformed_length": len(transformed),
                "custom_columns": custom_columns if custom_columns else "auto-detected",
            },
            context_updates={
                "transformed_content": transformed,
                "input_content": transformed,
                "final_answer": transformed,
            },
        )
