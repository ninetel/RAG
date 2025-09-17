import logging
from typing import List
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient

logger = logging.getLogger(__name__)

class VectorStoreManager:
    """Manages vector store operations including embeddings and storage"""
    
    def __init__(self, collection_name: str = "doc_chunks", persist_directory: str = "./chroma"):
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.chroma_client = PersistentClient(path=persist_directory)
        self.collection = self.chroma_client.get_or_create_collection(name=collection_name)
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        try:
            return self.embedding_model.encode(texts, show_progress_bar=False).tolist()
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            raise
    
    def store_documents(self, chunks: List[str], document_hash: str):
        """Store document chunks with their embeddings"""
        if not chunks:
            return
        
        embeddings = self.generate_embeddings(chunks)
        ids = [f"{document_hash}_{i}" for i in range(len(chunks))]
        
        try:
            self.collection.add(
                documents=chunks,
                embeddings=embeddings,
                ids=ids
            )
            logger.info(f"Stored {len(chunks)} chunks for document {document_hash}")
        except Exception as e:
            logger.error(f"Error storing documents: {e}")
            raise
    
    def query_similar_chunks(self, query: str, n_results: int = 3) -> List[str]:
        """Query similar chunks from the vector store"""
        try:
            query_embedding = self.generate_embeddings([query])[0]
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            return results["documents"][0] if results["documents"] else []
        except Exception as e:
            logger.error(f"Query error: {e}")
            return []