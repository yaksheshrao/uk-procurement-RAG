"""Turn each contract row into a single searchable text document with metadata."""
import json
import pandas as pd


def build_documents(df: pd.DataFrame) -> list[dict]:
    docs = []
    for _, r in df.iterrows():
        value = r.get("value_amount")
        value_str = f"{value:,.0f} {r.get('currency', '')}".strip() if pd.notna(value) else "unknown"
        text = (
            f"Contract title: {r['title']}\n"
            f"Buyer: {r['buyer']}\n"
            f"Supplier: {r['supplier']}\n"
            f"Value: {value_str}\n"
            f"Status: {r['status']}\n"
            f"Published: {r['published']}\n"
            f"Description: {r['description']}"
        )
        docs.append(
            {
                "id": r["ocid"],
                "text": text,
                "metadata": {
                    "buyer": (r["buyer"] or "").lower(),
                    "supplier": (r["supplier"] or "").lower(),
                    "value_amount": float(value) if pd.notna(value) else None,
                    "published": r["published"],
                },
            }
        )
    return docs


def save_documents(docs: list[dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
