from pathlib import Path


DOCUMENTS_DIR = Path("documents")

STOP_WORDS = {
    "show",
    "me",
    "find",
    "about",
    "the",
    "a",
    "an",
    "for",
    "with",
    "and",
    "or",
    "to",
    "of",
    "in",
    "on",
    "documents",
    "document",
    "reports",
    "report",
    "notes",
    "note",
    "linked",
}

GENERIC_WORDS = {
    "report",
    "reports",
    "inspection",
    "inspections",
    "document",
    "documents",
    "notes",
    "note",
    "property",
    "properties",
    "repair",
    "repairs",
    "contractor",
    "contractors",
}

IMPORTANT_KEYWORDS = {
    "boiler": 7,
    "heating": 5,
    "hot": 3,
    "water": 3,
    "fire": 7,
    "safety": 5,
    "damp": 7,
    "mould": 7,
    "mold": 7,
    "electrical": 7,
    "electric": 7,
    "socket": 5,
    "sockets": 5,
    "fuse": 5,
    "door": 4,
    "tenant": 3,
    "resident": 3,
    "postcode": 3,
    "uprn": 3,
    "condensation": 5,
    "bedroom": 3,
    "valve": 3,
    "pressure": 3,
}

SYNONYMS = {
    "mould": ["mold", "damp", "condensation", "black marks"],
    "mold": ["mould", "damp", "condensation", "black marks"],
    "damp": ["mould", "mold", "condensation", "black marks"],
    "boiler": ["heating", "hot water", "pressure", "valve"],
    "heating": ["boiler", "hot water"],
    "fire": ["fire door", "door closer", "safety"],
    "safety": ["fire", "inspection", "compliance"],
    "electrical": ["electric", "socket", "sockets", "fuse", "fuse board"],
    "electric": ["electrical", "socket", "sockets", "fuse", "fuse board"],
}


def _normalise(value: str) -> str:
    return value.lower().strip()


def _tokenise_search_text(search_text: str) -> list[str]:
    cleaned = (
        search_text.lower()
        .replace("-", " ")
        .replace("_", " ")
        .replace(",", " ")
        .replace(".", " ")
        .replace(":", " ")
        .replace("?", " ")
        .replace("(", " ")
        .replace(")", " ")
        .replace("/", " ")
    )

    tokens: list[str] = []

    for token in cleaned.split():
        token = token.strip()

        if not token:
            continue

        if token in STOP_WORDS:
            continue

        if token in GENERIC_WORDS:
            continue

        if len(token) < 3:
            continue

        tokens.append(token)

    return tokens


def _read_document(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")


def _get_document_type(file_path: Path) -> str:
    relative_path = file_path.relative_to(DOCUMENTS_DIR)

    if "structured" in relative_path.parts:
        return "structured"

    if "unstructured" in relative_path.parts:
        return "unstructured"

    return "unknown"


def _get_confidence(score: int) -> str:
    if score >= 15:
        return "high"

    if score >= 7:
        return "medium"

    return "low"


def _score_document(content: str, search_terms: list[str]) -> int:
    normalised_content = _normalise(content)
    combined_search_text = " ".join(search_terms)
    tokens = _tokenise_search_text(combined_search_text)

    score = 0

    for term in search_terms:
        normalised_term = _normalise(term)

        if not normalised_term:
            continue

        if normalised_term in normalised_content:
            score += 10

    for token in tokens:
        if token in normalised_content:
            if token.startswith("uprn"):
                score += 20
            elif any(char.isdigit() for char in token) and len(token) >= 5:
                score += 12
            else:
                score += IMPORTANT_KEYWORDS.get(token, 2)

        for synonym in SYNONYMS.get(token, []):
            if synonym in normalised_content:
                score += 2

    return score


def search_documents(
    search_terms: list[str],
    limit: int = 5,
    minimum_score: int | None = None,
) -> list[dict]:
    if not DOCUMENTS_DIR.exists():
        return []

    combined_search_text = " ".join(search_terms).lower()

    if minimum_score is None:
        if any(
            word in combined_search_text
            for word in ["mould", "mold", "damp", "boiler", "heating", "fire", "electrical", "electric"]
        ):
            minimum_score = 6
        elif any(char.isdigit() for char in combined_search_text):
            minimum_score = 10
        else:
            minimum_score = 8

    matches: list[dict] = []

    for file_path in DOCUMENTS_DIR.rglob("*.txt"):
        content = _read_document(file_path)
        score = _score_document(content, search_terms)

        if score < minimum_score:
            continue

        relative_path = file_path.relative_to(DOCUMENTS_DIR)

        matches.append(
            {
                "file_name": file_path.name,
                "relative_path": str(relative_path),
                "document_source_type": _get_document_type(file_path),
                "score": score,
                "confidence": _get_confidence(score),
                "content_preview": content[:700],
            }
        )

    matches.sort(key=lambda item: item["score"], reverse=True)

    return matches[:limit]


def search_documents_for_property(
    property_id: int,
    uprn: str | None = None,
    postcode: str | None = None,
    extra_terms: list[str] | None = None,
) -> list[dict]:
    search_terms = [
        f"Property ID: {property_id}",
    ]

    if uprn:
        search_terms.append(uprn)

    if postcode:
        search_terms.append(postcode)

    if extra_terms:
        search_terms.extend(extra_terms)

    return search_documents(
        search_terms=search_terms,
        limit=10,
        minimum_score=10,
    )