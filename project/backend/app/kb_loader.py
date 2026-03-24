from pathlib import Path


def load_knowledge_base(base_path: str = "../knowledge_base") -> list[dict]:
    base = Path(base_path)
    docs = []

    for file_path in base.rglob("*.md"):
        try:
            content = file_path.read_text(encoding="utf-8")
            docs.append(
                {
                    "path": str(file_path),
                    "filename": file_path.name,
                    "category": file_path.parent.name,
                    "content": content,
                }
            )
        except Exception as e:
            print(f"Viga faili lugemisel {file_path}: {e}")

    return docs