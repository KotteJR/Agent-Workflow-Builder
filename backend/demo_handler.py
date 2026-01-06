"""
Demo Handler - Returns premade outputs for specific demo files.

This is a "dirty demo" function that bypasses actual processing
for specific PDFs and returns impressive, pre-built spreadsheet outputs.
"""

from pathlib import Path
from typing import Optional, Tuple

# Demo data directory
DEMO_DATA_DIR = Path(__file__).parent / "demo_data"

# Mapping of demo file names to their premade outputs
# Key: filename (case-insensitive), Value: (output_file, description)
DEMO_FILES = {
    # Add your demo PDFs here
    "invoice_sample.pdf": ("invoice_output.csv", "Invoice data extraction"),
    "contract_sample.pdf": ("contract_output.csv", "Contract clause extraction"),
    "resume_sample.pdf": ("resume_output.csv", "Resume data extraction"),
    "report_sample.pdf": ("report_output.csv", "Report findings extraction"),
    # Add more demo files as needed
}


def check_demo_file(filename: str) -> Optional[Tuple[str, str]]:
    """
    Check if a filename matches a demo file.
    
    Args:
        filename: The uploaded file name
        
    Returns:
        Tuple of (csv_content, description) if demo file, None otherwise
    """
    # Normalize filename for comparison
    filename_lower = filename.lower().strip()
    
    for demo_name, (output_file, description) in DEMO_FILES.items():
        if demo_name.lower() in filename_lower or filename_lower in demo_name.lower():
            output_path = DEMO_DATA_DIR / output_file
            
            if output_path.exists():
                try:
                    content = output_path.read_text(encoding="utf-8")
                    print(f"[DEMO] Matched demo file: {filename} -> {output_file}")
                    return (content, description)
                except Exception as e:
                    print(f"[DEMO] Error reading demo output {output_file}: {e}")
                    return None
            else:
                print(f"[DEMO] Demo output file not found: {output_path}")
                return None
    
    return None


def is_demo_workflow(uploaded_files: list, has_spreadsheet_output: bool) -> Optional[str]:
    """
    Check if this workflow should use demo mode.
    
    Args:
        uploaded_files: List of uploaded file info dicts
        has_spreadsheet_output: Whether workflow has spreadsheet output node
        
    Returns:
        CSV content if demo mode should be used, None otherwise
    """
    if not has_spreadsheet_output:
        return None
    
    if not uploaded_files:
        return None
    
    # Check each uploaded file
    for file_info in uploaded_files:
        filename = file_info.get("name", "")
        result = check_demo_file(filename)
        if result:
            content, description = result
            return content
    
    return None


def get_demo_file_list() -> list:
    """Get list of available demo files."""
    return list(DEMO_FILES.keys())

