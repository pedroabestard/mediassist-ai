import requests
from xml.etree import ElementTree
from time import sleep


class PubMedRetriever:
    SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    @staticmethod
    def search_pubmed_articles(search_term, max_results=300):
        params = {
            'db': 'pubmed',
            'term': search_term,
            'retmax': 100,
            'retmode': 'xml'
        }

        pmid_list = []
        start = 0
        while len(pmid_list) < max_results:
            params['retstart'] = start
            response = requests.get(PubMedRetriever.SEARCH_URL, params=params)
            root = ElementTree.fromstring(response.content)
            ids = [id_elem.text for id_elem in root.findall(".//Id")]
            if not ids:
                break
            pmid_list.extend(ids)
            start += 100
            sleep(1)  # avoid overloading PubMed's servers
        return pmid_list[:max_results]

    @staticmethod
    def fetch_pubmed_abstracts(pmid_list):
        abstracts = []
        for i in range(0, len(pmid_list), 100):
            fetch_params = {
                'db': 'pubmed',
                'id': ','.join(pmid_list[i:i + 100]),
                'retmode': 'xml'
            }
            fetch_response = requests.get(PubMedRetriever.FETCH_URL, params=fetch_params)
            fetch_root = ElementTree.fromstring(fetch_response.content)

            for article in fetch_root.findall(".//PubmedArticle"):
                pmid = article.find(".//PMID").text
                title = article.find(".//ArticleTitle").text if article.find(
                    ".//ArticleTitle") is not None else "No Title"

                abstract_sections = article.findall(".//AbstractText")
                abstract = {
                    section.attrib.get('Label', 'SUMMARY'): section.text
                    for section in abstract_sections if section.text is not None
                } if abstract_sections else {"SUMMARY": "No Abstract"}

                journal = article.find(".//Journal/Title").text if article.find(
                    ".//Journal/Title") is not None else "Unknown Journal"
                pub_date = article.find(".//PubDate/Year").text if article.find(
                    ".//PubDate/Year") is not None else "Unknown Year"

                authors = [
                    f"{author.find('.//ForeName').text} {author.find('.//LastName').text}"
                    for author in article.findall(".//Author")
                    if author.find(".//ForeName") is not None and author.find(".//LastName") is not None
                ]

                abstracts.append({
                    "pmid": pmid,
                    "title": title,
                    "abstract": abstract,
                    "journal": journal,
                    "authors": ", ".join(authors) if authors else "No Authors",
                    "publication_date": pub_date
                })
        return abstracts


# ---- Combined workflow ----
def retrieve_pubmed_data(search_term, max_results=5):
    print(f"🔍 Searching PubMed for: '{search_term}'...")
    pmids = PubMedRetriever.search_pubmed_articles(search_term, max_results)
    print(f"Found {len(pmids)} articles. Fetching details...\n")
    results = PubMedRetriever.fetch_pubmed_abstracts(pmids)

    # Print formatted summaries
    for idx, article in enumerate(results, 1):
        print(f"🧾 Article {idx}: {article['title']}")
        print(f"   PMID: {article['pmid']}")
        print(f"   Journal: {article['journal']} ({article['publication_date']})")
        print(f"   Authors: {article['authors']}")
        print(f"   Abstract summary: {next(iter(article['abstract'].values()))[:250]}...")
        print("-" * 100)

    return results