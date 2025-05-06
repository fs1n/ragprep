#!/usr/bin/env python3
"""
HTML to JSONL Preprocessor for RAG

Usage:
    python preprocess_html.py \
        --input PATH1 [PATH2 ...] \
        --output output.jsonl \
        --chunk_size 1000 \
        --chunk_overlap 200

Description:
    This script processes HTML files (forums, blogs, docs, etc.), cleans them using BeautifulSoup
    (removing boilerplate like headers/footers, scripts, styles), extracts metadata (title, author, date),
    chunks the content into segments with overlap using LangChain's RecursiveCharacterTextSplitter,
    and writes the result to a JSONL file (one JSON object per chunk).
"""

import os
import argparse
import json
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tqdm import tqdm

def clean_html(html_content):
    """
    Clean raw HTML content by removing scripts/styles and boilerplate sections.
    Returns clean text.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    # Remove scripts and styles
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    # Remove common boilerplate sections
    for tag in ["header", "footer", "nav", "aside", "form"]:
        found = soup.find(tag)
        if found:
            found.decompose()
    # TODO: add more rules if needed (e.g., remove divs with specific classes)
    text = soup.get_text(separator="\n")
    # Collapse multiple whitespace and strip
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines), soup

def extract_metadata(soup):
    """
    Extract basic metadata from a BeautifulSoup object.
    """
    meta = {}
    # Title
    if soup.title and soup.title.string:
        meta["title"] = soup.title.string.strip()
    # Author (common patterns)
    author_tag = soup.find('meta', attrs={'name': 'author'})
    if author_tag and author_tag.get("content"):
        meta["author"] = author_tag["content"].strip()
    # Author from <span class="author"> or similar
    if "author" not in meta:
        author_span = soup.find(class_="author")
        if author_span:
            meta["author"] = author_span.get_text(separator=" ").strip()
    # Timestamp/date
    time_tag = soup.find('time')
    if time_tag:
        # Prefer datetime attribute, otherwise text
        meta["date"] = time_tag.get("datetime", time_tag.get_text()).strip()
    # Meta property (common for articles)
    date_meta = soup.find('meta', attrs={'property': 'article:published_time'})
    if date_meta and date_meta.get("content"):
        meta["date"] = date_meta["content"].strip()
    return meta

def process_file(file_path, splitter, output_handle, source_url=None):
    """
    Process a single HTML file: read, clean, chunk, and write chunks to output.
    """
    try:
        # Read file as text (let BeautifulSoup detect encoding)
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            raw = f.read()
    except Exception as e:
        print(f"Warning: could not read file {file_path}: {e}")
        return

    text, soup = clean_html(raw)
    if not text:
        print(f"Note: no content extracted from {file_path}")
        return

    metadata = extract_metadata(soup)
    # Include filename and optional source URL
    metadata["filename"] = os.path.basename(file_path)
    if source_url:
        metadata["source"] = source_url

    # Chunk the text
    chunks = splitter.split_text(text)
    for idx, chunk in enumerate(chunks):
        entry = {
            "content": chunk,
            "metadata": {
                **metadata,
                "chunk": idx  # index of this chunk
            }
        }
        output_handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

def gather_files(paths):
    """
    Given a list of file paths or directories, return a list of HTML file paths.
    """
    files = []
    for path in paths:
        if os.path.isdir(path):
            # Walk directory for .html or .htm files
            for root, _, filenames in os.walk(path):
                for name in filenames:
                    if name.lower().endswith((".html", ".htm")):
                        files.append(os.path.join(root, name))
        elif os.path.isfile(path):
            files.append(path)
        else:
            print(f"Skipping non-existent path: {path}")
    return sorted(files)

def main():
    parser = argparse.ArgumentParser(description="Preprocess HTML files for RAG (clean, chunk, JSONL output)")
    parser.add_argument("--input", "-i", required=True, nargs="+", help="Input HTML file or directory (can specify multiple)")
    parser.add_argument("--output", "-o", default="output.jsonl", help="Output JSONL file")
    parser.add_argument("--chunk_size", type=int, default=1000, help="Chunk size (characters)")
    parser.add_argument("--chunk_overlap", type=int, default=200, help="Chunk overlap (characters)")
    args = parser.parse_args()

    files = gather_files(args.input)
    if not files:
        print("No input files found.")
        return

    # Initialize the text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )

    # Open output file
    with open(args.output, "w", encoding="utf-8") as out_f:
        # Process each file with a progress bar
        for file_path in tqdm(files, desc="Processing files"):
            # If each HTML has a known URL, one could map it here (not implemented)
            source_url = None
            process_file(file_path, text_splitter, out_f, source_url)

    print(f"Done. Output written to {args.output}")

if __name__ == "__main__":
    main()
