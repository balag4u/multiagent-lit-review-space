# data_providers.py
import requests
import xml.etree.ElementTree as ET
import json

def search_pubmed(query, max_results=10):
    """
    Searches PubMed for a given query and returns a list of articles.
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    search_url = f"{base_url}esearch.fcgi"
    fetch_url = f"{base_url}efetch.fcgi"

    search_params = {
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "usehistory": "y"
    }
    try:
        search_response = requests.get(search_url, params=search_params)
        search_response.raise_for_status()
        search_root = ET.fromstring(search_response.content)
        id_list = [id_elem.text for id_elem in search_root.findall(".//Id")]
    except requests.exceptions.RequestException as e:
        print(f"Error searching PubMed: {e}")
        return []

    if not id_list:
        return []

    fetch_params = {
        "db": "pubmed",
        "id": ",".join(id_list),
        "rettype": "abstract",
        "retmode": "xml"
    }
    try:
        fetch_response = requests.get(fetch_url, params=fetch_params)
        fetch_response.raise_for_status()
        fetch_root = ET.fromstring(fetch_response.content)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from PubMed: {e}")
        return []

    articles = []
    for article_elem in fetch_root.findall(".//PubmedArticle"):
        title = article_elem.find(".//ArticleTitle").text
        abstract = article_elem.find(".//Abstract/AbstractText")
        abstract_text = abstract.text if abstract is not None else ""
        doi = article_elem.find(".//ArticleId[@IdType='doi']")
        doi_text = doi.text if doi is not None else ""
        pmid = article_elem.find(".//PMID").text
        url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

        articles.append({
            "title": title,
            "abstract": abstract_text,
            "doi": doi_text,
            "url": url,
            "source": "PubMed"
        })
    return articles

def search_patents(query, max_results=10):
    """
    Searches PatentsView for a given query and returns a list of patents.
    """
    base_url = "https://api.patentsview.org/patents/query"
    # Perform a text search for the query in the patent title or abstract
    query_dict = {
        "_or": [
            {"_text_any": {"patent_title": query}},
            {"_text_any": {"patent_abstract": query}}
        ]
    }
    params = {
        "q": json.dumps(query_dict),
        "f": '["patent_id","patent_title","patent_abstract","assignee_organization","patent_date"]',
        "o": {"per_page": max_results}
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        patents = []
    except requests.exceptions.RequestException as e:
        print(f"Error searching PatentsView: {e}")
        return []
    except json.JSONDecodeError:
        print("Error decoding JSON from PatentsView")
        return []
    for patent in data.get("patents", []):
        patents.append({
            "title": patent.get("patent_title"),
            "abstract": patent.get("patent_abstract"),
            "url": f"https://patents.google.com/patent/US{patent.get('patent_id')}/en",
            "source": "PatentsView"
        })
    return patents
