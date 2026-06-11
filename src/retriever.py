"""Hybrid retriever: parse simple structured filters from the question,
apply them as metadata filters, then semantically rank the rest.

This is the part to highlight in interviews: it addresses the weakness of
naive RAG on data that mixes free text with structured numeric/categorical fields.
"""
import re


def parse_filters(question: str) -> dict:
    q = question.lower()
    filters = {}

    # value threshold: "over £1m", "above 500000", "more than £250k"
    m = re.search(r"(?:over|above|more than|greater than)\s*£?\s*([\d,\.]+)\s*(m|k|million|thousand)?", q)
    if m:
        amount = float(m.group(1).replace(",", ""))
        unit = m.group(2)
        if unit in ("m", "million"):
            amount *= 1_000_000
        elif unit in ("k", "thousand"):
            amount *= 1_000
        filters["min_value"] = amount

    # buyer mention: "by the NHS", "from the Ministry of Defence"
    m = re.search(r"(?:by|from|awarded by)\s+(?:the\s+)?([a-z &]+?)(?:\s+in|\s+over|\s+for|\?|$)", q)
    if m:
        filters["buyer"] = m.group(1).strip()

    return filters


def apply_filters(docs: list[dict], filters: dict) -> list[dict]:
    out = []
    for d in docs:
        meta = d["metadata"]
        if "min_value" in filters:
            if meta["value_amount"] is None or meta["value_amount"] < filters["min_value"]:
                continue
        if "buyer" in filters:
            if filters["buyer"] not in (meta["buyer"] or ""):
                continue
        out.append(d)
    return out


def retrieve(vector_store, question: str, top_k: int = 5) -> list[dict]:
    filters = parse_filters(question)
    candidates = vector_store.search(question, k=max(50, top_k * 5))
    filtered = apply_filters(candidates, filters)
    # Fall back to unfiltered results if filters were too strict
    final = filtered if filtered else candidates
    return final[:top_k]
