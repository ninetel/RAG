import logging
import re
from typing import List
import pdfplumber

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles document processing including text extraction and chunking"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text(self, file) -> str:
        """Extract text from PDF or TXT file"""
        try:
            if file.name.endswith(".pdf"):
                return self._extract_from_pdf(file)
            else:
                return file.read().decode("utf-8")
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            raise ValueError(f"Failed to extract text from file: {e}")
    
    def _extract_from_pdf(self, file) -> str:
        """Extract text from PDF file"""
        text = []
        try:
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
            return "\n".join(text)
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            raise
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks with sentence awareness"""
        if not text:
            return []
        
        # First split by paragraphs
        paragraphs = text.split('\n\n')
        chunks = []
        
        for paragraph in paragraphs:
            if len(paragraph) <= self.chunk_size:
                chunks.append(paragraph)
            else:
                # Split long paragraphs into sentences
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                current_chunk = ""
                
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) <= self.chunk_size:
                        current_chunk += sentence + " "
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence + " "
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
        
        return chunks