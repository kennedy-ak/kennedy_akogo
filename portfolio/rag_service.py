import requests
import json
import logging
from typing import List, Dict, Tuple, Optional
import re
import os
from django.conf import settings

# Optional imports for RAG functionality
try:
    import numpy as np
    import faiss
    from groq import Groq
    from openai import OpenAI
    RAG_DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    RAG_DEPENDENCIES_AVAILABLE = False
    logging.warning(f"RAG dependencies not available: {e}")

logger = logging.getLogger(__name__)


class ProjectRAGService:
    """Service for handling RAG operations for projects"""
    
    def __init__(self):
        self.openai_client = None
        self.groq_client = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize the OpenAI client and Groq client"""
        if not RAG_DEPENDENCIES_AVAILABLE:
            logger.warning("RAG dependencies not available. Please install: pip install openai faiss-cpu groq numpy tiktoken")
            return

        try:
            # Initialize OpenAI client for embeddings
            openai_api_key = getattr(settings, 'OPENAI_API_KEY', None)
            if openai_api_key:
                self.openai_client = OpenAI(api_key=openai_api_key)
            else:
                logger.warning("OPENAI_API_KEY not found in settings")

            # Initialize Groq client
            groq_api_key = getattr(settings, 'GROQ_API_KEY', None)
            if groq_api_key:
                self.groq_client = Groq(api_key=groq_api_key)
            else:
                logger.warning("GROQ_API_KEY not found in settings")

        except Exception as e:
            logger.error(f"Error initializing RAG models: {e}")
    
    def fetch_repo_content_with_gitingest(self, github_url: str) -> Optional[str]:
        """
        Fetch repository content using Gitingest API
        
        Args:
            github_url: GitHub repository URL
            
        Returns:
            Repository content as text or None if failed
        """
        try:
            # Extract repo path from GitHub URL
            # e.g., https://github.com/owner/repo -> owner/repo
            repo_path = self._extract_repo_path(github_url)
            if not repo_path:
                logger.error(f"Could not extract repo path from URL: {github_url}")
                return None
            
            # Gitingest API endpoint
            gitingest_url = f"https://gitingest.com/api/ingest"

            # Make request to Gitingest with updated format
            payload = {
                "input_text": github_url,
                "max_file_size": 102400,  # 100KB max file size (API limit)
                "include_patterns": [],  # Include all files by default
                "exclude_patterns": [
                    "*.pyc", "*.pyo", "*.pyd", "__pycache__/*",
                    "*.so", "*.dylib", "*.dll",
                    "node_modules/*", ".git/*", ".vscode/*", ".idea/*",
                    "*.log", "*.tmp", "*.temp",
                    "*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.svg",
                    "*.pdf", "*.doc", "*.docx", "*.xls", "*.xlsx",
                    "*.zip", "*.tar", "*.gz", "*.rar",
                    "dist/*", "build/*", "target/*",
                    ".env", ".env.*"
                ]
            }
            
            response = requests.post(gitingest_url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('content', '')
            else:
                logger.error(f"Gitingest API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching repo content: {e}")
            return None
    
    def _extract_repo_path(self, github_url: str) -> Optional[str]:
        """Extract owner/repo from GitHub URL"""
        try:
            # Remove trailing slash and split
            parts = github_url.rstrip('/').split('/')
            if len(parts) >= 2 and 'github.com' in github_url:
                return f"{parts[-2]}/{parts[-1]}"
            return None
        except Exception:
            return None
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Input text to chunk
            chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # If this isn't the last chunk, try to break at a sentence or word boundary
            if end < len(text):
                # Look for sentence boundary
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + chunk_size // 2:
                    end = sentence_end + 1
                else:
                    # Look for word boundary
                    word_end = text.rfind(' ', start, end)
                    if word_end > start + chunk_size // 2:
                        end = word_end
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = max(start + 1, end - overlap)
            
            # Prevent infinite loop
            if start >= len(text):
                break
        
        return chunks
    
    def create_embeddings(self, chunks: List[str]) -> Tuple[Optional[object], Optional[object]]:
        """
        Create embeddings for text chunks and build FAISS index using OpenAI
        
        Args:
            chunks: List of text chunks
            
        Returns:
            Tuple of (embeddings array, FAISS index)
        """
        if not chunks or not self.openai_client or not RAG_DEPENDENCIES_AVAILABLE:
            return None, None
        
        try:
            # Generate embeddings using OpenAI
            embeddings_list = []
            for chunk in chunks:
                response = self.openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=chunk
                )
                embeddings_list.append(response.data[0].embedding)
            
            # Convert to numpy array
            embeddings = np.array(embeddings_list, dtype=np.float32)
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            index.add(embeddings)
            
            return embeddings, index
            
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            return None, None
    
    def search_similar_chunks(self, query: str, index: object,
                            chunks: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for similar chunks using FAISS
        
        Args:
            query: Search query
            index: FAISS index
            chunks: Original text chunks
            top_k: Number of top results to return
            
        Returns:
            List of (chunk, score) tuples
        """
        if not query or not index or not chunks or not self.openai_client:
            return []
        
        try:
            # Generate query embedding using OpenAI
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            query_embedding = np.array([response.data[0].embedding], dtype=np.float32)
            faiss.normalize_L2(query_embedding)
            
            # Search
            scores, indices = index.search(query_embedding, min(top_k, len(chunks)))
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(chunks):
                    results.append((chunks[idx], float(score)))
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar chunks: {e}")
            return []
    
    def generate_response_with_groq(self, query: str, context_chunks: List[str],
                                  project_title: str, chat_history: List[Dict] = None) -> str:
        """
        Generate response using Groq with context

        Args:
            query: User query
            context_chunks: Relevant context chunks
            project_title: Project title for context
            chat_history: Previous chat messages for context

        Returns:
            Generated response
        """
        if not self.groq_client:
            return "Sorry, the AI service is not available at the moment."
        
        try:
            # Prepare context
            context = "\n\n".join(context_chunks[:3])  # Use top 3 chunks

            # Prepare chat history context
            history_context = ""
            if chat_history and len(chat_history) > 0:
                recent_history = chat_history[-4:]  # Last 4 messages for context
                history_items = []
                for msg in recent_history:
                    role = "User" if msg.get('role') == 'user' else "Assistant"
                    history_items.append(f"{role}: {msg.get('content', '')}")
                history_context = f"\n\nRecent conversation:\n" + "\n".join(history_items)

            # Create prompt
            prompt = f"""You are an AI assistant helping users understand the "{project_title}" project.
Use the following code/documentation context to answer the user's question accurately and helpfully.

Context from the project repository:
{context}{history_context}

User Question: {query}

Instructions:
- Keep responses CONCISE and to the point (2-3 sentences max)
- Focus on the most important information
- Use bullet points for lists when appropriate
- If the context doesn't contain enough information, say so briefly and suggest what might help"""

            # Generate response using Groq
            response = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant that explains code and projects clearly and concisely. Keep responses brief and focused."},
                    {"role": "user", "content": prompt}
                ],
                model="llama3-8b-8192",  # or another available model
                max_tokens=200,  # Reduced for more concise responses
                temperature=0.5  # Lower temperature for more focused responses
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating response with Groq: {e}")
            return "Sorry, I encountered an error while generating a response. Please try again."
