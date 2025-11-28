"""
Vector Store Implementation
Provides semantic search capabilities using Google GenAI embeddings and SQLite.
"""

import logging
import json
import sqlite3
import numpy as np
from typing import List, Dict, Optional, Tuple
from google import genai

logger = logging.getLogger(__name__)

class VectorStore:
    """
    Simple Vector Store using SQLite for storage and numpy for cosine similarity.
    In a production ADK environment, this would be replaced by Vertex AI Vector Search.
    """
    
    def __init__(self, db_path: str = "vibe_memory.db"):
        self.db_path = db_path
        self.model_id = "text-embedding-004"
        
        try:
            self.client = genai.Client(
                http_options={'api_version': 'v1alpha'}
            )
            self._init_db()
        except Exception as e:
            logger.error(f"Failed to initialize VectorStore: {e}")
            self.client = None

    def _init_db(self):
        """Initialize SQLite table for vectors"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vectors (
                    id TEXT PRIMARY KEY,
                    content TEXT,
                    embedding TEXT,  -- JSON encoded list of floats
                    metadata TEXT,   -- JSON encoded dict
                    agent_id TEXT,
                    user_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index for faster filtering
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_user ON vectors (agent_id, user_id)")

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text using Gemini"""
        if not self.client:
            return []
            
        try:
            result = self.client.models.embed_content(
                model=self.model_id,
                contents=text
            )
            return result.embeddings[0].values
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []

    async def add_document(
        self, 
        doc_id: str, 
        content: str, 
        metadata: Dict, 
        user_id: str, 
        agent_id: str
    ) -> bool:
        """Add a document and its embedding to the store"""
        embedding = await self.embed_text(content)
        if not embedding:
            return False
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO vectors (id, content, embedding, metadata, agent_id, user_id) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        doc_id,
                        content,
                        json.dumps(embedding),
                        json.dumps(metadata),
                        agent_id,
                        user_id
                    )
                )
            return True
        except Exception as e:
            logger.error(f"Failed to add document to vector store: {e}")
            return False

    async def search(
        self, 
        query: str, 
        user_id: str, 
        agent_id: str, 
        limit: int = 5
    ) -> List[Dict]:
        """
        Semantic search for relevant documents
        """
        query_embedding = await self.embed_text(query)
        if not query_embedding:
            return []
            
        query_vec = np.array(query_embedding)
        
        results = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Fetch all vectors for this user/agent
                # Note: In production, use a real Vector DB (pgvector, Vertex AI) for efficiency
                cursor = conn.execute(
                    "SELECT id, content, embedding, metadata, created_at FROM vectors WHERE user_id = ? AND agent_id = ?",
                    (user_id, agent_id)
                )
                
                rows = cursor.fetchall()
                
                for row in rows:
                    doc_id, content, emb_json, meta_json, created_at = row
                    doc_vec = np.array(json.loads(emb_json))
                    
                    # Cosine Similarity
                    similarity = np.dot(query_vec, doc_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(doc_vec))
                    
                    results.append({
                        "id": doc_id,
                        "content": content,
                        "metadata": json.loads(meta_json),
                        "score": float(similarity),
                        "created_at": created_at
                    })
                
                # Sort by score descending
                results.sort(key=lambda x: x["score"], reverse=True)
                
                return results[:limit]
                
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
