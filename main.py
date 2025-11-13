"""
main.py — MediAssist Retrieval Pipeline

Two-tier system:
1. General Knowledge Base (200 articles): permanent PubMed foundation.
2. Query-specific Cache (100 articles per user query): temporary, capped at 15.
"""

from pathlib import Path
from pubmed import PubMedRetriever
from pubmed_vectorstore import process_pubmed_articles, generate_answer, initialize_components
from datetime import datetime
import json

# Paths for caching
CACHE_DIR = Path(__file__).parent / "resources" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
QUERY_CACHE_FILE = CACHE_DIR / "query_cache.json"


def load_cache(file_path):
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def update_query_cache(query):
    """
    Fetch up to 100 new PubMed articles related to the given query.
    Keeps only the 15 most recent queries.
    """
    query_cache = load_cache(QUERY_CACHE_FILE)

    if query in query_cache:
        print(f"🧠 Using cached results for query: '{query}'")
        return query_cache[query]["articles"]

    print(f"🔎 Searching PubMed for new query: '{query}'...")
    pmids = PubMedRetriever.search_pubmed_articles(query, max_results=100)
    articles = PubMedRetriever.fetch_pubmed_abstracts(pmids)

    query_cache[query] = {
        "articles": articles,
        "timestamp": str(datetime.now())
    }

    # Limit to last 15 queries
    if len(query_cache) > 15:
        oldest_key = sorted(
            query_cache.items(), key=lambda x: x[1]["timestamp"]
        )[0][0]
        del query_cache[oldest_key]

    save_cache(query_cache, QUERY_CACHE_FILE)
    print(f"✅ Cached {len(articles)} articles for query: '{query}'")

    return articles


def main():
    # Step 1: Initialize LLM + Vector DB
    initialize_components()

    # Step 2: Handle a user query
    query = input("\n💬 Enter your medical question: ").strip()

    # Step 3: Retrieve or fetch query-specific articles
    query_articles = update_query_cache(query)

    # Step 4: Store in vector DB
    print("\n📥 Storing combined articles into vector database...")
    for message in process_pubmed_articles(query_articles):
        print("   ", message)

    # Step 5: Generate an answer
    print("\n🧩 Generating answer...\n")
    answer, sources, _ = generate_answer(query)

    print("\n🩺 Answer:\n", answer)
    print("\n🔗 Sources:\n", "\n".join(sources))


if __name__ == "__main__":
    main()