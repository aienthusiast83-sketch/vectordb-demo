"""
ingest.py - Step 1 of "chat with my PDFs"

What this script does:
  1. Reads every PDF in the ./docs folder, page by page.
  2. Cuts the text into "chunks" made of whole sentences.
  3. Stores each chunk in Chroma, a vector database saved in the ./db folder.
     Chroma turns every chunk into an "embedding" - a list of numbers that
     captures the MEANING of the text - so we can later search by meaning.

Run it with:   python ingest.py
Run it again any time you add or change PDFs. Each run rebuilds the database
from scratch, so old chunks from earlier experiments never get mixed in.
"""

import re
from pathlib import Path

import chromadb
from pypdf import PdfReader

DOCS_FOLDER = Path(__file__).parent / "docs"
DB_FOLDER = Path(__file__).parent / "db"

SENTENCES_PER_CHUNK = 1  # how many whole sentences go in each chunk - try 1, 2 or 3


def split_into_sentences(text):
    """Split text into sentences: break after . ! or ? when followed by a space."""
    text = " ".join(text.split())  # PDFs break lines mid-sentence; join them back up
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]


def split_into_chunks(text, per_chunk=SENTENCES_PER_CHUNK):
    """Group sentences into chunks of `per_chunk` whole sentences each."""
    sentences = split_into_sentences(text)
    return [" ".join(sentences[i:i + per_chunk]) for i in range(0, len(sentences), per_chunk)]


def main():
    pdfs = sorted(DOCS_FOLDER.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found. Copy some PDF files into: {DOCS_FOLDER}")
        return

    # Open (or create) the database on disk. It survives after the script ends.
    client = chromadb.PersistentClient(path=str(DB_FOLDER))

    # A "collection" is like a table. Chroma's default embedding model runs
    # locally on your Mac for free (the first run downloads it, about 80 MB).
    # Start fresh each run: remove the old collection (if any), then create it again.
    # This only clears the vector database in ./db - your PDFs are never touched.
    try:
        client.delete_collection(name="my_pdfs")
    except Exception:
        pass  # nothing to remove on the very first run
    collection = client.create_collection(name="my_pdfs")

    total = 0
    for pdf_path in pdfs:
        reader = PdfReader(str(pdf_path))
        file_chunks = 0
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            chunks = split_into_chunks(text)
            if not chunks:
                continue  # scanned pages (images) have no text to extract

            # Each chunk gets a unique id plus "metadata" saying where it came from,
            # so search results can tell you the file and page.
            ids = [f"{pdf_path.name}-p{page_number}-c{i}" for i in range(len(chunks))]
            metadatas = [{"file": pdf_path.name, "page": page_number} for _ in chunks]

            # Chroma creates the embeddings for us inside this call.
            collection.add(ids=ids, documents=chunks, metadatas=metadatas)
            file_chunks += len(chunks)

        print(f"  {pdf_path.name}: {len(reader.pages)} pages -> {file_chunks} chunks")
        total += file_chunks

    print(f"\nDone. The database now holds {collection.count()} chunks.")
    print('Next, try:  python search.py "your question here"')


if __name__ == "__main__":
    main()
