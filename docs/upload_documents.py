#!/usr/bin/env python3
"""
Document Upload Script

Reads documents from a folder and uploads them to the pgvector database.

Usage:
    python upload_documents.py --folder /Users/aleksandarkotevski/Projects/workflow-builder-standalone/backend/documents --kb legal --url agent-workflow-builder-production.up.railway.app
    
Or generate curl commands:
    python upload_documents.py --folder /Users/aleksandarkotevski/Projects/workflow-builder-standalone/backend/documents --kb legal --curl-only
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Try to import PDF reader
try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False
    print("Warning: pypdf not installed. PDFs will be skipped. Install with: pip install pypdf")

# Try to import requests for API calls
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("Warning: requests not installed. Use --curl-only mode or install with: pip install requests")


def extract_text_from_pdf(filepath: Path) -> str:
    """Extract text from a PDF file. Tries OCR if text extraction fails."""
    if not HAS_PYPDF:
        return ""
    
    try:
        reader = PdfReader(filepath)
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text and text.strip():
                text_parts.append(text)
        
        extracted_text = "\n\n".join(text_parts)
        
        # If no text extracted, try OCR (for scanned PDFs)
        if not extracted_text.strip():
            try:
                from pdf2image import convert_from_path
                import pytesseract
                
                # Convert PDF to images
                images = convert_from_path(str(filepath), dpi=200)
                ocr_text_parts = []
                
                for img in images:
                    ocr_text = pytesseract.image_to_string(img, lang='eng+ara')
                    if ocr_text.strip():
                        ocr_text_parts.append(ocr_text)
                
                if ocr_text_parts:
                    extracted_text = "\n\n".join(ocr_text_parts)
                    print(f"    (Used OCR for {filepath.name})")
            except ImportError:
                pass  # OCR libraries not available
            except Exception as e:
                print(f"    (OCR failed for {filepath.name}: {e})")
        
        return extracted_text
    except Exception as e:
        print(f"  Warning: Could not read PDF {filepath.name}: {e}")
        return ""


def extract_title(content: str, filename: str) -> str:
    """Extract title from markdown heading or use filename."""
    lines = content.strip().split("\n")
    for line in lines:
        if line.startswith("# "):
            return line[2:].strip()
    # Clean up filename as title
    title = filename.replace("_", " ").replace("-", " ")
    for ext in [".md", ".txt", ".pdf"]:
        title = title.replace(ext, "")
    return title.strip().title()


def read_document(filepath: Path) -> dict:
    """Read a document and return title + content."""
    content = ""
    
    if filepath.suffix.lower() == ".pdf":
        content = extract_text_from_pdf(filepath)
    elif filepath.suffix.lower() in [".md", ".txt"]:
        try:
            content = filepath.read_text(encoding="utf-8")
        except Exception as e:
            print(f"  Warning: Could not read {filepath.name}: {e}")
            return None
    else:
        return None
    
    if not content.strip():
        print(f"  ⚠ Skipping {filepath.name}: No content extracted (may be image-only or corrupted)")
        return None
    
    # Check if content is mostly garbage (too many control characters)
    printable_chars = sum(1 for c in content if c.isprintable() or c.isspace())
    if len(content) > 100 and printable_chars / len(content) < 0.5:
        print(f"  ⚠ Skipping {filepath.name}: Content appears corrupted (too many non-printable characters)")
        return None
    
    title = extract_title(content, filepath.name)
    
    return {
        "title": title,
        "content": content,
        "source": filepath.name,
    }


def upload_document(api_url: str, doc: dict, knowledge_base: str) -> bool:
    """Upload a document via the API."""
    if not HAS_REQUESTS:
        return False
    
    payload = {
        "title": doc["title"],
        "content": doc["content"],
        "knowledge_base": knowledge_base,
        "source": doc.get("source", doc["title"]),
    }
    
    try:
        response = requests.post(
            f"{api_url}/api/documents",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=300,  # Long timeout for large PDFs and embedding generation
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"  Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"  Error uploading: {e}")
        return False


def generate_curl_command(doc: dict, knowledge_base: str, api_url: str) -> str:
    """Generate a curl command for uploading."""
    payload = {
        "title": doc["title"],
        "content": doc["content"],
        "knowledge_base": knowledge_base,
        "source": doc.get("source", doc["title"]),
    }
    
    # Escape for shell
    json_str = json.dumps(payload).replace("'", "'\\''")
    
    return f"curl -X POST '{api_url}/api/documents' \\\n  -H 'Content-Type: application/json' \\\n  -d '{json_str}'"


def save_as_json(documents: list, output_file: Path, knowledge_base: str):
    """Save documents as a JSON file for manual upload."""
    output = []
    for doc in documents:
        output.append({
            "title": doc["title"],
            "content": doc["content"],
            "knowledge_base": knowledge_base,
            "source": doc.get("source", doc["title"]),
        })
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved {len(output)} documents to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Upload documents to pgvector database")
    parser.add_argument("--folder", "-f", required=True, help="Folder containing documents")
    parser.add_argument("--kb", "-k", default="legal", choices=["legal", "audit"], 
                        help="Knowledge base to upload to (default: legal)")
    parser.add_argument("--url", "-u", default="http://localhost:8000",
                        help="API URL (default: http://localhost:8000)")
    parser.add_argument("--curl-only", action="store_true",
                        help="Only generate curl commands, don't upload")
    parser.add_argument("--json-output", "-o", type=str,
                        help="Save documents as JSON file instead of uploading")
    
    args = parser.parse_args()
    
    folder = Path(args.folder)
    if not folder.exists():
        print(f"Error: Folder '{folder}' does not exist")
        sys.exit(1)
    
    print(f"Scanning folder: {folder}")
    print(f"Knowledge base: {args.kb}")
    print(f"API URL: {args.url}")
    print("-" * 50)
    
    # Find all documents
    documents = []
    all_files = sorted(folder.iterdir())
    total_files = len([f for f in all_files if f.is_file() and f.suffix.lower() in [".pdf", ".md", ".txt"]])
    
    print(f"Found {total_files} files to process...")
    
    for idx, filepath in enumerate(all_files, 1):
        if filepath.is_dir():
            continue
        if filepath.suffix.lower() not in [".pdf", ".md", ".txt"]:
            continue
        
        if total_files > 100:
            # Less verbose for large batches
            if idx % 100 == 0 or idx == total_files:
                print(f"  Processing {idx}/{total_files}...")
        else:
            print(f"Reading: {filepath.name}")
        
        doc = read_document(filepath)
        if doc:
            documents.append(doc)
            if total_files <= 100:
                print(f"  Title: {doc['title']}")
                print(f"  Content length: {len(doc['content'])} chars")
    
    print("-" * 50)
    print(f"Successfully read {len(documents)}/{total_files} documents")
    
    if not documents:
        print("No documents to process.")
        sys.exit(0)
    
    # Save as JSON if requested
    if args.json_output:
        save_as_json(documents, Path(args.json_output), args.kb)
        sys.exit(0)
    
    # Generate curl commands if requested
    if args.curl_only:
        print("\n" + "=" * 50)
        print("CURL COMMANDS:")
        print("=" * 50 + "\n")
        
        for doc in documents:
            print(f"# {doc['title']}")
            print(generate_curl_command(doc, args.kb, args.url))
            print()
        
        sys.exit(0)
    
    # Upload documents
    if not HAS_REQUESTS:
        print("\nError: 'requests' library not installed. Install with: pip install requests")
        print("Or use --curl-only to generate curl commands instead.")
        sys.exit(1)
    
    print("\nUploading documents...")
    success_count = 0
    error_count = 0
    
    for idx, doc in enumerate(documents, 1):
        if len(documents) > 50:
            # Show progress for large batches
            print(f"  [{idx}/{len(documents)}] Uploading: {doc['title'][:50]}...", end=" ", flush=True)
        else:
            print(f"  Uploading: {doc['title']}...", end=" ", flush=True)
        
        try:
            if upload_document(args.url, doc, args.kb):
                print("✓")
                success_count += 1
            else:
                print("✗")
                error_count += 1
        except KeyboardInterrupt:
            print("\n\nUpload interrupted by user.")
            break
        except Exception as e:
            print(f"✗ (Error: {str(e)[:50]})")
            error_count += 1
        
        # Show progress every 50 files
        if idx % 50 == 0:
            print(f"\n  Progress: {success_count} uploaded, {error_count} failed\n")
    
    print("-" * 50)
    print(f"✓ Uploaded: {success_count}")
    print(f"✗ Failed: {error_count}")
    print(f"Total: {len(documents)} documents")


if __name__ == "__main__":
    main()

