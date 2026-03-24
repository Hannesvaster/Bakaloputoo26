from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SimpleRAG:
    def __init__(self, documents: list[dict]):
        self.documents = documents
        self.vectorizer = TfidfVectorizer()
        self.doc_texts = [doc["content"] for doc in documents]
        self.doc_vectors = self.vectorizer.fit_transform(self.doc_texts)

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.doc_vectors).flatten()

        ranked_indices = similarities.argsort()[::-1][:top_k]

        results = []
        for idx in ranked_indices:
            results.append(
                {
                    "score": float(similarities[idx]),
                    "document": self.documents[idx],
                }
            )
        return results