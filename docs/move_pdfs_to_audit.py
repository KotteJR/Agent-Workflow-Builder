#!/usr/bin/env python3
"""
Move all PDF files from nested folders to a single audit folder.
Handles filename conflicts by adding a unique prefix.
"""

import os
import shutil
from pathlib import Path

SOURCE_DIR = Path("/Users/aleksandarkotevski/Projects/workflow-builder-standalone/Jan 1st Regulation Analysis files")
TARGET_DIR = Path("/Users/aleksandarkotevski/Projects/workflow-builder-standalone/backend/documents/audit")

def move_pdfs():
    """Move all PDFs to audit folder."""
    # Create target directory
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    
    # Find all PDFs
    pdf_files = list(SOURCE_DIR.rglob("*.pdf"))
    
    print(f"Found {len(pdf_files)} PDF files")
    print(f"Moving to: {TARGET_DIR}")
    print("-" * 50)
    
    moved_count = 0
    skipped_count = 0
    conflict_count = 0
    
    for pdf_path in pdf_files:
        # Get original filename
        original_name = pdf_path.name
        
        # Create target path
        target_path = TARGET_DIR / original_name
        
        # Handle conflicts
        if target_path.exists():
            # Add parent folder name as prefix to avoid conflicts
            parent_name = pdf_path.parent.name
            # Clean parent name (remove special chars)
            clean_parent = "".join(c for c in parent_name if c.isalnum() or c in (' ', '-', '_')).strip()
            clean_parent = clean_parent.replace(' ', '_')
            
            # Create unique name
            stem = pdf_path.stem
            suffix = pdf_path.suffix
            target_path = TARGET_DIR / f"{clean_parent}_{stem}{suffix}"
            
            # If still exists, add number
            counter = 1
            while target_path.exists():
                target_path = TARGET_DIR / f"{clean_parent}_{stem}_{counter}{suffix}"
                counter += 1
            
            conflict_count += 1
        
        try:
            # Move file
            shutil.move(str(pdf_path), str(target_path))
            moved_count += 1
            
            if moved_count % 100 == 0:
                print(f"  Moved {moved_count} files...")
        except Exception as e:
            print(f"  Error moving {pdf_path.name}: {e}")
            skipped_count += 1
    
    print("-" * 50)
    print(f"✓ Moved: {moved_count}")
    print(f"✗ Skipped: {skipped_count}")
    print(f"⚠ Conflicts resolved: {conflict_count}")
    print(f"\nAll PDFs are now in: {TARGET_DIR}")

if __name__ == "__main__":
    move_pdfs()

