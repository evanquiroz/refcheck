import requests

def query_openalex(ref):
    url = "https://api.openalex.org/works"
    params = {"search": ref}

    r = requests.get(url, params=params)
    data = r.json()

    if data["results"]:
        item = data["results"][0]
        return {
            "source": "OpenAlex",
            "title": item.get("display_name"),
            "url": item.get("id")
        }
    return None