import requests
import xmltodict

PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

def search_pubmed(query: str, max_results: int = 5) -> list[str]:
    """Retorna lista de PMIDs para una query."""
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json"
    }
    response = requests.get(PUBMED_SEARCH_URL, params=params)
    data = response.json()
    return data["esearchresult"]["idlist"]

def fetch_abstracts(pmids: list[str]) -> list[dict]:
    """Descarga abstracts de una lista de PMIDs."""
    if not pmids:
        return []
    
    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
        "rettype": "abstract"
    }
    response = requests.get(PUBMED_FETCH_URL, params=params)
    data = xmltodict.parse(response.content)
    
    articles = []
    raw_articles = data.get("PubmedArticleSet", {}).get("PubmedArticle", [])
    
    # Si viene uno solo no es lista
    if isinstance(raw_articles, dict):
        raw_articles = [raw_articles]
    
    for article in raw_articles:
        try:
            medline = article["MedlineCitation"]
            article_data = medline["Article"]
            
            title = article_data.get("ArticleTitle", "Sin titulo")
            if isinstance(title, dict):
                title = title.get("#text", "Sin titulo")
            
            abstract = article_data.get("Abstract", {}).get("AbstractText", "Sin abstract")
            if isinstance(abstract, list):
                abstract = " ".join([
                    a.get("#text", a) if isinstance(a, dict) else a 
                    for a in abstract
                ])
            elif isinstance(abstract, dict):
                abstract = abstract.get("#text", "Sin abstract")
            
            pmid = str(medline["PMID"]["#text"] if isinstance(medline["PMID"], dict) else medline["PMID"])
            
            year = (
                medline.get("Article", {})
                .get("Journal", {})
                .get("JournalIssue", {})
                .get("PubDate", {})
                .get("Year", "s/f")
            )

            articles.append({
                "pmid": pmid,
                "title": title,
                "abstract": str(abstract),
                "year": year,
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            })
        except Exception:
            continue
    
    return articles