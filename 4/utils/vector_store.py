"""Vector store management for the RAG chatbot."""
from langchain_core.documents import Document
from langchain_chroma import Chroma
import config
from .embedding import OpenRouterEmbeddings


class VectorStoreManager:
    """Manages the vector store for document embeddings."""

    def __init__(self):
        """Initialize the vector store manager using OpenRouter embeddings."""
        self.embeddings = OpenRouterEmbeddings()
        
        # Fresh per-session in-memory store (created on first add)
        self.vector_store = None
    
    def add_documents(self, documents):
        """Add documents to the vector store.
        
        Args:
            documents: List of documents to add
        """
        if self.vector_store is None:
            # Create new vector store with documents
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name=config.COLLECTION_NAME
            )
        else:
            # Add to existing store
            self.vector_store.add_documents(documents)
        

    def similarity_search(self, query, k=None):
        """Perform similarity search on the vector store.
        
        Args:
            query: Search query
            k: Number of results to return (default from config)
            
        Returns:
            List of most similar documents
        """
        if self.vector_store is None:
            return []
        
        k = k or config.TOP_K_RESULTS
        return self.vector_store.similarity_search(query, k=k)
    
    def get_retriever(self, k=None):
        """Get a retriever interface for the vector store.
        
        Args:
            k: Number of results to return (default from config)
            
        Returns:
            Retriever object
        """
        if self.vector_store is None:
            return None
        
        k = k or config.TOP_K_RESULTS
        return self.vector_store.as_retriever(search_kwargs={"k": k})
    
    def get_chunks_for_file(self, file_name):
        """Return all chunks associated with a specific file name.

        This queries the underlying vector store by metadata filter
        and reconstructs `Document` objects with their original metadata.
        """
        if self.vector_store is None:
            return []
        try:
            result = self.vector_store.get(where={"file_name": file_name})
            documents = []
            raw_docs = result.get("documents", []) or []
            raw_metas = result.get("metadatas", []) or []
            for content, metadata in zip(raw_docs, raw_metas):
                documents.append(Document(page_content=content or "", metadata=metadata or {}))
            return documents
        except Exception:
            # Return empty list on any retrieval error to avoid crashing the UI
            return []
    
    def clear_store(self):
        """Clear all documents from the vector store."""
        if self.vector_store is not None:
            try:
                # Delete all documents in the current collection
                self.vector_store.delete(where={})
            except Exception:
                # Best-effort cleanup; ignore if already deleted
                pass
            self.vector_store = None
    
    def has_documents(self):
        """Return True if any documents have been added to the store."""
        return self.vector_store is not None