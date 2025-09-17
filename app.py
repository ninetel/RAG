import streamlit as st
import os
from dotenv import load_dotenv
from src.rag_assistant import RAGResearchAssistant

# Load environment variables
load_dotenv()

def main():
    """Main application function"""
    # Get configuration from environment variables
    A4F_API_KEY = os.getenv("A4F_API_KEY")
    A4F_BASE_URL = os.getenv("A4F_BASE_URL")
    
    if not A4F_API_KEY or not A4F_BASE_URL:
        st.error("Missing API configuration. Please check your environment variables.")
        return
    
    # Initialize the application
    st.set_page_config(page_title="RAG Research Assistant", layout="wide")
    st.title("📄 RAG Research Assistant")
    st.write("Upload a PDF or TXT file and ask questions based on its content.")
    
    # Initialize components
    rag_assistant = RAGResearchAssistant(A4F_API_KEY, A4F_BASE_URL)
    
    # File uploader
    uploaded_file = st.file_uploader("Upload your document", type=["pdf", "txt"])
    
    if uploaded_file:
        success = rag_assistant.process_document(uploaded_file)
        
        if success:
            # Question input
            question = st.text_input("Ask a question about the document:")
            ask_button = st.button("Get Answer")
            
            if ask_button and question:
                rag_assistant.answer_question(question)

if __name__ == "__main__":
    main()