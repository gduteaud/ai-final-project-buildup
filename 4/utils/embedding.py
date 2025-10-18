"""Embedding helper using Jina AI Embeddings API.

Provides a LangChain-compatible Embeddings implementation so it can be plugged into vector stores like Chroma.

It does this by exposing a tiny class with just two methods that vector stores need:
- embed_documents(list[str]) -> list[list[float]]
- embed_query(str) -> list[float]

"""
import requests
import config


class JinaEmbeddings:
    """Minimal Embeddings adapter for Jina AI's embeddings endpoint.

    Implements the subset of the LangChain Embeddings interface used by vector stores: embed_documents and embed_query.
    """

    def __init__(self):
        # Read all settings directly from config so we don't have to pass them in
        self.api_key = config.EMBEDDING_API_KEY
        if not self.api_key:
            raise ValueError("Embedding API key required. Set EMBEDDING_API_KEY in .env")

        self.model = getattr(config, "EMBEDDING_MODEL", "jina-embeddings-v3")
        self.task = getattr(config, "EMBEDDING_TASK", "text-matching")
        self.base_url = "https://api.jina.ai/v1/embeddings"

    def _request_embeddings(self, inputs):
        """Call the API and return a list of embedding vectors for inputs."""
        if not inputs:
            return []

        payload = {"model": self.model, "input": inputs, "task": self.task}
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        resp = requests.post(self.base_url, headers=headers, json=payload, timeout=60)
        if resp.status_code != 200:
            raise RuntimeError(f"Jina embeddings API error: {resp.status_code} {resp.text}")

        data = resp.json() or {}
        items = data.get("data", [])
        return [item.get("embedding", []) for item in items]

    def embed_documents(self, texts):
        """Return embeddings for a list of texts (same order and length)."""
        normalized = [(t or "").strip() for t in texts]
        if not any(normalized):
            # Keep lengths aligned with input even if all are empty
            return [[] for _ in normalized]
        return self._request_embeddings(normalized)

    def embed_query(self, text):
        """Return embedding for a single query string."""
        results = self._request_embeddings([text or ""])
        return results[0] if results else []

