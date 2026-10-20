"""
search.py - Step 2 of "chat with my PDFs"

What this script does:
  1. Turns your question into an embedding (a list of numbers capturing its meaning),
     using the same model that ingest.py used for the chunks.
  2. Asks Chroma for the chunks whose embeddings are closest to the question's.
  3. Prints them with the file name, page number and "distance".
     A smaller distance means the chunk is closer in meaning to your question.

Run it with:   python search.py "what is the penalty for late payment?"
"""

import sys
from pathlib import Path

import chromadb

DB_FOLDER = Path(__file__).parent / "db"
TOP_K = 4  # how many chunks to show - try 2 or 8 and compare


def main():
    if len(sys.argv) < 2:
        print('Please add a question, for example:  python search.py "what is RAG?"')
        return
    question = " ".join(sys.argv[1:])

    client = chromadb.PersistentClient(path=str(DB_FOLDER))
    try:
        collection = client.get_collection(name="my_pdfs")
    except Exception:
        print("No database yet. Put PDFs in the docs folder and run:  python ingest.py")
        return

    results = collection.query(query_texts=[question], n_results=TOP_K)

    print(f'\nQuestion: {question}\n')
    for rank, (text, meta, distance) in enumerate(
        zip(results["documents"][0], results["metadatas"][0], results["distances"][0]), start=1
    ):
        print(f"#{rank}  {meta['file']}, page {meta['page']}  (distance {distance:.3f})")
        print("-" * 70)
        print(text)
        print()


if __name__ == "__main__":
    main()
