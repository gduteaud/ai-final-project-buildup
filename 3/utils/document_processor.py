# In utils/document_processor.py
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    BSHTMLLoader
)
from langchain_core.documents import Document
import config


class DocumentProcessor:
    """Handles document loading and processing."""
    
    def __init__(self, chunk_size=None, chunk_overlap=None):
        """Initialize the document processor with text splitter.

        If ``chunk_size``/``chunk_overlap`` are not provided, fall back to config defaults.
        """
        self.chunk_size = chunk_size if chunk_size is not None else config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap if chunk_overlap is not None else config.CHUNK_OVERLAP
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )

    def update_splitter(self, chunk_size=None, chunk_overlap=None):
        """Update the splitter configuration at runtime."""
        if chunk_size is not None:
            self.chunk_size = int(chunk_size)
        if chunk_overlap is not None:
            self.chunk_overlap = int(chunk_overlap)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )
    
    def load_pdf(self, file_path):
        """Load and process a PDF file."""
        loader = PyPDFLoader(str(file_path))
        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)
        return self._annotate_with_file_metadata(file_path, chunks)
    
    def load_text(self, file_path):
        """Load and process a text file."""
        loader = TextLoader(str(file_path), encoding='utf-8')
        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)
        return self._annotate_with_file_metadata(file_path, chunks)
    
    def load_docx(self, file_path):
        """Load and process a Word document."""
        loader = Docx2txtLoader(str(file_path))
        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)
        return self._annotate_with_file_metadata(file_path, chunks)
    
    def load_markdown(self, file_path):
        """Load and process a Markdown file."""
        # For Markdown, we can use TextLoader since it's plain text
        loader = TextLoader(str(file_path), encoding='utf-8')
        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)
        return self._annotate_with_file_metadata(file_path, chunks)
    
    def load_html(self, file_path):
        """Load and process an HTML file."""
        loader = BSHTMLLoader(str(file_path))
        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)
        return self._annotate_with_file_metadata(file_path, chunks)
    
    def process_file(self, file_path):
        """Process a file based on its extension."""
        suffix = file_path.suffix.lower()
        
        if suffix == '.pdf':
            return self.load_pdf(file_path)
        elif suffix == '.txt':
            return self.load_text(file_path)
        elif suffix == '.docx':
            return self.load_docx(file_path)
        elif suffix == '.md':
            return self.load_markdown(file_path)
        elif suffix == '.html' or suffix == '.htm':
            return self.load_html(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

    def _annotate_with_file_metadata(self, file_path, documents):
        """Annotate each chunk with consistent file metadata for management.

        Adds:
        - file_name: basename of the uploaded file (stable for filtering)
        - source_path: absolute/temporary path used during processing (informational)
        """
        file_name = file_path.name
        source_path = str(file_path)
        for doc in documents:
            # Ensure metadata exists and annotate
            metadata = doc.metadata or {}
            metadata["file_name"] = file_name
            # Preserve original loader-provided source if present; also add explicit path
            metadata.setdefault("source", metadata.get("source", source_path))
            metadata["source_path"] = source_path
            doc.metadata = metadata
        return documents