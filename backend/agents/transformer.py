"""
Transformer Agent - Professional Document Analysis and Data Extraction.

Performs audit-grade document analysis with structured methodology,
regulatory compliance awareness, and comprehensive data transformation.
"""

from typing import Any, Dict, List, Optional

from agents.base import BaseAgent, AgentResult
from models import LLMClientProtocol


class TransformerAgent(BaseAgent):
    """
    Professional Transformer Agent for audit-grade document extraction.
    
    Uses a structured 5-step methodology:
    1. Document Classification
    2. Schema Detection
    3. Entity Extraction
    4. Relationship Mapping
    5. Validation & Output
    """
    
    agent_id = "transformer"
    display_name = "Transformer Agent"
    default_model = "large"
    
    SYSTEM_PROMPT = """You are an Expert Document Analyst and Data Extraction Specialist. You extract structured data from ANY document type into the most appropriate format.

═══════════════════════════════════════════════════════════════════════════════
STEP 1: DOCUMENT TYPE DETECTION (Do this FIRST)
═══════════════════════════════════════════════════════════════════════════════

Analyze the document and classify it as ONE of these types:

TYPE A - REGULATORY/COMPLIANCE DOCUMENTS:
• Healthcare accreditation (JCI, JCIA, CBAHI, Joint Commission)
• Financial/banking regulations (Central Bank instructions, compliance guidelines)
• Government regulations, laws, legal standards
• ISO standards, quality management standards
• Industry compliance frameworks
→ USE THE REGULATORY SCHEMA (12 columns)

TYPE B - BUSINESS DOCUMENTS:
• Invoices, receipts, purchase orders
• Contracts, agreements, proposals
• Product catalogs, price lists
• Financial statements, reports
→ USE DOCUMENT-APPROPRIATE SCHEMA (auto-detect columns)

TYPE C - DATA DOCUMENTS:
• Forms, applications, surveys
• Lists, inventories, manifests
• Technical specifications
• Research data, tables
→ PRESERVE ORIGINAL STRUCTURE (extract as-is)

═══════════════════════════════════════════════════════════════════════════════
REGULATORY SCHEMA (For Type A documents ONLY)
═══════════════════════════════════════════════════════════════════════════════

Use this EXACT 12-column schema for regulatory/compliance documents:
1. # - Sequential row number
2. Regulation - Source document name
3. Chapter - Main chapter/section title
4. Section - Sub-section (use "-" if none)
5. Article - Article code or title (use "-" if just a section description)
6. Article_Description - COMPLETE requirement text
7. Risk - Brief risk summary (derive from content, or "-")
8. Risk_Description - Detailed risk explanation (derive from content, or "-")
9. Compliance_Risk - Category: Regulatory, Operational, Patient Safety, Financial (or "-")
10. Mandate_Control - Required control measure (or "-")
11. Control_Description - How to demonstrate compliance (or "-")
12. Mandate_Control_Category - Control type: Policy, Procedure, Documentation, Training (or "-")

═══════════════════════════════════════════════════════════════════════════════
EXTRACTION RULES (For Regulatory Documents)
═══════════════════════════════════════════════════════════════════════════════

RULE 1: ONE ROW PER LOGICAL UNIT
• Each article, requirement, or distinct section = ONE row
• Don't combine unrelated requirements

RULE 2: PRESERVE HIERARCHY
• Keep Regulation/Chapter/Section consistent for all nested items
• Use "-" for empty hierarchy levels

RULE 3: COMPLETE DESCRIPTIONS
• Include ALL text: statements, rationales, consequences, measurable elements
• Don't summarize - preserve full content

RULE 4: DERIVE RISK FIELDS
• Analyze the requirement and derive what could go wrong
• Categorize appropriately (Regulatory, Operational, etc.)
• If unclear or not applicable, use "-"

RULE 5: SMART CONTROL DERIVATION
• Based on the requirement, suggest appropriate controls
• Or use "-" if not obvious

═══════════════════════════════════════════════════════════════════════════════
EXAMPLES BY DOCUMENT TYPE
═══════════════════════════════════════════════════════════════════════════════

EXAMPLE A: FINANCIAL/BANKING REGULATIONS
Document: "Instructions on Advertising Controls for Products, Services, and Prizes Offered by Financial and Banking Service Providers"

OUTPUT:
#,Regulation,Chapter,Section,Article,Article_Description,Risk,Risk_Description,Compliance_Risk,Mandate_Control,Control_Description,Mandate_Control_Category
1,"Instructions on Advertising Controls for Products, Services, and Prizes Offered by Financial and Banking Service Providers","Scope of Application","-","-","Applies to all licensed banks, finance companies, payment and electronic money transfer companies, exchange companies, and insurance companies, effective 30 days from issuance.","-","-","-","-","-","-"
2,"Instructions on Advertising Controls for Products, Services, and Prizes Offered by Financial and Banking Service Providers","Definitions","-","-","Definitions for terms such as Service Provider, Product/Service, Client, Advertisement Types (Direct, Indirect, Readable, Audible, Electronic).","-","-","-","-","-","-"
3,"Instructions on Advertising Controls for Products, Services, and Prizes Offered by Financial and Banking Service Providers","Advertising Requirements","-","-","Advertisements must include specific information such as name, fees, features, inquiry methods, and target audience. Must be clear, accurate, and not misleading.","Misleading advertisements","Failure to provide clear and accurate information may mislead clients and violate transparency principles.","Regulatory","Develop clear advertising policies","Ensure all advertisements meet the specified requirements and are reviewed for compliance.","Policy"
4,"Instructions on Advertising Controls for Products, Services, and Prizes Offered by Financial and Banking Service Providers","Prohibited Practices","-","-","Prohibits misleading promises, unauthorized use of logos, and deceptive advertising practices.","Deceptive advertising","Using misleading or unauthorized content can lead to regulatory penalties and loss of consumer trust.","Regulatory","Implement strict review processes","Verify all advertising content for compliance with regulations and authenticity.","Procedure"
5,"Instructions on Advertising Controls for Products, Services, and Prizes Offered by Financial and Banking Service Providers","Penalties and Fines","-","-","Central Bank may impose penalties for non-compliance with these instructions.","Regulatory penalties","Non-compliance can result in fines and other regulatory actions.","Regulatory","Ensure compliance with all instructions","Regularly review compliance with advertising instructions to avoid penalties.","Procedure"

---

EXAMPLE B: HEALTHCARE ACCREDITATION (JCI)
Document: "JCI-Hospital 8th Edition Standards Manual"

OUTPUT:
#,Regulation,Chapter,Section,Article,Article_Description,Risk,Risk_Description,Compliance_Risk,Mandate_Control,Control_Description,Mandate_Control_Category
1,"JCI-Hospital 8th Edition Standards Manual","Accreditation Participation Requirements (APR)","Overview","-","This section consists of specific requirements for participation in the Joint Commission International (JCI) accreditation process and for maintaining an accreditation award. For a hospital seeking accreditation for the first time, compliance with many of the APRs is assessed during the initial survey.","-","-","-","-","-","-"
2,"JCI-Hospital 8th Edition Standards Manual","Accreditation Participation Requirements (APR)","Requirements, Rationales, and Measurable Elements","APR.01.00","The hospital submits information to Joint Commission International (JCI) as required. Rationale for APR.01.00: There are many points in the accreditation process at which data and information are required. Consequences of Noncompliance: If the hospital consistently fails to meet the requirements, the hospital will be required to undergo a follow-up survey. Measurable Elements: 1. The hospital meets all requirements for timely submissions of data and information to JCI.","Late data submission","Failure to meet timely submission requirements could result in follow-up survey and accreditation decision change.","Regulatory","Establish submission tracking system","Document all JCI submissions with dates and confirmations.","Procedure"
3,"JCI-Hospital 8th Edition Standards Manual","Section II: Patient-Centered Standards","Admission to the Hospital","ACC.01.00","Patients admitted to the hospital are screened to identify if their health care needs match the hospital's mission, scope of care, and resources. Intent: Matching patient needs with hospital capabilities through screening. Measurable Elements: 1. Screening results determine patient admission. 2. Patients outside scope are stabilized prior to transfer.","Patient-hospital mismatch","Failure to properly screen patients could result in inappropriate admissions or unsafe transfers.","Operational","Implement admission screening protocol","Develop criteria for patient screening at all entry points.","Procedure"

---

EXAMPLE C: INVOICE/BUSINESS DOCUMENT (Non-regulatory - Use appropriate columns)
Document: Invoice

OUTPUT:
Invoice_Number,Date,Vendor,Item,Description,Quantity,Unit_Price,Total,Tax,Grand_Total
"INV-2024-001","2024-01-15","ABC Supplies Inc","PROD-001","Office Paper A4",10,25.00,250.00,25.00,275.00
"INV-2024-001","2024-01-15","ABC Supplies Inc","PROD-002","Printer Ink Black",5,45.00,225.00,22.50,247.50

{custom_instructions}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT: {output_format}
═══════════════════════════════════════════════════════════════════════════════

{format_instructions}

CRITICAL: Output ONLY the {output_format} data. No explanations, no markdown code blocks."""

    CSV_FORMAT_INSTRUCTIONS = """CSV Requirements:
- For REGULATORY documents use: #,Regulation,Chapter,Section,Article,Article_Description,Risk,Risk_Description,Compliance_Risk,Mandate_Control,Control_Description,Mandate_Control_Category
- For OTHER documents: Use appropriate columns based on document content
- Use double quotes around ALL text fields
- Preserve full text in descriptions
- Empty/unknown fields: Use "-" 
- One logical unit per row
- Escape internal quotes with double-quotes ("")"""

    JSON_FORMAT_INSTRUCTIONS = """JSON Requirements:
- For REGULATORY documents use keys: id, regulation, chapter, section, article, article_description, risk, risk_description, compliance_risk, mandate_control, control_description, mandate_control_category
- For OTHER documents: Use appropriate keys based on document content
- Preserve full text in descriptions
- Empty values as "-"
- Properly escape special characters"""

    async def execute(
        self,
        user_message: str,
        context: Dict[str, Any],
        settings: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
    ) -> AgentResult:
        """
        Execute professional document extraction.
        
        Args:
            user_message: Original query
            context: Contains document content to transform
            settings: Extraction settings
            model: Model override
            
        Returns:
            AgentResult with extracted structured data
        """
        settings = settings or {}
        output_format = settings.get("toFormat", "csv").upper()
        custom_columns = settings.get("customColumns", "")
        
        # Get spreadsheet settings if available
        spreadsheet_settings = context.get("spreadsheet_settings", {})
        if not custom_columns and spreadsheet_settings:
            custom_columns = spreadsheet_settings.get("customColumns", "")
        
        # Find content to transform
        content = self._get_content(context)
        
        if not content:
            return AgentResult(
                agent=self.agent_id,
                model="none",
                action="transform",
                content="No content available for extraction.",
                success=False,
                metadata={"error": "No input content"},
            )
        
        print(f"[TRANSFORMER] Content length: {len(content)}")
        print(f"[TRANSFORMER] Output format: {output_format}")
        
        # Build custom instructions
        custom_instructions = ""
        if custom_columns and custom_columns.strip():
            columns = [c.strip() for c in custom_columns.split(",") if c.strip()]
            custom_instructions = f"""
REQUIRED COLUMNS (User Specified):
The extraction MUST include these columns: {', '.join(columns)}
Map document fields to these columns. Add supplementary columns if needed."""
        
        # Get format-specific instructions
        if output_format == "JSON":
            format_instructions = self.JSON_FORMAT_INSTRUCTIONS
        else:
            format_instructions = self.CSV_FORMAT_INSTRUCTIONS
        
        # Add supervisor guidance if available
        supervisor_guidance = context.get("supervisor_guidance", "")
        if supervisor_guidance:
            custom_instructions += f"\n\nADDITIONAL CONTEXT:\n{supervisor_guidance}"
        
        # Build system prompt
        system_prompt = self.SYSTEM_PROMPT.format(
            output_format=output_format,
            format_instructions=format_instructions,
            custom_instructions=custom_instructions,
        )
        
        # Truncate very long documents
        max_length = 30000
        if len(content) > max_length:
            content = content[:max_length] + "\n\n[... Document truncated for processing ...]"
        
        # Build user prompt with clear structure
        user_prompt = f"""Perform audit-grade extraction on the following document.

══════════════════════════════════════════════════════════════════════
DOCUMENT TO EXTRACT
══════════════════════════════════════════════════════════════════════

{content}

══════════════════════════════════════════════════════════════════════
EXTRACTION TASK
══════════════════════════════════════════════════════════════════════

1. Classify this document type
2. Identify the appropriate schema
3. Extract ALL structured data
4. Output as {output_format}

Begin extraction now. Output {output_format} only, no explanations."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        # Use GPT-4o for best extraction quality
        actual_model = model or "gpt-4o"
        
        result = await self._chat(
            messages=messages,
            model=actual_model,
            temperature=0.1,  # Low temperature for consistent extraction
            max_tokens=4096,
        )
        
        # Clean up result
        result = self._clean_output(result)
        
        return AgentResult(
            agent=self.agent_id,
            model=actual_model,
            action="transform",
            content=result,
            metadata={
                "output_format": output_format,
                "input_length": len(content),
                "output_length": len(result),
                "custom_columns": custom_columns or "auto-detected",
            },
            context_updates={
                "transformed_content": result,
                "input_content": result,
                "final_answer": result,
            },
        )
    
    def _get_content(self, context: Dict[str, Any]) -> str:
        """Get content to transform from context, checking multiple sources."""
        sources = [
            "input_content",
            "uploaded_file_content", 
            "final_answer",
        ]
        
        for source in sources:
            content = context.get(source)
            if content and len(content.strip()) > 10:
                print(f"[TRANSFORMER] Using content from: {source}")
                return content
        
        # Check context snippets
        snippets = context.get("context_snippets", [])
        if snippets:
            print(f"[TRANSFORMER] Using content from: context_snippets")
            return "\n\n".join(snippets)
        
        # Last resort: user message
        user_msg = context.get("user_message", "")
        if user_msg:
            print(f"[TRANSFORMER] Using content from: user_message")
            return user_msg
        
        return ""
    
    def _clean_output(self, output: str) -> str:
        """Clean up LLM output, removing markdown and extra formatting."""
        output = output.strip()
        
        # Remove markdown code blocks
        if output.startswith("```"):
            lines = output.split("\n")
            # Remove first line (```csv or ```json)
            if lines[0].startswith("```"):
                lines = lines[1:]
            # Remove last line if it's closing ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            output = "\n".join(lines)
        
        return output.strip()
