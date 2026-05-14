import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

from app.embedding_service import get_embedding

INDEX_NAME = "housing-compliance-docs"

_client = None


def _get_client() -> SearchClient:
    global _client
    if _client is None:
        endpoint = os.getenv("SEARCH_ENDPOINT")
        api_key = os.getenv("SEARCH_API_KEY")
        if not endpoint or not api_key:
            raise RuntimeError("SEARCH_ENDPOINT and SEARCH_API_KEY must be set")
        _client = SearchClient(
            endpoint=endpoint,
            index_name=INDEX_NAME,
            credential=AzureKeyCredential(api_key),
        )
    return _client


def _get_confidence(score: float) -> str:
    if score >= 5.0:
        return "high"
    if score >= 2.0:
        return "medium"
    return "low"


def search_documents(
    search_terms: list[str],
    limit: int = 5,
    minimum_score: float | None = None,
) -> list[dict]:
    if minimum_score is None:
        minimum_score = 0.5

    search_text = " ".join(search_terms)
    embedding = get_embedding(search_text)

    vector_query = VectorizedQuery(
        vector=embedding,
        k_nearest_neighbors=limit,
        fields="embedding",
    )

    results = _get_client().search(
        search_text=search_text,
        vector_queries=[vector_query],
        top=limit,
    )

    matches = []
    for r in results:
        score = r.get("@search.score", 0)
        if score < minimum_score:
            continue
        matches.append({
            "file_name": r.get("file_name", ""),
            "relative_path": r.get("relative_path", ""),
            "document_source_type": r.get("document_type", "unknown"),
            "score": round(score * 3),
            "confidence": _get_confidence(score),
            "content_preview": (r.get("content") or "")[:700],
        })

    return matches


def search_documents_for_property(
    property_id: int,
    uprn: str | None = None,
    postcode: str | None = None,
    extra_terms: list[str] | None = None,
) -> list[dict]:
    search_terms = [f"Property ID: {property_id}"]
    if uprn:
        search_terms.append(uprn)
    if postcode:
        search_terms.append(postcode)
    if extra_terms:
        search_terms.extend(t for t in extra_terms if t)

    return search_documents(
        search_terms=search_terms,
        limit=10,
        minimum_score=0.3,
    )
