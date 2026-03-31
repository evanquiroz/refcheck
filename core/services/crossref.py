import requests

def query_crossref(ref):
    url = "https://api.crossref.org/works"
    params = {"query.bibliographic": ref, "rows": 1}

    r = requests.get(url, params=params)
    data = r.json()

    if data["message"]["items"]:
        item = data["message"]["items"][0]
        return {
            "source": "Crossref",
            "title": item.get("title", [""])[0],
            "doi": item.get("DOI"),
            "url": item.get("URL")
        }
    return None