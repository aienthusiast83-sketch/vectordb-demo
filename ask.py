"""
ask.py - Step 3 of "chat with my PDFs": the "A" in RAG (retrieval-augmented generation)

What this script does:
  1. RETRIEVE: finds the chunks of your PDFs closest in meaning to your question
     (exactly what search.py does).
  2. AUGMENT:  builds a prompt that contains those chunks plus your question,
     with an instruction to answer ONLY from them and to name the source file.
  3. GENERATE: an AI writes the answer from that prompt. Two ways:

     Free mode (default, uses your Claude Pro plan):
         python ask.py "your question"
         The prompt is printed AND copied to your clipboard.
         Paste it into the Claude app (Cmd+V) and press Enter.

     API mode (fully automatic, needs an API key with a little credit):
         python ask.py --api "your question"
         One-time setup:  pip install anthropic
                          export ANTHROPIC_API_KEY="your-key-here"
"""

import subprocess
import sys
from pathlib import Path

import chromadb

DB_FOLDER = Path(__file__).parent / "db"
TOP_K = 4                      # how many chunks to give the AI
API_MODEL = "claude-haiku-5-5"  # cheapest Claude model - fine for short answers


def retrieve(question):
    """Step 1: find the chunks closest in meaning to the question."""
    client = chromadb.PersistentClient(path=str(DB_FOLDER))
    collection = client.get_collection(name="my_pdfs")
    results = collection.query(query_texts=[question], n_results=TOP_K)
    return list(zip(results["documents"][0], results["metadatas"][0]))


def build_prompt(question, chunks):
    """Step 2: put the chunks and the question together into one prompt."""
    sources = "\n".join(
        f"[{i}] ({meta['file']}, page {meta['page']}) {text}"
        for i, (text, meta) in enumerate(chunks, start=1)
    )
    return (
        "Answer the question using ONLY the sources below. "
        "After each fact, name the source file in brackets, like (Mountains.pdf). "
        "If the sources do not contain the answer, say \"I couldn't find that in the documents.\"\n\n"
        f"Sources:\n{sources}\n\n"
        f"Question: {question}"
    )


def answer_with_api(prompt):
    """Step 3 (API mode): send the prompt to Claude and return its answer."""
    import anthropic  # only needed in API mode

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from your Terminal
    message = client.messages.create(
        model=API_MODEL,
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def main():
    args = sys.argv[1:]
    use_api = "--api" in args
    question = " ".join(a for a in args if a != "--api")
    if not question:
        print('Please add a question, for example:  python ask.py "Which state grows the most coffee?"')
        return

    try:
        chunks = retrieve(question)
    except Exception:
        print("No database yet. Put PDFs in the docs folder and run:  python ingest.py")
        return

    prompt = build_prompt(question, chunks)

    if use_api:
        print("Asking Claude...\n")
        print(answer_with_api(prompt))
        return

    print("=" * 70)
    print(prompt)
    print("=" * 70)
    try:
        subprocess.run("pbcopy", input=prompt.encode("utf-8"), check=True)  # Mac clipboard
        print("\nCopied to your clipboard. Paste it into the Claude app (Cmd+V) and press Enter.")
    except Exception:
        print("\nCopy the text between the lines above and paste it into the Claude app.")


if __name__ == "__main__":
    main()
