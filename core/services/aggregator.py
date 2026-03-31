from .crossref import query_crossref
from .openalex import query_openalex
from .semantic import query_semantic
from .doi_checker import check_doi_mismatch

def verify_reference(ref):
    results = []

    for func in [query_crossref, query_openalex, query_semantic]:
        try:
            r = func(ref)
            if r:
                results.append(r)
        except Exception:
            continue

    doi_check = None

    if results and results[0].get("doi"):
        try:
            doi_check = check_doi_mismatch(
                results[0]["doi"],
                results[0]["title"]
            )
        except Exception:
            doi_check = None

    return {
        "api_results": results,
        "doi_check": doi_check
    }