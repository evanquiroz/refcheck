from difflib import SequenceMatcher

def detect_hallucination(ref, results):
    if not results:
        return {"status": "Hallucinated", "confidence": 0.0}

    scores = [
        SequenceMatcher(None, ref.lower(), r["title"].lower()).ratio()
        for r in results if r.get("title")
    ]

    max_score = max(scores) if scores else 0

    if max_score < 0.5:
        return {"status": "Likely Fake", "confidence": max_score}

    return {"status": "Valid", "confidence": max_score}