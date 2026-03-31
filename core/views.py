from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json, re, requests

def index(request):
    return render(request, "index.html")

def parse_reference(raw_ref):
    text = " ".join(raw_ref.split())
    if not text: return None
    
    # --- VALIDATION GUARDS ---
    # 1. Check length (Minimum 15 characters for a realistic reference)
    if len(text) < 15: 
        return {"raw": text, "invalid": True}
    
    # 2. Check word count (At least 3 words)
    if len(text.split()) < 3:
        return {"raw": text, "invalid": True}

    # 3. Look for "Reference-like" patterns
    all_years = re.findall(r'(19|20)\d{2}', text)
    extracted_year = all_years[-1] if all_years else None
    doi_match = re.search(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", text, re.I)
    extracted_doi = doi_match.group(0) if doi_match else None
    
    # If no year, no DOI, and short text, it's likely gibberish
    if not extracted_year and not extracted_doi and len(text) < 40:
        return {"raw": text, "invalid": True}

    return {
        "raw": text, 
        "invalid": False, 
        "title": text, 
        "authors": [], 
        "year": extracted_year or "N/A", 
        "doi": extracted_doi
    }

def crossref_lookup(title=None, doi=None):
    try:
        url = f"https://api.crossref.org/works/{doi}" if doi else f"https://api.crossref.org/works?query.bibliographic={requests.utils.quote(title)}&rows=1"
        r = requests.get(url, timeout=5, headers={'User-Agent': 'RefCheck/1.0'})
        if r.status_code != 200: return None
        msg = r.json()["message"]
        item = msg if "DOI" in msg else (msg["items"][0] if msg.get("items") else None)
        if not item: return None
        return {
            "title": item.get("title", [""])[0],
            "year": str(item.get("issued", {}).get("date-parts", [[None]])[0][0]),
            "doi": item.get("DOI"), 
            "journal": item.get("container-title", [""])[0],
            "authors": [a.get("family", "") for a in item.get("author", [])]
        }
    except: return None

@csrf_exempt
def check_refs(request):
    if request.method != "POST": return JsonResponse({"error": "POST required"}, status=405)
    
    try:
        data = json.loads(request.body.decode("utf-8"))
    except:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
        
    references = data.get("references", [])
    results, verified_count = [], 0

    for ref in references:
        parsed = parse_reference(ref)
        
        # --- NEW GUARD CLAUSE ---
        # If the parser flagged it as invalid, skip CrossRef lookup
        if not parsed or parsed.get("invalid"):
            results.append({
                "raw": ref,
                "authors": "N/A",
                "title": "Invalid reference format detected",
                "year": "N/A",
                "doi": "",
                "journal": "N/A",
                "score": 0,
                "status_label": "Invalid" # Triggers Orange in your JS
            })
            continue

        # Normal Lookup Process
        found = crossref_lookup(title=parsed["title"], doi=parsed["doi"])
        
        score = 0
        if found:
            score = 60 # Match found
            if found.get("doi"): score += 20
            if str(parsed["year"]) in str(found.get("year")): score += 20
        
        # Determine Label based on Score
        if score >= 80:
            status = "Verified"
            verified_count += 1
        elif 1 <= score < 80:
            status = "Not Verified"
        else:
            status = "Invalid"

        results.append({
            "raw": ref,
            "authors": ", ".join(found["authors"]) if found else "Unknown",
            "title": found["title"] if found else parsed["title"],
            "year": found["year"] if found else parsed["year"],
            "doi": found["doi"] if found else "",
            "journal": found["journal"] if found else "",
            "score": score,
            "status_label": status
        })

    total = len(references)
    return JsonResponse({
        "overall_score": round((verified_count / total * 100) if total > 0 else 0, 1),
        "total_references": total,
        "verified_references": verified_count,
        "results": results
    })