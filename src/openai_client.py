import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

class OpenAIClientManager:
    """Manages OpenAI API interactions"""
    
    def __init__(self, api_key: str, base_url: str):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
    
    def generate_answer(self, question: str, context: str, model: str = "provider-3/gpt-4o-mini") -> str:
        """Generate answer using OpenAI API with provided context"""
        prompt = self._build_prompt(question, context)
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1  # Lower temperature for more factual answers
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return "Sorry, I encountered an error while generating the answer."
    
    def _build_prompt(self, question: str, context: str) -> str:
        """Build the prompt for the OpenAI API"""
        return f"""You are a helpful research assistant. Use the following context to answer the question. 
If the context doesn't contain relevant information, say so. Don't make up information.

Context:
{context}

Question:
{question}

Please provide a concise and accurate answer based on the context:"""