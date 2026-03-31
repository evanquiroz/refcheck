import requests

def query_semantic(ref):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {"query": ref, "limit": 1, "fields": "title,url"}

    r = requests.get(url, params=params)
    data = r.json()

    if data.get("data"):
        item = data["data"][0]
        return {
            "source": "Semantic",
            "title": item.get("title"),
            "url": item.get("url")
        }
    return None