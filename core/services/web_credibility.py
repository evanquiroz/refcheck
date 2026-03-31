from urllib.parse import urlparse
import re

def is_valid_url(text):
    """Check if string is a proper URL"""
    return isinstance(text, str) and text.startswith(("http://", "https://"))


def extract_domain(url):
    """Safely extract domain without crashing"""
    try:
        parsed = urlparse(url)
        return parsed.netloc if parsed.netloc else None
    except Exception:
        return None


def is_doi(text):
    """Basic DOI detection"""
    if not isinstance(text, str):
        return False

    return bool(re.match(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", text, re.I))


def check_website_credibility(ref):
    """
    Safe web credibility checker
    Handles:
    - URLs
    - DOIs
    - plain text (ignored safely)
    """

    if not isinstance(ref, str):
        return {
            "type": "invalid",
            "status": "non-string input",
            "score": 0
        }

    ref = ref.strip()

    # =========================
    # CASE 1: URL
    # =========================
    if is_valid_url(ref):
        domain = extract_domain(ref)

        if not domain:
            return {
                "type": "url",
                "status": "invalid-url",
                "domain": None,
                "score": 0
            }

        # simple heuristic scoring
        score = 70

        if ".gov" in domain or ".edu" in domain:
            score = 90
        elif ".org" in domain:
            score = 75
        elif ".com" in domain:
            score = 60

        return {
            "type": "url",
            "status": "valid-url",
            "domain": domain,
            "score": score
        }

    # =========================
    # CASE 2: DOI
    # =========================
    if is_doi(ref):
        return {
            "type": "doi",
            "status": "valid-doi-format",
            "domain": "doi.org",
            "score": 85
        }

    # =========================
    # CASE 3: Plain text / citation
    # =========================
    return {
        "type": "text",
        "status": "non-url-reference",
        "domain": None,
        "score": 0
    }