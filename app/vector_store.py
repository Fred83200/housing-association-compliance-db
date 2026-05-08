import os
import numpy as np
import faiss

from app.embedding_service import get_embedding

DOCUMENTS_PATHS = ["documents/structured", "documents/unstructured"]


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100):
    """
    Splits text into overlapping chunks for better semantic retrieval.
    """
    chunks = []

    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks


class DocumentStore:

    def __init__(self):
        self.texts = []
        self.metadata = []
        self.index = None

    def initialise(self):
        print("Initialising document store...")

        self.load_documents()
        self.build_index()

        print("Document store ready.")

    def load_documents(self):
        for doc_path in DOCUMENTS_PATHS:
            for file in os.listdir(doc_path):
                if file.endswith(".txt"):
                    path = os.path.join(doc_path, file)

                    with open(path, "r") as f:
                        content = f.read()

                    chunks = chunk_text(content)

                    for chunk in chunks:
                        self.texts.append(chunk)
                        self.metadata.append({
                            "file": file
                        })

    def build_index(self):
        if not self.texts:
            raise ValueError("No documents loaded")

        print(f"Building embeddings for {len(self.texts)} chunks...")

        embeddings = [get_embedding(t) for t in self.texts]
        vectors = np.array(embeddings).astype("float32")

        dim = vectors.shape[1]

        self.index = faiss.IndexFlatL2(dim)
        self.index.add(vectors)

        print("Vector index built successfully.")

    def search(self, query: str, k: int = 3):
        if self.index is None:
            raise RuntimeError("Vector store not initialised")

        query_embedding = np.array(
            [get_embedding(query)]
        ).astype("float32")

        distances, indices = self.index.search(query_embedding, k)

        results = []

        for i in indices[0]:
            results.append({
                "text": self.texts[i],
                "metadata": self.metadata[i]
            })

        return results


doc_store = DocumentStore()
