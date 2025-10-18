"""Embedding helper using Jina AI Embeddings API.

Provides a LangChain-compatible Embeddings implementation so it can be plugged into vector stores like Chroma.
"""
import requests
import config


class JinaEmbeddings:
    """Minimal Embeddings adapter for Jina AI's embeddings endpoint.

    Implements the subset of the LangChain Embeddings interface used by vector stores: embed_documents and embed_query.
    """

    def __init__(
        self,
        api_key=None,
        model=None,
        task=None,
        base_url="https://api.jina.ai/v1/embeddings",
    ):
        self.api_key = api_key or config.EMBEDDING_API_KEY
        if not self.api_key:
            raise ValueError("Embedding API key required. Set EMBEDDING_API_KEY in .env")

        # Defaults mirror 3/config.py changes
        self.model = model or getattr(config, "EMBEDDING_MODEL", "jina-embeddings-v3")
        self.task = task or getattr(config, "EMBEDDING_TASK", "text-matching")
        self.base_url = base_url

    def _headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def _post(self, inputs):
        if not inputs:
            return []

        payload = {
            "model": self.model,
            "input": inputs,
            "task": self.task,
        }

        response = requests.post(self.base_url, headers=self._headers(), json=payload, timeout=60)
        if response.status_code != 200:
            raise RuntimeError(f"Jina embeddings API error: {response.status_code} {response.text}")
        data = response.json() or {}
        items = data.get("data", [])
        embeddings = []
        for item in items:
            emb = item.get("embedding")
            if isinstance(emb, list):
                embeddings.append(emb)
        if len(embeddings) != len(inputs):
            # Best-effort: pad/truncate to maintain alignment
            min_len = min(len(embeddings), len(inputs))
            embeddings = embeddings[:min_len]
        return embeddings

    def embed_documents(self, texts):
        """Return embeddings for a list of texts."""
        normalized = [(t or "").strip() for t in texts]
        if not any(normalized):
            return [[] for _ in normalized]
        return self._post(normalized)

    def embed_query(self, text):
        """Return embedding for a single query string."""
        results = self._post([text or ""])
        return results[0] if results else []


