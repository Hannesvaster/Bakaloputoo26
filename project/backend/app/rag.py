import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SimpleRAG:
    def __init__(self, documents: list[dict]):
        self.documents = documents

        self.search_texts = [
            f"{doc['filename']} {doc['category']} {doc['content']}"
            for doc in documents
        ]

        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.doc_vectors = self.vectorizer.fit_transform(self.search_texts)

    def _tokenize(self, text: str) -> set[str]:
        return set(re.findall(r"\w+", text.lower()))

    def _keyword_bonus(self, query: str, doc: dict) -> float:
        query_tokens = self._tokenize(query)
        filename_tokens = self._tokenize(doc["filename"].replace(".md", ""))
        category_tokens = self._tokenize(doc["category"])

        bonus = 0.0

        filename_matches = query_tokens.intersection(filename_tokens)
        category_matches = query_tokens.intersection(category_tokens)

        bonus += 0.25 * len(filename_matches)
        bonus += 0.10 * len(category_matches)

        return bonus

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.doc_vectors).flatten()

        scored_results = []
        for idx, sim in enumerate(similarities):
            doc = self.documents[idx]
            score = float(sim) + self._keyword_bonus(query, doc)

            scored_results.append(
                {
                    "score": score,
                    "document": doc,
                }
            )

        scored_results.sort(key=lambda x: x["score"], reverse=True)

        unique_results = []
        seen = set()

        for item in scored_results:
            doc = item["document"]
            key = (doc["filename"], doc["chunk_id"])

            if key not in seen:
                seen.add(key)
                unique_results.append(item)

            if len(unique_results) >= top_k:
                break

        return unique_results