def compute_score(ref, parsed_input=None, confidence=1.0):
    """
    Computes score with a 50-point bonus if Title, Year, and Authors match 
    the user's input.
    """
    if not isinstance(ref, dict):
        return 0, {}

    score = 0
    breakdown = {}

    # --- 1. BASE ATTRIBUTE SCORING ---
    if ref.get("title"):
        score += 25
        breakdown["title_found"] = 25

    if ref.get("doi"):
        score += 35
        breakdown["doi_found"] = 35

    if ref.get("authors"):
        score += 20
        breakdown["authors_found"] = 20

    if ref.get("year"):
        score += 10
        breakdown["year_found"] = 10

    if ref.get("journal"):
        score += 10
        breakdown["journal_found"] = 10

    # --- 2. THE TRIPLE MATCH REWARD (+50 Points) ---
    # We check if the found record matches the user's parsed input
    if parsed_input:
        match_title = False
        match_year = False
        match_author = False

        # Title Match (Fuzzy: check first 30 chars)
        if ref.get("title") and parsed_input.get("title"):
            if parsed_input["title"].lower()[:30] in ref["title"].lower():
                match_title = True

        # Year Match
        if str(ref.get("year")) == str(parsed_input.get("year")):
            match_year = True

        # Author Match (Check if at least one author family name exists in input)
        if ref.get("authors") and parsed_input.get("raw"):
            # Simple check: is one of the registry authors mentioned in the raw text?
            if any(str(auth).lower() in parsed_input["raw"].lower() for auth in ref["authors"]):
                match_author = True

        # IF ALL THREE MATCH: Add 50 points
        if match_title and match_year and match_author:
            score += 50
            breakdown["triple_match_bonus"] = 50

    # --- 3. CONFIDENCE & FINAL CALCULATION ---
    confidence = float(confidence or 1.0)
    score *= min(max(confidence, 0.5), 1.2)

    # Cap at 100
    score = round(max(0, min(100, score)), 2)
    breakdown["final"] = score

    return score, breakdown