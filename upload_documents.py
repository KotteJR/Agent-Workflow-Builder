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
    """Extract text from a PDF file."""
    if not HAS_PYPDF:
        return ""
    
    try:
        reader = PdfReader(filepath)
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return "\n\n".join(text_parts)
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
        print(f"  Skipping {filepath.name}: No content extracted")
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
            timeout=120,  # Long timeout for embedding generation
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
    for filepath in sorted(folder.iterdir()):
        if filepath.is_dir():
            continue
        if filepath.suffix.lower() not in [".pdf", ".md", ".txt"]:
            continue
        
        print(f"Reading: {filepath.name}")
        doc = read_document(filepath)
        if doc:
            documents.append(doc)
            print(f"  Title: {doc['title']}")
            print(f"  Content length: {len(doc['content'])} chars")
    
    print("-" * 50)
    print(f"Found {len(documents)} documents")
    
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
    
    for doc in documents:
        print(f"  Uploading: {doc['title']}...", end=" ", flush=True)
        if upload_document(args.url, doc, args.kb):
            print("✓")
            success_count += 1
        else:
            print("✗")
    
    print("-" * 50)
    print(f"Uploaded {success_count}/{len(documents)} documents")


if __name__ == "__main__":
    main()

