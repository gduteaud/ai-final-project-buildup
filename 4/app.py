"""Main Streamlit application for the RAG chatbot."""
import streamlit as st
from pathlib import Path
import tempfile
import config
from utils.document_processor import DocumentProcessor
from utils.vector_store import VectorStoreManager
from utils.rag import RAGSystem


# Page configuration
st.set_page_config(
    page_title="RAG Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


def _format_metadata_caption(metadata):
    """Return a compact caption showing only title/file_name and page info."""
    if not metadata:
        return ""
    title_or_file = metadata.get("title") or metadata.get("file_name")
    parts = []
    if title_or_file:
        # Prefer Title label when a real title exists
        label = "Title" if metadata.get("title") else "File"
        parts.append(f"{label}: {title_or_file}")
    total_pages = metadata.get("total_pages")
    page_label = metadata.get("page_label")
    page = metadata.get("page")
    page_str = None
    if page_label is not None:
        page_str = f"Page: {page_label}/{total_pages}" if total_pages is not None else f"Page: {page_label}"
    elif page is not None:
        page_str = f"Page: {page}/{total_pages}" if total_pages is not None else f"Page: {page}"
    if page_str:
        parts.append(page_str)
    return " | ".join(parts)


def initialize_session_state():
    """Initialize session state variables."""
    if 'vector_store_manager' not in st.session_state:
        st.session_state.vector_store_manager = VectorStoreManager()
    
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = RAGSystem(st.session_state.vector_store_manager)
    
    if 'document_processor' not in st.session_state:
        st.session_state.document_processor = DocumentProcessor()
    if 'chunk_size' not in st.session_state:
        st.session_state.chunk_size = config.CHUNK_SIZE
    if 'chunk_overlap' not in st.session_state:
        st.session_state.chunk_overlap = config.CHUNK_OVERLAP
    if 'temperature' not in st.session_state:
        st.session_state.temperature = config.TEMPERATURE
    if 'max_tokens' not in st.session_state:
        st.session_state.max_tokens = config.MAX_TOKENS
    if 'top_k_results' not in st.session_state:
        st.session_state.top_k_results = config.TOP_K_RESULTS
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'documents_loaded' not in st.session_state:
        # Fresh session starts with no documents loaded
        st.session_state.documents_loaded = False
    # Track loaded files purely in-session for UI
    if 'loaded_files' not in st.session_state:
        st.session_state.loaded_files = {}
    if 'loaded_file_samples' not in st.session_state:
        st.session_state.loaded_file_samples = {}


def display_sidebar():
    """Display the sidebar with document upload and management."""
    with st.sidebar:
        
        # API Key check
        if not config.OPENROUTER_API_KEY:
            st.error("⚠️ OpenRouter API key not found! Please set OPENROUTER_API_KEY in your .env file.")
            st.stop()
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Upload documents",
            type=config.SUPPORTED_FILE_TYPES,
            accept_multiple_files=True,
        )
        

        if uploaded_files:
            if st.button("📥 Process Documents", use_container_width=True):
                with st.spinner("Processing documents..."):
                    try:
                        all_chunks = []
                        per_file_counts = {}
                        per_file_samples = {}
                        # Use a temporary directory to store uploaded files for processing
                        with tempfile.TemporaryDirectory() as tmp_dir:
                            tmp_dir_path = Path(tmp_dir)
                            for uploaded_file in uploaded_files:
                                st.write(f"Processing: {uploaded_file.name}")
                                temp_file_path = tmp_dir_path / uploaded_file.name
                                # Write uploaded file bytes to a temporary file
                                temp_file_path.write_bytes(uploaded_file.read())
                                # Reset the file pointer in case Streamlit reuses it elsewhere
                                uploaded_file.seek(0)
                                
                                # Update processor with current chunk settings and process
                                st.session_state.document_processor.update_splitter(
                                    chunk_size=int(st.session_state.chunk_size),
                                    chunk_overlap=int(st.session_state.chunk_overlap),
                                )
                                chunks = st.session_state.document_processor.process_file(temp_file_path)
                                all_chunks.extend(chunks)
                                file_name = temp_file_path.name
                                per_file_counts[file_name] = per_file_counts.get(file_name, 0) + len(chunks)
                                # Keep up to 3 sample chunks for UI preview
                                if file_name not in per_file_samples:
                                    per_file_samples[file_name] = []
                                remaining = 3 - len(per_file_samples[file_name])
                                if remaining > 0:
                                    per_file_samples[file_name].extend(chunks[:remaining])
                        
                        # Add to vector store
                        st.session_state.vector_store_manager.add_documents(all_chunks)
                        st.session_state.documents_loaded = True
                        # Update session fallback indexes for UI
                        st.session_state.loaded_files.update(per_file_counts)
                        for k, v in per_file_samples.items():
                            st.session_state.loaded_file_samples[k] = v
                        
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error processing documents: {str(e)}")
        
        
        # Processed files overview
        st.subheader("Processed Files")
        files = [{"file_name": k, "chunk_count": v} for k, v in sorted(st.session_state.loaded_files.items())]
        if not files:   
            st.caption("No files processed.")
        else:
            for item in files:
                file_name = item.get("file_name")
                chunk_count = item.get("chunk_count", 0)
                with st.expander(f"{file_name} ({chunk_count} chunks)"):
                    # Toggle to display all chunks for this file in full
                    show_all_key = f"show_all_{file_name}"
                    show_all = st.checkbox("Show all chunks (full text)", key=show_all_key)
                    if show_all:
                        all_chunks = st.session_state.vector_store_manager.get_chunks_for_file(file_name)
                        st.caption(f"Displaying {len(all_chunks)} chunk(s) from vector store")
                        for idx, chunk_doc in enumerate(all_chunks, start=1):
                            st.markdown(f"**Chunk {idx}:**")
                            st.text(chunk_doc.page_content or "")
                            if getattr(chunk_doc, 'metadata', None):
                                caption = _format_metadata_caption(chunk_doc.metadata)
                                if caption:
                                    st.caption(caption)
                    else:
                        # Preview a few chunks (session-only)
                        preview_docs = st.session_state.loaded_file_samples.get(file_name, [])
                        for i, doc in enumerate(preview_docs, start=1):
                            st.markdown(f"**Chunk {i}:**")
                            st.text((doc.page_content or "")[:300] + ("..." if len(doc.page_content or "") > 300 else ""))
                            if getattr(doc, 'metadata', None):
                                caption = _format_metadata_caption(doc.metadata)
                                if caption:
                                    st.caption(caption)
        
        # Clear options
        st.subheader("⚙️ Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.rag_system.clear_memory()
                st.rerun()
        
        with col2:
            if st.button("🔄 Clear All", use_container_width=True):
                st.session_state.messages = []
                st.session_state.vector_store_manager.clear_store()
                st.session_state.documents_loaded = False
                st.session_state.rag_system = RAGSystem(st.session_state.vector_store_manager)
                st.session_state.loaded_files = {}
                st.session_state.loaded_file_samples = {}
                st.rerun()

        # Settings sections
        st.markdown("**Processing Settings**")
        col_chunk1, col_chunk2 = st.columns([2, 2])
        with col_chunk1:
            st.session_state.chunk_size = st.number_input(
                "Chunk Size",
                min_value=100,
                max_value=5000,
                value=int(st.session_state.chunk_size),
                step=50,
                help="Number of characters per chunk during document processing.",
            )
        with col_chunk2:
            st.session_state.chunk_overlap = st.number_input(
                "Chunk Overlap",
                min_value=0,
                max_value=2000,
                value=int(st.session_state.chunk_overlap),
                step=25,
                help="Overlap between adjacent chunks to preserve context.",
            )

        st.markdown("**Retrieval Settings**")
        st.session_state.top_k_results = st.number_input(
            "Top K Results",
            min_value=1,
            max_value=20,
            value=int(st.session_state.top_k_results),
            step=1,
            help="Number of chunks to retrieve from the vector store.",
        )

        st.markdown("**Generation Settings**")
        col_gen1, col_gen2 = st.columns([2, 2])
        with col_gen1:
            st.session_state.temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=float(st.session_state.temperature),
                step=0.05,
                help="Higher values produce more creative but less deterministic outputs.",
            )
        with col_gen2:
            st.session_state.max_tokens = st.number_input(
                "Max Tokens",
                min_value=16,
                max_value=8192,
                value=int(st.session_state.max_tokens),
                step=16,
                help="Maximum number of tokens to generate in the response.",
            )
        


