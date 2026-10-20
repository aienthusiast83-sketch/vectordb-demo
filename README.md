# Build Your First Vector Database: chat with your PDFs

A small beginner project from the **My AI Notebook** YouTube channel. It shows how a vector database finds answers in documents **by meaning, not by exact words**, and how RAG makes an AI answer only from your files.

▶️ **Watch the video:** https://www.youtube.com/watch?v=0_HNkIzNdn8

> The Python scripts were written with the help of Claude (an AI assistant). I ran them, fixed errors along the way and learned how each part works. Every file has plain-English comments.

## The idea in plain English

- **Chunk:** a small piece of a document (here, one sentence).
- **Embedding:** an AI model turns each chunk into a list of numbers. Similar meaning gives similar numbers.
- **Vector database (Chroma):** stores those numbers and finds the ones closest to your question.
- **RAG (retrieve, augment, generate):** the closest chunks plus your question go to an AI, which answers using only those chunks and names the source file.

## Files

| File | What it does |
|---|---|
| `docs/` | Three tiny sample PDFs: Oceans, Mountains, Deserts. Add your own here. |
| `ingest.py` | Reads the PDFs, splits them into chunks, stores them in Chroma |
| `search.py` | Shows the chunks closest in meaning to your question |
| `ask.py` | Builds a "answer only from these sources" prompt for Claude (RAG) |

## Setup (Mac Terminal)

Needs Python 3.10 to 3.13. **Python 3.14 doesn't work yet on Intel Macs** (pip gets stuck building numpy). If that happens, install Python 3.12 from [python.org](https://www.python.org/downloads/) and use it for this project.

```bash
cd path/to/vectordb-demo
python3 -m venv .venv            # or: python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run it

```bash
python ingest.py                                    # builds the database (15 chunks)
python search.py "Where is it hard to breathe?"     # search by meaning
python ask.py "Which is the highest mountain?"      # copies a RAG prompt; paste it into Claude
```

Optional automatic mode: `pip install anthropic`, set `ANTHROPIC_API_KEY`, then `python ask.py --api "your question"`.

## Experiments to try

1. Change `SENTENCES_PER_CHUNK` in `ingest.py` (1, 3 or 5), run `ingest.py` again and compare the search results.
2. Change `TOP_K` in `search.py` (2 vs 8).
3. Ask something that isn't in the PDFs, like "What is the capital of France?", and see `ask.py` say it couldn't find it.

## Notes

- Scanned PDFs (photos of pages) contain no text, so they produce no chunks.
- The first run downloads the embedding model (about 80 MB). After that it works offline.
- Never share your API key or commit it to GitHub.

MIT licensed. Questions or ideas? Leave a comment on the video.
