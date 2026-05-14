import os
from pathlib import Path

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchableField,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from azure.search.documents.models import VectorizedQuery

from app.embedding_service import get_embedding

DOCUMENTS_PATHS = [Path("documents/structured"), Path("documents/unstructured")]
INDEX_NAME = "housing-compliance-docs"


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + chunk_size])
        start += chunk_size - overlap
    return chunks


def _credentials():
    endpoint = os.getenv("SEARCH_ENDPOINT")
    if not endpoint:
        raise RuntimeError("SEARCH_ENDPOINT must be set")
    if os.getenv("AZURE_KEYVAULT_URI"):
        from app.key_vault import get_secret
        api_key = get_secret("search-api-key")
    else:
        api_key = os.getenv("SEARCH_API_KEY")
        if not api_key:
            raise RuntimeError("SEARCH_API_KEY must be set")
    return endpoint, AzureKeyCredential(api_key)


class DocumentStore:

    def __init__(self):
        self._search_client: SearchClient | None = None

    def initialise(self):
        print("Initialising Azure AI Search document store...")

        endpoint, credential = _credentials()
        index_client = SearchIndexClient(endpoint=endpoint, credential=credential)
        self._ensure_index(index_client)

        self._search_client = SearchClient(
            endpoint=endpoint,
            index_name=INDEX_NAME,
            credential=credential,
        )

        # Only ingest documents if the index is empty
        sample = list(self._search_client.search("*", top=1))
        if not sample:
            self._index_documents()

        print("Document store ready.")

    def _ensure_index(self, index_client: SearchIndexClient):
        existing = [i.name for i in index_client.list_indexes()]
        if INDEX_NAME in existing:
            return

        print(f"Creating search index '{INDEX_NAME}'...")
        dim = len(get_embedding("probe"))

        index = SearchIndex(
            name=INDEX_NAME,
            fields=[
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SearchableField(
                    name="content",
                    type=SearchFieldDataType.String,
                    analyzer_name="en.microsoft",
                ),
                SimpleField(
                    name="file_name",
                    type=SearchFieldDataType.String,
                    filterable=True,
                    retrievable=True,
                ),
                SimpleField(
                    name="relative_path",
                    type=SearchFieldDataType.String,
                    filterable=True,
                    retrievable=True,
                ),
                SimpleField(
                    name="document_type",
                    type=SearchFieldDataType.String,
                    filterable=True,
                    retrievable=True,
                ),
                SearchField(
                    name="embedding",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    vector_search_dimensions=dim,
                    vector_search_profile_name="hnsw-profile",
                ),
            ],
            vector_search=VectorSearch(
                algorithms=[HnswAlgorithmConfiguration(name="hnsw")],
                profiles=[
                    VectorSearchProfile(
                        name="hnsw-profile",
                        algorithm_configuration_name="hnsw",
                    )
                ],
            ),
        )
        index_client.create_index(index)
        print("Index created.")

    def _index_documents(self):
        documents = []
        doc_id = 0

        for doc_path in DOCUMENTS_PATHS:
            if not doc_path.exists():
                continue
            for file in sorted(doc_path.glob("*.txt")):
                content = file.read_text(encoding="utf-8")
                doc_type = "structured" if "structured" in str(file) else "unstructured"
                relative = str(file.relative_to(doc_path.parent))

                for chunk in chunk_text(content):
                    documents.append({
                        "id": str(doc_id),
                        "content": chunk,
                        "file_name": file.name,
                        "relative_path": relative,
                        "document_type": doc_type,
                        "embedding": get_embedding(chunk),
                    })
                    doc_id += 1

        if not documents:
            print("No documents found to index.")
            return

        print(f"Indexing {len(documents)} chunks to Azure AI Search...")
        for i in range(0, len(documents), 100):
            self._search_client.upload_documents(documents[i : i + 100])
        print("Indexing complete.")

    def search(self, query: str, k: int = 3) -> list[dict]:
        if self._search_client is None:
            raise RuntimeError("Document store not initialised")

        vector_query = VectorizedQuery(
            vector=get_embedding(query),
            k_nearest_neighbors=k,
            fields="embedding",
        )
        results = self._search_client.search(
            search_text=query,
            vector_queries=[vector_query],
            top=k,
        )
        return [
            {"text": r["content"], "metadata": {"file": r["file_name"]}}
            for r in results
        ]


doc_store = DocumentStore()
