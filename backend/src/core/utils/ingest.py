"""CLI script to ingest markdown documents from rag_data/ into ChromaDB.

Usage (from the backend directory):
    python -m src.core.utils.ingest              # defaults
    python -m src.core.utils.ingest --data-dir rag_data --reset

The script:
  1. Reads every *.md file in the data directory.
  2. Splits each file into overlapping chunks using section-aware markdown splitting.
  3. Embeds the chunks with OpenAI embeddings.
  4. Upserts them into the configured ChromaDB collection.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

import chromadb
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

# ---------------------------------------------------------------------------
# Defaults (overridable via CLI flags or env vars)
# ---------------------------------------------------------------------------
DEFAULT_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "rag_data")
DEFAULT_CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
DEFAULT_CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8100"))
DEFAULT_COLLECTION = os.getenv("CHROMA_COLLECTION_NAME", "company_policies")
DEFAULT_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "1000"))
DEFAULT_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))


def _resolve_data_dir(data_dir: str) -> Path:
    p = Path(data_dir).resolve()
    if not p.exists():
        print(f"[ERROR] Data directory does not exist: {p}")
        sys.exit(1)
    return p


def _load_markdown_files(data_dir: Path) -> list[dict]:
    """Return a list of dicts with keys: source, filename, content."""
    files: list[dict] = []
    for md_file in sorted(data_dir.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        files.append(
            {
                "source": str(md_file),
                "filename": md_file.name,
                "content": content,
            }
        )
    if not files:
        print(f"[WARN] No markdown files found in {data_dir}")
    return files


def _split_documents(
    files: list[dict],
    chunk_size: int,
    chunk_overlap: int,
) -> list:
    """Split markdown files into LangChain Document objects with metadata."""
    from langchain_core.documents import Document

    # Markdown header-aware first-pass splitter
    headers_to_split_on = [
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
    ]
    md_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False,
    )

    # Second-pass recursive splitter for large sections
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    all_docs: list[Document] = []

    for file_info in files:
        filename = file_info["filename"]
        content = file_info["content"]

        # First split by markdown headers
        md_docs = md_splitter.split_text(content)

        for md_doc in md_docs:
            # Build section path from markdown header metadata
            section_parts = []
            for key in ("h1", "h2", "h3"):
                if key in md_doc.metadata:
                    section_parts.append(md_doc.metadata[key])
            section = " > ".join(section_parts) if section_parts else filename

            # Second split: chunk large sections
            sub_chunks = text_splitter.split_text(md_doc.page_content)

            for i, chunk in enumerate(sub_chunks):
                all_docs.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            "source": filename,
                            "section": section,
                            "chunk_index": i,
                        },
                    )
                )

    return all_docs


def ingest(
    data_dir: str = DEFAULT_DATA_DIR,
    chroma_host: str = DEFAULT_CHROMA_HOST,
    chroma_port: int = DEFAULT_CHROMA_PORT,
    collection_name: str = DEFAULT_COLLECTION,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    reset: bool = False,
) -> int:
    """Run the full ingestion pipeline.

    Returns the number of chunks ingested.
    """

    data_path = _resolve_data_dir(data_dir)
    print(f"[INFO] Data directory : {data_path}")
    print(f"[INFO] ChromaDB       : {chroma_host}:{chroma_port}")
    print(f"[INFO] Collection     : {collection_name}")
    print(f"[INFO] Chunk size     : {chunk_size}  overlap: {chunk_overlap}")

    # 1. Load markdown files
    files = _load_markdown_files(data_path)
    names = [f["filename"] for f in files]
    print(f"[INFO] Found {len(files)} markdown file(s): {names}")

    # 2. Split into chunks
    documents = _split_documents(files, chunk_size, chunk_overlap)
    print(f"[INFO] Created {len(documents)} document chunks")

    if not documents:
        print("[WARN] Nothing to ingest — exiting.")
        return 0

    # 3. Connect to ChromaDB
    chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)

    # Optionally reset the collection
    if reset:
        try:
            chroma_client.delete_collection(collection_name)
            print(f"[INFO] Deleted existing collection '{collection_name}'")
        except Exception:
            pass  # collection didn't exist

    # 4. Build embeddings
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # 5. Upsert into ChromaDB via LangChain Chroma wrapper
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        client=chroma_client,
        collection_name=collection_name,
    )

    count = vectorstore._collection.count()
    print(f"[OK] Ingested {count} chunks into collection '{collection_name}'")
    return count


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Ingest RAG markdown documents into ChromaDB",
    )
    parser.add_argument(
        "--data-dir",
        default=DEFAULT_DATA_DIR,
        help="Path to *.md files directory (default: rag_data/)",
    )
    parser.add_argument(
        "--chroma-host",
        default=DEFAULT_CHROMA_HOST,
        help="ChromaDB server host (default: localhost)",
    )
    parser.add_argument(
        "--chroma-port",
        type=int,
        default=DEFAULT_CHROMA_PORT,
        help="ChromaDB server port (default: 8100)",
    )
    parser.add_argument(
        "--collection",
        default=DEFAULT_COLLECTION,
        help="ChromaDB collection name (default: company_policies)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help="Maximum chunk size in characters (default: 1000)",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=DEFAULT_CHUNK_OVERLAP,
        help="Overlap between chunks in characters (default: 200)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete the collection before ingesting (fresh start)",
    )

    args = parser.parse_args()

    ingest(
        data_dir=args.data_dir,
        chroma_host=args.chroma_host,
        chroma_port=args.chroma_port,
        collection_name=args.collection,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        reset=args.reset,
    )


if __name__ == "__main__":
    main()
