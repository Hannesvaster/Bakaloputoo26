import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SimpleRAG:
    def __init__(self, documents: list[dict]):
        self.documents = documents

        self.synonyms = {
            "sihtrühm": "sihtryhm",
            "sihtgrupp": "sihtryhm",
            "sihtgrupi": "sihtryhm",
            "hind": "hinnastamine",
            "hinna": "hinnastamine",
            "hinnakujundus": "hinnastamine",
            "ettevõtlusvorm": "ou fie",
            "ettevõttevorm": "ou fie",
            "osaühing": "ou",
            "füüsilisest": "fie",
            "ettevõtja": "ettevotja",
        }

        self.search_texts = [
            f"{doc['filename']} {doc['category']} {doc['content']}"
            for doc in documents
        ]

        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.doc_vectors = self.vectorizer.fit_transform(self.search_texts)

    def _tokenize(self, text: str) -> set[str]:
        return set(re.findall(r"\w+", text.lower()))

    def _normalize_query(self, query: str) -> str:
        normalized = query.lower()
        for source, target in self.synonyms.items():
            normalized = normalized.replace(source, target)
        return normalized

    def _keyword_bonus(self, query: str, doc: dict) -> float:
        query_tokens = self._tokenize(query)
        filename_tokens = self._tokenize(doc["filename"].replace(".md", ""))
        category_tokens = self._tokenize(doc["category"])

        bonus = 0.0
        bonus += 0.30 * len(query_tokens.intersection(filename_tokens))
        bonus += 0.10 * len(query_tokens.intersection(category_tokens))

        return bonus

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        normalized_query = self._normalize_query(query)

        query_vector = self.vectorizer.transform([normalized_query])
        similarities = cosine_similarity(query_vector, self.doc_vectors).flatten()

        scored_results = []
        for idx, sim in enumerate(similarities):
            doc = self.documents[idx]
            score = float(sim) + self._keyword_bonus(normalized_query, doc)

            scored_results.append(
                {
                    "score": score,
                    "document": doc,
                }
            )

        scored_results.sort(key=lambda x: x["score"], reverse=True)

        unique_results = []
        seen_filenames = set()

        for item in scored_results:
            doc = item["document"]
            filename = doc["filename"]

            if filename not in seen_filenames:
                seen_filenames.add(filename)
                unique_results.append(item)

            if len(unique_results) >= top_k:
                break

        return unique_results