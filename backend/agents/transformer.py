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
REGULATORY EXTRACTION SCHEMA (12 COLUMNS)
═══════════════════════════════════════════════════════════════════════════════

Extract into this EXACT 12-column schema:

1. # - Sequential row number (1, 2, 3...)
2. Regulation - Full document name (e.g., "JCI-Hospital 8th Edition Standards Manual")
3. Chapter - Main chapter name (e.g., "Accreditation Participation Requirements (APR)", "Section II: Patient-Centered Standards")
4. Section - Sub-section name (e.g., "Access to Care and Continuity of Care (ACC)", "Anesthesia and Surgical Care (ASC)")
5. Article - Standard/Article code or title (e.g., "APR.01.00", "ACC.01.00", "Overview", "Introduction", "Standards")
6. Article Description - COMPLETE text including Intent, Rationale, Consequences, Measurable Elements - preserve ALL content
7. Risk - Brief risk title derived from content (or "_" if none applicable)
8. Risk Description - Detailed explanation of what could go wrong and consequences (or "_" if none)
9. Compliance Risk Category - One of the DEFINED CATEGORIES below (or empty if not applicable)
10. Mandated Control - Suggested control measure title (or "_" if none obvious)
11. Control Description - How to implement the control (or "_" if none)
12. Mandated Control Category - One of the DEFINED CONTROL CATEGORIES below (or empty if not applicable)

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
EXAMPLE OUTPUT - SECTION I: ACCREDITATION PARTICIPATION REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════

For Section I documents, use this structure:
- Chapter: "Accreditation Participation Requirements (APR)"
- Section: "Accreditation Participation Requirements (APR)"
- Article: "Overview", "Introduction", "Requirements - APR.01.00", etc.

#,Regulation,Chapter,Section,Article,Article Description,Risk,Risk Description,Compliance Risk Category,Mandated Control,Control Description,Mandated Control Category
1,"JCI-Hospital 8th Edition Standards Manual","Accreditation Participation Requirements (APR)","Accreditation Participation Requirements (APR)","Overview","This section consists of specific requirements for participation in the Joint Commission International (JCI) accreditation process...","_","_",,,"_","_",
2,"JCI-Hospital 8th Edition Standards Manual","Accreditation Participation Requirements (APR)","Accreditation Participation Requirements (APR)","Introduction","The following is a list of all accreditation participation requirements. JCI reserves the right to update its APRs...","_","_",,,"_","_",
3,"JCI-Hospital 8th Edition Standards Manual","Accreditation Participation Requirements (APR)","Accreditation Participation Requirements (APR)","Requirements - APR.01.00","The hospital submits information to JCI as required. Rationale: There are many points in the accreditation process at which data and information are required... Consequences of Noncompliance: If the hospital consistently fails to meet the requirements for timely submission, the hospital will be required to undergo a follow-up survey. Measurable Elements: 1. The hospital meets all requirements for timely submissions of data and information to JCI.","Do not meet the submission date of Data to JCI","Failure to meet timely submission requirements could result in follow-up survey and accreditation decision change.","Regulatory & Licensing Compliance","_","_",
4,"JCI-Hospital 8th Edition Standards Manual","Accreditation Participation Requirements (APR)","Accreditation Participation Requirements (APR)","Requirements - APR.04.00","The hospital permits the performance of a survey at JCI's discretion. Rationale: JCI has the right to enter all or any portion of the hospital on an announced or unannounced basis... Consequences of Noncompliance: JCI will deny or withdraw accreditation of a hospital that refuses or limits access. Measurable Elements: 1. The hospital permits evaluations at the discretion of JCI.","Refusal of JCI survey access","Refusing or limiting access to JCI staff will lead to immediate denial of accreditation.","Regulatory & Licensing Compliance","Survey Access Policy","Hospital must have policy ensuring JCI surveyors have unrestricted access to all areas.","Governance & Documentation Controls"
5,"JCI-Hospital 8th Edition Standards Manual","Accreditation Participation Requirements (APR)","Accreditation Participation Requirements (APR)","Requirements - APR.08.00","Any staff member can report concerns about patient safety to JCI without retaliatory action. Rationale: To create a safe reporting environment... Consequences of Noncompliance: Confirmed reports of retaliatory actions may cause Denial of Accreditation. Measurable Elements: 1. Hospital educates staff. 2. Hospital informs staff of no retaliation policy. 3. Hospital takes no disciplinary action.","Retaliation against staff reporting to JCI","Staff fear of retaliation could result in underreporting of safety issues, leading to patient harm.","Conduct, Ethics, and Conflicts Risks","Non-retaliation Policy","Implement and communicate a non-retaliation policy for JCI reporting.","Governance & Documentation Controls"
6,"JCI-Hospital 8th Edition Standards Manual","Accreditation Participation Requirements (APR)","Accreditation Participation Requirements (APR)","Requirements - APR.11.00","The hospital provides care and environment that pose no risk of Immediate Threat to Health or Safety. Rationale: Patients, staff, and the public trust hospitals to be safe places. Consequences of Noncompliance: Immediate threats interrupt the survey and place hospital in Preliminary Denial of Accreditation. Measurable Elements: 1. Hospital provides care and environment posing no immediate threat.","Immediate Threat to Health or Safety","Hazardous conditions may result in patient harm, legal consequences, and accreditation denial.","ESG, Health and Safety Compliance","Safety Monitoring Program","Ongoing review and supervision of safety practices throughout the hospital.","ESG/Health & Safety Controls"

