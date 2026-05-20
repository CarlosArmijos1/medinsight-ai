# test_pubmed.py — creá este archivo en la raíz del proyecto
from rag.pubmed_fetcher import search_pubmed, fetch_abstracts

pmids = search_pubmed("eosinophilia clinical significance", max_results=3)
print("PMIDs:", pmids)

articles = fetch_abstracts(pmids)
print("Articulos:", len(articles))
for a in articles:
    print("-", a["title"])