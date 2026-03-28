from pathlib import Path


def split_into_chunks(text: str, max_paragraphs: int = 2) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []

    for i in range(0, len(paragraphs), max_paragraphs):
        chunk = "\n\n".join(paragraphs[i:i + max_paragraphs])
        if chunk:
            chunks.append(chunk)

    return chunks


def load_knowledge_base(base_path: str) -> list[dict]:
    base = Path(base_path)
    docs = []

    for file_path in base.rglob("*.md"):
        content = file_path.read_text(encoding="utf-8")
        chunks = split_into_chunks(content)

        for idx, chunk in enumerate(chunks):
            docs.append(
                {
                    "filename": file_path.name,
                    "category": file_path.parent.name,
                    "content": chunk,
                    "path": str(file_path),
                    "chunk_id": idx,
                }
            )

    return docs