def display_chat():
    """Display the chat interface."""
    st.title("🤖 RAG Chatbot")
    st.markdown("Ask questions about your uploaded documents!")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display sources if available
            if "sources" in message and message["sources"]:
                with st.expander("📄 View Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"**Source {i}:**")
                        st.text(source.page_content[:300] + "...")
                        if hasattr(source, 'metadata') and source.metadata:
                            caption = _format_metadata_caption(source.metadata)
                            if caption:
                                st.caption(caption)
                        st.divider()

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        if not st.session_state.documents_loaded:
            st.warning("⚠️ Please upload and process documents first!")
            return
        
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response from RAG chain
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.rag_system.ask(
                    prompt,
                    temperature=float(st.session_state.temperature),
                    max_tokens=int(st.session_state.max_tokens),
                    top_k_results=int(st.session_state.top_k_results),
                )
                answer = response["answer"]
                sources = response.get("source_documents", [])
                
                st.markdown(answer)
                
                # Display sources
                if sources:
                    with st.expander("📄 View Sources"):
                        for i, source in enumerate(sources, 1):
                            st.markdown(f"**Source {i}:**")
                            st.text(source.page_content[:300] + "...")
                            if hasattr(source, 'metadata') and source.metadata:
                                caption = _format_metadata_caption(source.metadata)
                                if caption:
                                    st.caption(caption)
                            st.divider()
        
        # Add assistant message to chat
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources
        })


def main():
    """Main application function."""
    initialize_session_state()
    display_sidebar()
    display_chat()


if __name__ == "__main__":
    main()

