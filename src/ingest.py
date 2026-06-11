"""Download UK Contracts Finder notices via the OCDS search API.

Source: https://www.contractsfinder.service.gov.uk
Contains public sector information licensed under the Open Government Licence v3.0.
"""
import json
import time
import requests
import pandas as pd

OCDS_SEARCH_URL = (
    "https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search"
)


def fetch_notices(pages: int = 5, sleep: float = 1.0) -> list[dict]:
    """Fetch recent OCDS releases. Each page returns a batch of notices."""
    all_releases = []
    cursor = None
    for _ in range(pages):
        params = {"order": "desc"}
        if cursor:
            params["cursor"] = cursor
        resp = requests.get(OCDS_SEARCH_URL, params=params, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
        releases = payload.get("results", []) or payload.get("releases", [])
        if not releases:
            break
        all_releases.extend(releases)
        cursor = _next_cursor(payload)
        if not cursor:
            break
        time.sleep(sleep)
    return all_releases


def _next_cursor(payload: dict):
    links = payload.get("links", {})
    nxt = links.get("next")
    if not nxt or "cursor=" not in nxt:
        return None
    return nxt.split("cursor=")[-1].split("&")[0]


def flatten(releases: list[dict]) -> pd.DataFrame:
    """Pull the fields we care about out of nested OCDS records."""
    rows = []
    for rel in releases:
        tender = rel.get("tender", {}) or {}
        buyer = rel.get("buyer", {}) or {}
        value = (tender.get("value") or {})
        awards = rel.get("awards", []) or []
        supplier = ""
        if awards:
            suppliers = awards[0].get("suppliers", []) or []
            if suppliers:
                supplier = suppliers[0].get("name", "")
        rows.append(
            {
                "ocid": rel.get("ocid", ""),
                "title": tender.get("title", ""),
                "description": tender.get("description", ""),
                "buyer": buyer.get("name", ""),
                "supplier": supplier,
                "value_amount": value.get("amount"),
                "currency": value.get("currency", ""),
                "status": tender.get("status", ""),
                "published": rel.get("date", ""),
            }
        )
    return pd.DataFrame(rows)


def run(pages: int = 5, out_csv: str = "data/contracts.csv") -> pd.DataFrame:
    releases = fetch_notices(pages=pages)
    df = flatten(releases)
    df = df[(df["title"].str.len() > 0)].drop_duplicates(subset=["ocid"])
    df.to_csv(out_csv, index=False)
    print(f"Saved {len(df)} contracts to {out_csv}")
    return df


if __name__ == "__main__":
    run()
