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
    
    SYSTEM_PROMPT = """You are an Expert GRC (Governance, Risk, and Compliance) Analyst specializing in regulatory document extraction and risk assessment. You extract structured compliance data from regulatory documents with professional risk analysis.

═══════════════════════════════════════════════════════════════════════════════
DOCUMENT TYPES YOU HANDLE
═══════════════════════════════════════════════════════════════════════════════

TYPE A - HEALTHCARE ACCREDITATION STANDARDS (JCI, JCIA, CBAHI, Joint Commission):
→ Use the HEALTHCARE REGULATORY SCHEMA with full risk analysis

TYPE B - FINANCIAL/BANKING REGULATIONS:
→ Use the REGULATORY SCHEMA with appropriate risk categories

TYPE C - OTHER REGULATORY/COMPLIANCE DOCUMENTS:
→ Use the REGULATORY SCHEMA adapted to document type

TYPE D - BUSINESS/DATA DOCUMENTS:
→ Use document-appropriate schema

═══════════════════════════════════════════════════════════════════════════════
REGULATORY EXTRACTION SCHEMA (11 COLUMNS) - CONCISE FORMAT
═══════════════════════════════════════════════════════════════════════════════

Extract into this EXACT 11-column schema (NO row numbers, use ABBREVIATIONS):

1. Regulation - ABBREVIATED (e.g., "JCI 8th Ed", "CBAHI 4th Ed", "ISO 27001")
2. Chapter - ABBREVIATED (e.g., "Section II", "Section I", "APR")
3. Section - CODE ONLY (e.g., "ACC", "AOP", "ASC", "COP", "MMU", "PCI", "GLD", "SQE", "MOI", "FMS")
4. Article - Standard code (e.g., "ACC.01.00", "ACC.01.01", "Overview")
5. Article Description - MAX 1 SENTENCE summarizing the key requirement (not full text!)
6. Risk - Brief risk title, max 5 words (or "_")
7. Risk Description - MAX 1 SENTENCE describing consequences (or "_")
8. Compliance Risk Category - Use category codes below
9. Mandated Control - Control title, max 5 words (or "_")
10. Control Description - MAX 1 SENTENCE on implementation (or "_")
11. Mandated Control Category - Use control codes below

CRITICAL: Keep descriptions SHORT! This allows processing the ENTIRE document.

ABBREVIATION EXAMPLES:
• "JOINT COMMISSION INTERNATIONAL ACCREDITATION STANDARDS FOR HOSPITALS, 8TH EDITION" → "JCI 8th Ed"
• "Access to Care and Continuity of Care (ACC)" → "ACC"
• "Section II: Patient-Centered Standards" → "Section II"
• Long article description → 1 sentence summary of requirement

═══════════════════════════════════════════════════════════════════════════════
COMPLIANCE RISK CATEGORIES (Use EXACTLY these)
═══════════════════════════════════════════════════════════════════════════════

Choose the MOST appropriate category for each risk:

• Regulatory & Licensing Compliance - Risks related to accreditation, licensing, regulatory reporting, government compliance
• Operational Compliance Risks - Risks in clinical operations, patient flow, care delivery processes, procedures
• Employment & Labor Compliance Risks - Staff qualifications, training, competency, labor law compliance
• Third-Party & Vendor Compliance Risks - Contracted services, external providers, vendor management
• Product & Service Compliance Risks - Quality of care/services delivered, patient outcomes, service standards
• Conduct, Ethics, and Conflicts Risks - Staff behavior, ethical issues, conflicts of interest, retaliation
• ESG, Health and Safety Compliance - Environmental, health & safety, workplace safety, hazardous materials
• Data Protection & Confidentiality - Patient records, privacy, data security, information management
• Compliance Governance & Framework - Policies, documentation, governance structure, oversight

═══════════════════════════════════════════════════════════════════════════════
MANDATED CONTROL CATEGORIES (Use EXACTLY these)
═══════════════════════════════════════════════════════════════════════════════

Choose the MOST appropriate control type:

• Governance & Documentation Controls - Policies, procedures, written guidelines, documentation requirements
• System/GRC Controls - Technology systems, tracking systems, automated controls, GRC software
• Third Party and Vendor Due Diligence - Vendor vetting, contract management, external service oversight
• Employment and Labor Qualifications Controls - Hiring criteria, credentialing, qualification verification
• ESG/Health & Safety Controls - Safety programs, environmental controls, protective equipment
• Training & Awareness Controls - Education programs, competency training, awareness initiatives
• Monitoring and Testing Controls - Audits, inspections, surveillance, quality monitoring
• Recordkeeping & Evidence Controls - Documentation, record retention, evidence preservation
• Operational Continuity Controls - Business continuity, emergency preparedness, service availability

═══════════════════════════════════════════════════════════════════════════════
RISK DERIVATION RULES FOR JCI/HEALTHCARE STANDARDS
═══════════════════════════════════════════════════════════════════════════════

WHEN TO DERIVE RISKS:
1. Look for "Consequences of Noncompliance" - this tells you what happens if standard is not met
2. Look for "Rationale" - this explains WHY the standard matters (derive risk from this)
3. Look for "Measurable Elements" - requirements that if not met = compliance risk
4. Look for keywords: "must", "required", "shall", "ensure", "verify", "document"

HOW TO DERIVE RISKS:
• If standard mentions patient safety → Risk relates to patient harm
• If standard mentions staff qualifications → Risk relates to unqualified personnel
• If standard mentions documentation → Risk relates to incomplete records
• If standard mentions reporting → Risk relates to non-compliance with reporting requirements
• If standard mentions equipment → Risk relates to equipment failure/safety
• If standard mentions infection → Risk relates to infection control failures
• If standard mentions transfer/discharge → Risk relates to continuity of care gaps

WHEN TO LEAVE RISK FIELDS EMPTY ("_"):
• Overview sections that are purely descriptive
• Lists of standards without specific requirements
• Introductory/explanatory text without compliance implications
• Section headers or navigation content

═══════════════════════════════════════════════════════════════════════════════
EXTRACTION RULES
═══════════════════════════════════════════════════════════════════════════════

RULE 1: ONE ROW PER LOGICAL UNIT
• Each Standard (e.g., APR.01.00, ACC.01.00) = ONE row
• Overview/Introduction sections = ONE row each
• If a standard has MULTIPLE distinct risks, you MAY create multiple rows for the same standard

RULE 2: PRESERVE DOCUMENT HIERARCHY
• Regulation = Always the full document name
• Chapter = Main section (e.g., "Accreditation Participation Requirements (APR)")  
• Section = Sub-section within chapter (e.g., "Admission to the Hospital")
• Article = Specific standard code or descriptive title

RULE 3: COMPLETE ARTICLE DESCRIPTIONS
• Include Intent/Rationale text
• Include Consequences of Noncompliance
• Include ALL Measurable Elements
• Preserve formatting with proper punctuation
• Use quotes for multi-line content

RULE 4: SMART RISK ANALYSIS
• Read the requirement carefully
• Identify what could go wrong if not followed
• Categorize using the EXACT categories provided
• Suggest practical controls

RULE 5: USE UNDERSCORE FOR EMPTY VALUES
• Use "_" (underscore) for empty/not-applicable fields
• Leave Compliance Risk Category and Mandated Control Category empty (no underscore) if not applicable

═══════════════════════════════════════════════════════════════════════════════
JCI HOSPITAL STANDARDS - SPECIFIC GUIDANCE
═══════════════════════════════════════════════════════════════════════════════

For JCI Hospital 8th Edition Standards Manual:

DOCUMENT STRUCTURE - SECTION I vs SECTION II:

ITS VERY IMPORTANT THAT YOU SPLIT THE INFO INTO ITS UNIQUE ROWS!!! DONT MISS ANYTHING!!! AND YOU ARE ALLOWED TO MAKE AS MANY ROWS AS YOU NEED!!!!!!!!

**SECTION I: Accreditation Participation Requirements**
Use this hierarchy:
- Chapter: "Accreditation Participation Requirements (APR)"
- Section: "Accreditation Participation Requirements (APR)" (same as chapter for consistency)
- Article: "Overview", "Introduction", "Requirements - APR.01.00", "Requirements - APR.02.00", etc.

**SECTION II: Patient-Centered Standards**  
Use this hierarchy:
- Chapter: "Section II: Patient-Centered Standards"
- Section: The specific chapter like "Access to Care and Continuity of Care (ACC)", "Assessment of Patients (AOP)", etc.
- Article: "Overview", "Standards", "Admission to the Hospital - Standard ACC.01.00", etc.


CHAPTERS TO RECOGNIZE:
• Accreditation Participation Requirements (APR) - APR.01.00 through APR.11.00
• International Patient Safety Goals (IPSG) - IPSG.01.00 through IPSG.06.00
• Access to Care and Continuity of Care (ACC) - ACC.01.00 through ACC.06.00
• Assessment of Patients (AOP) - AOP.01.00 through AOP.06.00
• Anesthesia and Surgical Care (ASC) - ASC.01.00 through ASC.04.04
• Care of Patients (COP)
• Medication Management and Use (MMU)
• Patient and Family Education (PFE)
• Patient-Centered Care (PCC)
• Quality Improvement and Patient Safety (QPS)
• Prevention and Control of Infections (PCI)
• Governance, Leadership, and Direction (GLD)
• Facility Management and Safety (FMS)
• Staff Qualifications and Education (SQE)
• Management of Information (MOI)
• Health Care Technology (HCT)

TYPICAL RISK PATTERNS:
• APR standards → Regulatory & Licensing Compliance risks (accreditation, reporting, surveys)
• IPSG standards → Patient Safety risks, Operational Compliance Risks
• ACC standards → Operational Compliance Risks (patient flow, admission, discharge, transfer)
• AOP standards → Operational Compliance Risks (assessment quality, laboratory, radiology)
• ASC standards → Operational + Employment risks (qualified staff, surgical procedures)
• COP standards → Product & Service Compliance Risks (care quality)
• MMU standards → Operational Compliance Risks (medication safety)
• Staff-related → Employment & Labor Compliance Risks
• Contracted services → Third-Party & Vendor Compliance Risks
• Patient rights/consent → Product & Service Compliance Risks
• Reporting to JCI → Conduct, Ethics, and Conflicts Risks
• Safety/environment → ESG, Health and Safety Compliance
• Medical records → Data Protection & Confidentiality
• Policies/procedures → Compliance Governance & Framework

═══════════════════════════════════════════════════════════════════════════════
EXAMPLE OUTPUT - CONCISE FORMAT (MANDATORY)
═══════════════════════════════════════════════════════════════════════════════

NOTICE: Use ABBREVIATED names and SHORT descriptions to maximize row count!

Regulation,Chapter,Section,Article,Article Description,Risk,Risk Description,Compliance Risk Category,Mandated Control,Control Description,Mandated Control Category
"JCI 8th Ed","Section I","APR","Overview","Requirements for JCI accreditation participation and maintaining award.","_","_","","_","_",""
"JCI 8th Ed","Section I","APR","APR.01.00","Hospital must submit required information to JCI on time.","Late data submission","May trigger follow-up survey.","Regulatory & Licensing Compliance","Submission tracking","Track all JCI submission deadlines.","System/GRC Controls"
"JCI 8th Ed","Section I","APR","APR.04.00","Hospital must permit JCI surveys at their discretion.","Survey access denial","Immediate denial of accreditation.","Regulatory & Licensing Compliance","Survey access policy","Ensure unrestricted surveyor access.","Governance & Documentation Controls"
"JCI 8th Ed","Section I","APR","APR.08.00","Staff can report safety concerns to JCI without retaliation.","Staff retaliation","Denial of accreditation.","Conduct, Ethics, and Conflicts Risks","Non-retaliation policy","Communicate no-retaliation policy.","Governance & Documentation Controls"
"JCI 8th Ed","Section II","ACC","Overview","Integrated care approach matching patient needs to services.","_","_","","_","_",""
"JCI 8th Ed","Section II","ACC","ACC.01.00","Screen patients to match needs with hospital resources.","Patient-resource mismatch","Inappropriate admissions or unsafe transfers.","Operational Compliance Risks","Admission screening","Criteria for patient screening at entry.","Governance & Documentation Controls"
"JCI 8th Ed","Section II","ACC","ACC.01.01","Prioritize emergent/urgent patients using triage process.","Delayed urgent care","Patient deterioration.","Operational Compliance Risks","Triage implementation","Use evidence-based triage process.","Governance & Documentation Controls"
"JCI 8th Ed","Section II","ACC","ACC.01.02","Inform patients of unusual delays for services.","Uninformed delays","Patient dissatisfaction and harm.","Operational Compliance Risks","Delay notification","Protocol for communicating delays.","Governance & Documentation Controls"
"JCI 8th Ed","Section II","ACC","ACC.02.00","Manage patient flow from admission to discharge.","Flow bottlenecks","Overcrowding and delayed care.","Operational Compliance Risks","Flow management","System to monitor patient flow.","System/GRC Controls"
"JCI 8th Ed","Section II","ACC","ACC.02.01","Educate patient/family on care area, costs, and outcomes.","Uninformed patients","Confusion and dissatisfaction.","Operational Compliance Risks","Patient education","Comprehensive education program.","Training & Awareness Controls"
"JCI 8th Ed","Section II","ACC","ACC.02.02","Establish criteria for specialized unit admission/discharge.","Inappropriate unit use","Resource misuse.","Operational Compliance Risks","Unit criteria","Written admission/discharge criteria.","Governance & Documentation Controls"
"JCI 8th Ed","Section II","ACC","ACC.03.00","Provide continuous care coordination among providers.","Care coordination gaps","Fragmented care.","Operational Compliance Risks","Coordination protocol","Seamless coordination across settings.","Governance & Documentation Controls"
"JCI 8th Ed","Section II","ACC","ACC.03.01","Assign qualified individual responsible for patient care.","Unclear responsibility","Gaps in care.","Operational Compliance Risks","Care coordinator","Assign designated care coordinator.","Governance & Documentation Controls"
"JCI 8th Ed","Section II","ACC","ACC.04.00","Implement discharge planning based on patient readiness.","Inadequate discharge","Readmissions and harm.","Operational Compliance Risks","Discharge planning","Structured discharge process.","Governance & Documentation Controls"
"JCI 8th Ed","Section II","ACC","ACC.04.01","Educate patient/family on continuing care needs at discharge.","Poor discharge education","Non-compliance with instructions.","Operational Compliance Risks","Discharge education","Comprehensive education program.","Training & Awareness Controls"
"JCI 8th Ed","Section II","ACC","ACC.04.02","Prepare complete discharge summary for all patients.","Incomplete summary","Follow-up care gaps.","Operational Compliance Risks","Summary protocol","Complete accurate summaries.","Recordkeeping & Evidence Controls"
"JCI 8th Ed","Section II","ACC","ACC.04.03","Document emergency care including arrival/departure times.","Missing ED documentation","Continuity issues.","Operational Compliance Risks","ED documentation","Comprehensive ED record system.","Recordkeeping & Evidence Controls"
"JCI 8th Ed","Section II","ACC","ACC.04.04","Medical records contain patient profiles.","Incomplete profiles","Care errors.","Operational Compliance Risks","Profile management","Standardized patient profiles.","Recordkeeping & Evidence Controls"
"JCI 8th Ed","Section II","ACC","ACC.04.05","Process for patients leaving against medical advice.","AMA patients","Health risks and legal issues.","Operational Compliance Risks","AMA process","Document AMA cases properly.","Governance & Documentation Controls"
"JCI 8th Ed","Section II","ACC","ACC.05.00","Transfer patients based on needs and hospital capability.","Unsafe transfers","Continuity gaps.","Operational Compliance Risks","Transfer process","Written transfer protocols.","Governance & Documentation Controls"
"JCI 8th Ed","Section II","ACC","ACC.05.01","Provide written summary to receiving organization.","Missing transfer info","Care gaps at receiving facility.","Operational Compliance Risks","Transfer summary","Provide clinical summary with patient.","Recordkeeping & Evidence Controls"
"JCI 8th Ed","Section II","ACC","ACC.06.00","Transportation services meet laws and quality requirements.","Unsafe transport","Patient harm during transport.","ESG, Health and Safety Compliance","Transport safety","Compliant transport services.","ESG/Health & Safety Controls"


These are additional instructions that you should keep in mind:
{custom_instructions}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT: {output_format}
═══════════════════════════════════════════════════════════════════════════════

These are the format instructions that you should follow:
{format_instructions}

CRITICAL RULES FOR MAXIMUM ROW OUTPUT:
1. Output ONLY the {output_format} data - no explanations, no markdown code blocks
2. Use "_" for empty Risk, Risk Description, Mandated Control, Control Description fields
3. Leave Compliance Risk Category and Mandated Control Category empty (blank) if not applicable
4. Use double quotes around ALL text fields
5. Escape internal quotes with double-quotes ("")
6. KEEP DESCRIPTIONS SHORT (1 sentence max) - this is CRITICAL for processing the entire document
7. Use ABBREVIATED names (JCI 8th Ed, ACC, Section II, etc.)
8. NO row numbers (#) column - start directly with Regulation
9. Extract EVERY standard/article from the ENTIRE document - do not stop early!"""

    CSV_FORMAT_INSTRUCTIONS = """CSV Requirements:
- Header: Regulation,Chapter,Section,Article,Article Description,Risk,Risk Description,Compliance Risk Category,Mandated Control,Control Description,Mandated Control Category
- NO row number (#) column!
- Article Description: MAX 1 SENTENCE (key requirement only)
- Risk Description: MAX 1 SENTENCE (key consequence only)  
- Control Description: MAX 1 SENTENCE (implementation summary)
- Use ABBREVIATED names: "JCI 8th Ed", "ACC", "Section II"
- Empty Risk/Control: "_"
- Empty Category: leave blank
- Double quotes around text fields
- EXTRACT ALL STANDARDS from entire document!"""

    JSON_FORMAT_INSTRUCTIONS = """JSON Requirements:
- Array of objects with keys: regulation, chapter, section, article, article_description, risk, risk_description, compliance_risk_category, mandated_control, control_description, mandated_control_category
- NO id/row number field!
- Article Description: MAX 1 SENTENCE
- Risk Description: MAX 1 SENTENCE
- Control Description: MAX 1 SENTENCE
- Use ABBREVIATED names
- Empty Risk/Control: "_"
- Empty Category: "" or null"""

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
        # EXCEL format uses CSV output (converted to Excel by spreadsheet node)
        if output_format == "JSON":
            format_instructions = self.JSON_FORMAT_INSTRUCTIONS
            actual_output_format = "JSON"
        else:
            format_instructions = self.CSV_FORMAT_INSTRUCTIONS
            actual_output_format = "CSV"
        
        # Add supervisor guidance if available
        supervisor_guidance = context.get("supervisor_guidance", "")
        if supervisor_guidance:
            custom_instructions += f"\n\nADDITIONAL CONTEXT:\n{supervisor_guidance}"
        
        # Build system prompt
        system_prompt = self.SYSTEM_PROMPT.format(
            output_format=actual_output_format,
            format_instructions=format_instructions,
            custom_instructions=custom_instructions,
        )
        
        # Truncate very long documents to avoid API timeouts
        # 80K chars is roughly 20K tokens - GPT-4o has 128K context window
        # With concise output format, we can process much more content
        max_length = 80000
        if len(content) > max_length:
            print(f"[TRANSFORMER] Document truncated from {len(content)} to {max_length} chars")
            content = content[:max_length] + "\n\n[... Document truncated for processing. Process remaining content in subsequent runs. ...]"
        
        # Build user prompt with clear structure
        user_prompt = f"""Perform comprehensive GRC extraction on the following regulatory document.

═══════════════════════════════════════════════════════════════════════════════
DOCUMENT TO EXTRACT
═══════════════════════════════════════════════════════════════════════════════

{content}

═══════════════════════════════════════════════════════════════════════════════
EXTRACTION INSTRUCTIONS
═══════════════════════════════════════════════════════════════════════════════

1. Identify document type and structure
2. Extract EACH standard/requirement as a separate row
3. For EACH row, analyze and derive:
   - Risk: What could go wrong if this standard is not met?
   - Risk Description: Detailed explanation of consequences
   - Compliance Risk Category: Select from the defined categories
   - Mandated Control: What control would address this risk?
   - Control Description: How to implement the control
   - Mandated Control Category: Select from the defined categories
4. Preserve COMPLETE Article Description text
5. Output as {actual_output_format}

Begin extraction now. Output {actual_output_format} data only, no explanations."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        # Use GPT-4o for best extraction quality
        actual_model = model or "gpt-4o"
        
        result = await self._chat(
            messages=messages,
            model=actual_model,
            temperature=0.1,
            max_tokens=22000,
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
