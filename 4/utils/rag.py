from openai import OpenAI
import config

class RAGSystem:
    
    def __init__(self, vector_store_manager):
        """Initialize the RAG system."""
        self.vector_store_manager = vector_store_manager
        self.chat_history = []
        
        # Configure OpenAI client (OpenRouter-compatible)
        # Include recommended headers if provided
        self.client = OpenAI(
            base_url=config.OPENROUTER_BASE_URL,
            api_key=config.OPENROUTER_API_KEY,
            default_headers={
                **({"HTTP-Referer": config.OPENROUTER_SITE_URL} if getattr(config, "OPENROUTER_SITE_URL", "") else {}),
                **({"X-Title": config.OPENROUTER_APP_NAME} if getattr(config, "OPENROUTER_APP_NAME", "") else {}),
            },
        )
        
    def _format_prompt(self, question, context_docs):
        """Format the prompt with context from retrieved documents."""
        # Extract and format context from documents
        context_text = "\n\n".join([doc.page_content for doc in context_docs])
        
        prompt = f"""You are a helpful AI assistant. Use the following pieces of context to answer the question at the end. 
If you don't know the answer based on the context provided, just say that you don't know, don't try to make up an answer.

Context:
{context_text}

Question: {question}

Helpful Answer:"""
        return prompt
    
    def ask(
        self,
        question,
        *,
        temperature=None,
        max_tokens=None,
        top_k_results=None,
    ):
        # Get relevant documents
        retriever = self.vector_store_manager.get_retriever(k=top_k_results if top_k_results is not None else None)
        if not retriever:
            return {
                "answer": "Please upload documents first to enable document question answering.",
                "source_documents": []
            }
        
        try:
            # Retrieve relevant documents
            docs = retriever.invoke(question)
            
            # Format prompt with context
            prompt = self._format_prompt(question, docs)
            
            # Call the LLM
            response = self.client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=(temperature if temperature is not None else config.TEMPERATURE),
                max_tokens=(max_tokens if max_tokens is not None else config.MAX_TOKENS),
            )
            
            # Extract answer from response
            answer = response.choices[0].message.content
            
            # Update chat history
            self.chat_history.append({"role": "user", "content": question})
            self.chat_history.append({"role": "assistant", "content": answer})
            
            return {
                "answer": answer,
                "source_documents": docs
            }
        except Exception as e:
            return {
                "answer": f"An error occurred: {str(e)}",
                "source_documents": []
            }
    
    def clear_memory(self):
        self.chat_history = []