"""Lightweight evaluation of retrieval quality and answer relevance.

We measure two things without needing labelled ground truth:
1. Retrieval hit-rate: do retrieved documents contain expected keywords?
2. Answer groundedness: does the generated answer's content overlap with retrieved context?
"""
import json
from src.rag import ProcurementRAG


def keyword_hit_rate(docs, keywords):
    text = " ".join(d["text"].lower() for d in docs)
    hits = sum(1 for kw in keywords if kw.lower() in text)
    return hits / len(keywords) if keywords else 0.0


def groundedness(answer, docs):
    """Crude proxy: fraction of answer words that appear in the retrieved context."""
    ctx = " ".join(d["text"].lower() for d in docs)
    words = [w for w in answer.lower().split() if len(w) > 4]
    if not words:
        return 0.0
    grounded = sum(1 for w in words if w in ctx)
    return grounded / len(words)


def main():
    with open("eval/eval_questions.json", encoding="utf-8") as f:
        questions = json.load(f)
    rag = ProcurementRAG()

    retrieval_scores, grounded_scores = [], []
    for item in questions:
        result = rag.answer(item["question"])
        r = keyword_hit_rate(result["sources"], item["expect_keywords"])
        g = groundedness(result["answer"], result["sources"])
        retrieval_scores.append(r)
        grounded_scores.append(g)
        print(f"Q: {item['question']}")
        print(f"   retrieval keyword hit-rate: {r:.2f} | answer groundedness: {g:.2f}\n")

    print(f"Mean retrieval hit-rate: {sum(retrieval_scores)/len(retrieval_scores):.2f}")
    print(f"Mean answer groundedness: {sum(grounded_scores)/len(grounded_scores):.2f}")


if __name__ == "__main__":
    main()
