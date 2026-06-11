# UK Procurement RAG Assistant

A retrieval-augmented generation (RAG) chatbot that answers natural-language
questions about UK public sector procurement contracts, built on open
government data.

> **Data**: [Contracts Finder](https://www.contractsfinder.service.gov.uk),
> published by the Crown Commercial Service.
> Contains public sector information licensed under the
> [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

## Why this project

Public procurement data is high-volume and mixes free text (contract titles,
descriptions) with structured fields (values, buyers, dates). Plain semantic
search handles the text well but struggles with structured intent like
"contracts over £1m awarded by the NHS". This project implements a **hybrid
retriever** that parses structured filters from the question and applies them
before semantic ranking — a small design choice that meaningfully improves
answer quality.

## Architecture

1. **Ingest** — pull recent notices from the Contracts Finder OCDS API and
   flatten the nested records into a tidy table (`src/ingest.py`).
2. **Document build** — convert each contract into one searchable text block
   with attached metadata (`src/chunk.py`).
3. **Embed & index** — encode documents with a sentence-transformer model and
   store them in a FAISS index (`src/vector_store.py`).
4. **Hybrid retrieve** — parse value/buyer filters, apply them, then
   semantically rank (`src/retriever.py`).
5. **Generate** — build a grounded prompt and answer with a pluggable LLM
   backend: free local (Ollama) or OpenAI (`src/llm.py`, `src/rag.py`).
6. **Evaluate** — measure retrieval hit-rate and answer groundedness
   (`eval/evaluate.py`).

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env        # then edit your choices
python build_index.py       # downloads data + builds the index
streamlit run app/streamlit_app.py
```

Run on a free local model with [Ollama](https://ollama.com):
`ollama pull llama3.1` then set `LLM_BACKEND=ollama` in `.env`.

## Evaluation

```bash
python eval/evaluate.py
```

Reports mean retrieval keyword hit-rate and answer groundedness across a small
question set. Extend `eval/eval_questions.json` to track quality as you change
the chunking, embedding model, or retriever.

## Design trade-offs

- **FAISS flat index**: exact search, simple, fine for tens of thousands of
  contracts. Swap for an IVF/HNSW index at larger scale.
- **One document per contract**: keeps provenance clean; long descriptions
  could be sub-chunked if needed.
- **Regex-based filter parsing**: transparent and fast; an LLM-based query
  parser would generalise better at the cost of latency.

## License

Code: MIT. Data: Open Government Licence v3.0 (see attribution above).
