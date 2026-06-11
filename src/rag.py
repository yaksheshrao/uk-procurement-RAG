"""Tie retrieval and generation together into a question-answering pipeline."""
from src.config import config
from src.vector_store import VectorStore
from src.retriever import retrieve
from src.llm import generate

PROMPT_TEMPLATE = """You are an assistant answering questions about UK public sector \
procurement contracts. Use ONLY the context below. If the answer is not in the context, \
say you don't have enough information. Cite contract titles where relevant.

Context:
{context}

Question: {question}

Answer:"""


class ProcurementRAG:
    def __init__(self):
        self.store = VectorStore(config.embedding_model)
        self.store.load(config.index_path, config.docs_path)

    def answer(self, question: str) -> dict:
        docs = retrieve(self.store, question, top_k=config.top_k)
        context = "\n\n---\n\n".join(d["text"] for d in docs)
        prompt = PROMPT_TEMPLATE.format(context=context, question=question)
        answer = generate(prompt)
        return {"answer": answer, "sources": docs}
