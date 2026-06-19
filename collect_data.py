"""
collect_data.py — Collect Messi vs Ronaldo GOAT debate comments from Reddit
via the PullPush archive API (api.pullpush.io).

Usage:
    python collect_data.py

Output:
    - data_raw/*.json   — raw API responses
    - data_raw/all_comments_raw.csv  — all collected comments (before labeling)
"""

import requests
import json
import csv
import time
import os
from datetime import datetime

# ─── Configuration ───────────────────────────────────────────────────────────

API_BASE = "https://api.pullpush.io/reddit/search/comment/"

SUBREDDITS = ["soccer", "football", "futbol"]

SEARCH_QUERIES = [
    "messi ronaldo goat",
    "messi vs ronaldo",
    "ronaldo better messi",
    "messi better ronaldo",
    "goat debate football",
    "cr7 messi",
    "ronaldo goat",
    "messi goat",
    "messi ronaldo best",
    "ronaldo messi debate",
    "messi ronaldo compare",
    "ronaldo legacy messi",
    "messi world cup ronaldo",
    "ronaldo champions league messi",
]

# How many comments to request per API call
SIZE_PER_REQUEST = 100

# Minimum comment length (characters) to keep — filters out very short replies
MIN_COMMENT_LENGTH = 30

# Maximum comment length — filters out essays that are too long for classification
MAX_COMMENT_LENGTH = 1500

# Rate limit: seconds between API requests
RATE_LIMIT_SECONDS = 2

# Output directories
RAW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data_raw")


def fetch_comments(query, subreddit, size=SIZE_PER_REQUEST, before=None):
    """Fetch comments from PullPush API."""
    params = {
        "q": query,
        "subreddit": subreddit,
        "size": size,
        "sort": "desc",
    }
    if before:
        params["before"] = before

    try:
        resp = requests.get(API_BASE, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])
    except requests.exceptions.RequestException as e:
        print(f"  [ERROR] Request failed: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"  [ERROR] JSON decode failed: {e}")
        return []


def extract_comment_fields(comment):
    """Extract relevant fields from a raw comment object."""
    body = comment.get("body", "").strip()

    # Skip deleted/removed comments
    if body in ("[deleted]", "[removed]", ""):
        return None

    # Skip too short or too long
    if len(body) < MIN_COMMENT_LENGTH or len(body) > MAX_COMMENT_LENGTH:
        return None

    return {
        "id": comment.get("id", ""),
        "text": body,
        "author": comment.get("author", "[unknown]"),
        "subreddit": comment.get("subreddit", ""),
        "score": comment.get("score", 0),
        "created_utc": comment.get("created_utc", 0),
        "permalink": f"https://reddit.com{comment.get('permalink', '')}",
    }


def collect_all():
    """Main collection loop — iterate over all query × subreddit combos."""
    os.makedirs(RAW_DIR, exist_ok=True)

    all_comments = {}  # keyed by comment ID for deduplication
    raw_responses = []

    total_queries = len(SEARCH_QUERIES) * len(SUBREDDITS)
    current = 0

    for query in SEARCH_QUERIES:
        for subreddit in SUBREDDITS:
            current += 1
            print(f"[{current}/{total_queries}] q=\"{query}\" sub=r/{subreddit}")

            comments = fetch_comments(query, subreddit)
            raw_responses.append({
                "query": query,
                "subreddit": subreddit,
                "count": len(comments),
                "data": comments,
            })

            new_count = 0
            for c in comments:
                extracted = extract_comment_fields(c)
                if extracted and extracted["id"] not in all_comments:
                    all_comments[extracted["id"]] = extracted
                    new_count += 1

            print(f"  -> {len(comments)} returned, {new_count} new (total: {len(all_comments)})")

            time.sleep(RATE_LIMIT_SECONDS)

    # Save raw responses
    raw_path = os.path.join(RAW_DIR, "raw_responses.json")
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(raw_responses, f, indent=2, ensure_ascii=False)
    print(f"\nRaw responses saved to {raw_path}")

    # Save cleaned CSV
    csv_path = os.path.join(RAW_DIR, "all_comments_raw.csv")
    comments_list = sorted(all_comments.values(), key=lambda x: int(x.get("created_utc", 0) or 0), reverse=True)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "text", "author", "subreddit", "score", "created_utc", "permalink"])
        writer.writeheader()
        writer.writerows(comments_list)

    print(f"Cleaned CSV saved to {csv_path}")
    print(f"Total unique comments: {len(comments_list)}")

    # Print length distribution
    lengths = [len(c["text"]) for c in comments_list]
    if lengths:
        print(f"\nText length stats:")
        print(f"  Min: {min(lengths)} chars")
        print(f"  Max: {max(lengths)} chars")
        print(f"  Avg: {sum(lengths) // len(lengths)} chars")
        print(f"  Median: {sorted(lengths)[len(lengths)//2]} chars")

    return comments_list


if __name__ == "__main__":
    print("=" * 60)
    print("TakeMeter — Data Collection")
    print(f"Collecting from: {', '.join(f'r/{s}' for s in SUBREDDITS)}")
    print(f"Search queries: {len(SEARCH_QUERIES)}")
    print("=" * 60)
    print()

    results = collect_all()

    print()
    print("=" * 60)
    print("Collection complete!")
    print(f"Next step: Review data_raw/all_comments_raw.csv")
    print(f"Then annotate with labels: stat_analysis, hot_take, bait, appreciation")
    print("=" * 60)
