import requests

def check_doi_mismatch(doi, title):
    if not doi:
        return None

    url = f"https://api.crossref.org/works/{doi}"
    r = requests.get(url)

    if r.status_code != 200:
        return {"valid": False}

    official = r.json()["message"]["title"][0]

    from difflib import SequenceMatcher
    score = SequenceMatcher(None, title.lower(), official.lower()).ratio()

    return {"valid": score > 0.6, "score": score}