═══════════════════════════════════════════════════════════════════════════════
EXAMPLE OUTPUT - SECTION II: PATIENT-CENTERED STANDARDS
═══════════════════════════════════════════════════════════════════════════════

For Section II documents, use this structure:
- Chapter: "Section II: Patient-Centered Standards"
- Section: Specific chapter like "Access to Care and Continuity of Care (ACC)"
- Article: "Overview", "Standards", "Admission to the Hospital - Standard ACC.01.00", etc.

#,Regulation,Chapter,Section,Article,Article Description,Risk,Risk Description,Compliance Risk Category,Mandated Control,Control Description,Mandated Control Category
1,"JCI-Hospital 8th Edition Standards Manual","Section II: Patient-Centered Standards","Access to Care and Continuity of Care (ACC)","Overview","Health care organizations are pursuing a more comprehensive and integrated approach toward delivering health care...","_","_",,,"_","_",
2,"JCI-Hospital 8th Edition Standards Manual","Section II: Patient-Centered Standards","Access to Care and Continuity of Care (ACC)","Admission to the Hospital - Standard ACC.01.00","Patients admitted to the hospital are screened to identify if their health care needs match the hospital's mission, scope of care, and resources. Intent: Matching patient needs with hospital capabilities. Measurable Elements: 1. Screening results determine admission. 2. Patients outside scope are stabilized prior to transfer.","Misalignment of patient needs with hospital resources","Failure to properly screen patients could result in inappropriate admissions or unsafe transfers.","Operational Compliance Risks","Admission Screening Protocol","Develop criteria for patient screening at all entry points.","Governance & Documentation Controls"
3,"JCI-Hospital 8th Edition Standards Manual","Section II: Patient-Centered Standards","Access to Care and Continuity of Care (ACC)","Patient Flow - ACC.02.02","The hospital establishes criteria for admission to and discharge from specialized units. Intent: Ensure appropriate level of care and efficient use of limited resources. Measurable Elements: 1-4. Written admission and discharge criteria, documented in medical records.","Admission/Discharge Without Established Criteria","Inconsistent criteria may lead to inefficient resource use and compromised patient care.","Operational Compliance Risks","Standardized Admission and Discharge Criteria","Establish written admission and discharge criteria for specialized units.","Governance & Documentation Controls"
4, etc... etc...

═══════════════════════════════════════════════════════════════════════════════
EXAMPLE - MULTIPLE RISKS FROM SAME STANDARD
═══════════════════════════════════════════════════════════════════════════════

When a standard has multiple distinct risks, create multiple rows:

63,"JCI-Hospital 8th Edition Standards Manual","Section II: Patient-Centered Standards","Assessment of Patients (AOP)","Nuclear Medicine Services - AOP.06.00","When applicable, the hospital establishes and implements a nuclear medicine safety program that complies with applicable professional standards, laws, and regulations...","Unqualified personnel handling nuclear medicine","Failure to ensure that staff involved in nuclear medicine are properly trained, qualified, and certified to perform their respective roles.","Employment & Labor Compliance Risks","Qualified and certified personnel required","A qualified individual(s) is responsible for overseeing nuclear medicine services, and relevant staff members are properly trained, qualified, and certified to perform their respective roles in nuclear medicine safety and procedures.","Employment and Labor Qualifications Controls"
,"","","","","","Missing radiation safety requirements","Failure to provide shielding materials, ventilation systems, monitoring equipment, and radiation shielding barriers to ensure safety.","Employment & Labor Compliance Risks","Radiation safety requirements","Proper ventilation systems, monitoring equipment, and radiation shielding barriers are required to ensure safety.","ESG/Health & Safety Controls"


These are additional instructions that you should keep in mind:
{custom_instructions}

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT: {output_format}
═══════════════════════════════════════════════════════════════════════════════

These are the format instructions that you should follow:
{format_instructions}

CRITICAL RULES:
These are the critical rules that you should follow:
1. Output ONLY the {output_format} data - no explanations, no markdown code blocks
2. Use "_" (underscore) for empty Risk, Risk Description, Mandated Control, Control Description fields
3. Leave Compliance Risk Category and Mandated Control Category empty (blank) if not applicable
4. Use double quotes around ALL text fields containing commas or special characters
5. Escape internal quotes with double-quotes ("")
6. Preserve COMPLETE Article Description text - do not summarize"""

    CSV_FORMAT_INSTRUCTIONS = """CSV Requirements:
- Header row: #,Regulation,Chapter,Section,Article,Article Description,Risk,Risk Description,Compliance Risk Category,Mandated Control,Control Description,Mandated Control Category
- Use double quotes around ALL text fields
- Preserve full text in descriptions - do NOT summarize
- Empty Risk/Control fields: Use "_"
- Empty Category fields: Leave blank (empty)
- One logical unit per row (except when standard has multiple distinct risks)
- Escape internal quotes with double-quotes ("")
- Tab-separated values are also acceptable if CSV causes issues"""

    JSON_FORMAT_INSTRUCTIONS = """JSON Requirements:
- Array of objects with keys: id, regulation, chapter, section, article, article_description, risk, risk_description, compliance_risk_category, mandated_control, control_description, mandated_control_category
- Preserve full text in descriptions
- Empty Risk/Control values: "_"
- Empty Category values: null or ""
- Properly escape special characters and newlines"""

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
        # 35K chars is roughly 8-10K tokens, leaving room for prompt and response
        max_length = 35000
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
            temperature=0.1,  # Low temperature for consistent extraction
            max_tokens=8192,  # Increased for comprehensive output
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
