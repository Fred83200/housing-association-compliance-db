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
    "electrical": 7,
    "socket": 5,
    "sockets": 5,
    "fuse": 5,
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


def _score_document(content: str, search_terms: list[str]) -> int:
    normalised_content = _normalise(content)
    tokens = _tokenise_search_text(" ".join(search_terms))

    score = 0

    for token in tokens:
        if token in normalised_content:
            score += IMPORTANT_KEYWORDS.get(token, 2)

    return score


def search_documents(
    search_terms: list[str],
    limit: int = 5,
    minimum_score: int = 7,
) -> list[dict]:
    """
    Local SharePoint style document retrieval simulation

    This mimics a simple RAG retrieval step:
    - read local documents
    - extract useful keywords from the query
    - score documents using domain aware keywords
    - remove weak matches
    - return ranked document snippets
    """

    if not DOCUMENTS_DIR.exists():
        return []

    matches: list[dict] = []

    for file_path in DOCUMENTS_DIR.glob("*.txt"):
        content = _read_document(file_path)
        score = _score_document(content, search_terms)

        if score < minimum_score:
            continue

        matches.append(
            {
                "file_name": file_path.name,
                "score": score,
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
        limit=5,
        minimum_score=1,
    )