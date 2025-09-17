import logging
import hashlib
import streamlit as st
from typing import Optional
from .document_processor import DocumentProcessor
from .vector_store import VectorStoreManager
from .openai_client import OpenAIClientManager

logger = logging.getLogger(__name__)

class RAGResearchAssistant:
    """Main RAG Research Assistant application"""
    
    def __init__(self, a4f_api_key: str, a4f_base_url: str):
        self.document_processor = DocumentProcessor()
        self.vector_store = VectorStoreManager()
        self.openai_client = OpenAIClientManager(a4f_api_key, a4f_base_url)
        
        # Initialize session state
        if 'processed_document_hash' not in st.session_state:
            st.session_state.processed_document_hash = None
    
    def _calculate_file_hash(self, file) -> str:
        """Calculate hash of file to avoid reprocessing the same file"""
        file.seek(0)
        file_content = file.read()
        file_hash = hashlib.md5(file_content).hexdigest()
        file.seek(0)  # Reset file pointer
        return file_hash
    
    def process_document(self, uploaded_file) -> bool:
        """Process uploaded document and store in vector database"""
        try:
            file_hash = self._calculate_file_hash(uploaded_file)
            
            # Check if document has already been processed
            if st.session_state.processed_document_hash == file_hash:
                logger.info("Document already processed, skipping")
                return True
            
            # Process document
            with st.spinner("Processing document..."):
                raw_text = self.document_processor.extract_text(uploaded_file)
                chunks = self.document_processor.chunk_text(raw_text)
                self.vector_store.store_documents(chunks, file_hash)
            
            st.session_state.processed_document_hash = file_hash
            st.success(f"Document processed into {len(chunks)} chunks.")
            return True
            
        except Exception as e:
            logger.error(f"Document processing error: {e}")
            st.error(f"Error processing document: {e}")
            return False
    
    def answer_question(self, question: str) -> None:
        """Generate answer to question based on stored documents"""
        if not question:
            st.warning("Please enter a question.")
            return
        
        with st.spinner("Searching for relevant information..."):
            relevant_chunks = self.vector_store.query_similar_chunks(question)
        
        if not relevant_chunks:
            st.info("No relevant information found in the document to answer this question.")
            return
        
        context = "\n\n".join(relevant_chunks)
        
        with st.spinner("Generating answer..."):
            answer = self.openai_client.generate_answer(question, context)
        
        # Display results
        st.markdown("### Answer")
        st.write(answer)
        
        with st.expander("View relevant context"):
            st.write(context)