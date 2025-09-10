import os
from typing import List

from django.conf import settings

from .models import Document, Chunk


def load_embedder():
    try:
        from sentence_transformers import SentenceTransformer  # local import to avoid startup cost
    except Exception:
        return None
    try:
        return SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    except Exception:
        return None


def _chunk_text(text: str, max_chars: int = 800) -> List[str]:
    parts = []
    buf = []
    total = 0
    for line in text.splitlines():
        if total + len(line) > max_chars:
            parts.append("\n".join(buf).strip())
            buf, total = [], 0
        buf.append(line)
        total += len(line)
    if buf:
        parts.append("\n".join(buf).strip())
    return [p for p in parts if p]


def ingest_path(path: str, source: str = 'local') -> int:
    """Ingest all .txt and .md files from a folder path."""
    count = 0
    embedder = load_embedder()
    for root, _, files in os.walk(path):
        for fname in files:
            if not (fname.endswith('.txt') or fname.endswith('.md')):
                continue
            fpath = os.path.join(root, fname)
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            doc = Document.objects.create(title=fname, source=source)
            chunks = _chunk_text(text)
            vectors = None
            if embedder and chunks:
                try:
                    vectors = embedder.encode(chunks).tolist()
                except Exception:
                    vectors = None
            for i, ch in enumerate(chunks):
                vec = vectors[i] if vectors else None
                Chunk.objects.create(document=doc, text=ch, order=i, embedding=vec)
                count += 1
    return count
