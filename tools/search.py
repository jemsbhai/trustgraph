"""TrustGraph web search tool using Tavily."""

import os
import json
from urllib.request import Request, urlopen
from urllib.error import URLError
from typing import Any


TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
TAVILY_URL = "https://api.tavily.com/search"


def web_search(query: str, max_results: int = 5) -> list[dict]:
    """Search the web using Tavily and return structured results.

    Returns list of dicts with: title, url, content, score
    """
    if not TAVILY_API_KEY:
        print("[WARN] TAVILY_API_KEY not set, returning empty results");
        return []

    payload = json.dumps({
        "query": query,
        "max_results": max_results,
        "include_answer": False,
        "search_depth": "basic",
    }).encode("utf-8")

    req = Request(
        TAVILY_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TAVILY_API_KEY}",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = []
            for r in data.get("results", []):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "content": r.get("content", ""),
                    "score": r.get("score", 0.0),
                })
            return results
    except URLError as e:
        print(f"[ERROR] Tavily search failed: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return []
