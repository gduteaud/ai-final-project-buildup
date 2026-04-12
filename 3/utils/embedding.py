"""Embedding helper using OpenRouter's embeddings API.

Provides a LangChain-compatible Embeddings implementation so it can be plugged into vector stores like Chroma.
"""
import requests
import config


class OpenRouterEmbeddings:
    """Minimal Embeddings adapter for OpenRouter's embeddings endpoint.

    Implements the subset of the LangChain Embeddings interface used by vector stores: embed_documents and embed_query.
    """

    def __init__(
        self,
        api_key=None,
        model=None,
        base_url=None,
    ):
        self.api_key = api_key or config.OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key required. Set OPENROUTER_API_KEY in the project root `.env`."
            )

        self.model = model or getattr(config, "EMBEDDING_MODEL", "openai/text-embedding-3-small")
        self.base_url = base_url or f"{config.OPENROUTER_BASE_URL}/embeddings"

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
        }

        response = requests.post(self.base_url, headers=self._headers(), json=payload, timeout=60)
        if response.status_code != 200:
            raise RuntimeError(f"OpenRouter embeddings API error: {response.status_code} {response.text}")
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
