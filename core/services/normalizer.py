def normalize_reference(data, source="crossref"):

    if not isinstance(data, dict):
        return {}

    def first(x):
        if isinstance(x, list) and x:
            return x[0]
        return x

    # ---------------- CROSSREF ----------------
    if source == "crossref":
        return {
            "title": first(data.get("title", "")),
            "doi": data.get("DOI") or data.get("doi", ""),
            "authors": [
                f"{a.get('given','')} {a.get('family','')}".strip()
                for a in data.get("author", [])
                if isinstance(a, dict)
            ],
            "year": (
                data.get("published-print", {}).get("date-parts", [[None]])[0][0]
                or data.get("published-online", {}).get("date-parts", [[None]])[0][0]
            ),
            "journal": first(data.get("container-title", []))
        }

    # ---------------- OPENALEX ----------------
    if source == "openalex":
        return {
            "title": data.get("title", ""),
            "doi": (data.get("doi", "") or "").replace("https://doi.org/", ""),
            "authors": [
                a.get("author", {}).get("display_name", "")
                for a in data.get("authorships", [])
                if isinstance(a, dict)
            ],
            "year": data.get("publication_year"),
            "journal": data.get("host_venue", {}).get("display_name", "")
        }

    return {}