import chromadb
from chromadb.utils import embedding_functions
from rag.pubmed_fetcher import search_pubmed, fetch_abstracts

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.Client()

def build_collection(hallazgos: list[str]) -> chromadb.Collection:
    collection_name = "pubmed_evidence"

    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    collection = client.create_collection(
        name=collection_name,
        embedding_function=embedding_fn
    )

    all_articles = []

    for hallazgo in hallazgos:
        # Query principal
        pmids = search_pubmed(hallazgo, max_results=5)
        articles = fetch_abstracts(pmids)
        all_articles.extend(articles)

        # Query alternativa mas corta para mejor cobertura
        termino = hallazgo.split(" clinical")[0]
        pmids2 = search_pubmed(f"{termino} blood test abnormal", max_results=3)
        articles2 = fetch_abstracts(pmids2)
        all_articles.extend(articles2)

    if not all_articles:
        return collection

    # Deduplicar
    seen = set()
    unique_articles = []
    for a in all_articles:
        if a["pmid"] not in seen and len(a["abstract"]) > 100:
            seen.add(a["pmid"])
            unique_articles.append(a)

    if not unique_articles:
        return collection

    collection.add(
        documents=[a["abstract"] for a in unique_articles],
        metadatas=[{
            "title": a["title"],
            "pmid": a["pmid"],
            "year": a["year"],
            "url": a["url"]
        } for a in unique_articles],
        ids=[a["pmid"] for a in unique_articles]
    )

    return collection

def query_evidence(collection: chromadb.Collection, query: str, n_results: int = 5) -> list[dict]:
    if collection.count() == 0:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count())
    )

    evidence = []
    for i, doc in enumerate(results["documents"][0]):
        meta = results["metadatas"][0][i]
        evidence.append({
            "title": meta["title"],
            "abstract": doc[:400] + "...",
            "year": meta["year"],
            "url": meta["url"],
            "pmid": meta["pmid"]
        })

    return evidence