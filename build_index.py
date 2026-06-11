"""One-shot script: ingest data, build documents, build the vector index."""
from src.config import config
from src.ingest import run as ingest_run
from src.chunk import build_documents
from src.vector_store import VectorStore


def main():
    df = ingest_run(pages=5, out_csv=f"{config.data_dir}/contracts.csv")
    docs = build_documents(df)
    store = VectorStore(config.embedding_model)
    store.build(docs, config.index_path, config.docs_path)
    print(f"Index built with {len(docs)} contracts.")


if __name__ == "__main__":
    main()
