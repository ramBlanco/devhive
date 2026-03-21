import sqlite3
import json
import hashlib
import math
import re
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class TFIDFVectorizer:
    """
    Pure Python TF-IDF implementation for text search.
    Avoids heavy dependencies like scikit-learn.
    """
    
    def __init__(self):
        self.vocabulary = {}  # word -> index
        self.idf_scores = {}  # word -> IDF score
        self.documents = []   # List of document IDs
        
    def tokenize(self, text: str) -> List[str]:
        """Simple tokenizer: lowercase + alphanumeric split."""
        text = text.lower()
        # Remove special characters, keep alphanumeric and spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        tokens = text.split()
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'can'}
        return [t for t in tokens if len(t) > 2 and t not in stop_words]
    
    def compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        """Compute Term Frequency for a document."""
        tf = Counter(tokens)
        max_freq = max(tf.values()) if tf else 1
        # Normalized TF
        return {word: count / max_freq for word, count in tf.items()}
    
    def fit(self, documents: List[Tuple[str, str]]):
        """
        Build vocabulary and IDF scores.
        
        Args:
            documents: List of (doc_id, text) tuples
        """
        self.documents = [doc_id for doc_id, _ in documents]
        
        # Count document frequencies
        df = defaultdict(int)  # word -> number of documents containing it
        
        for doc_id, text in documents:
            tokens = set(self.tokenize(text))  # unique words in document
            for token in tokens:
                df[token] += 1
        
        # Build vocabulary and compute IDF
        self.vocabulary = {word: idx for idx, word in enumerate(sorted(df.keys()))}
        num_docs = len(documents)
        
        for word, doc_freq in df.items():
            # IDF = log(N / df) where N is total docs
            self.idf_scores[word] = math.log((num_docs + 1) / (doc_freq + 1)) + 1
    
    def transform_query(self, query: str) -> Dict[str, float]:
        """Convert query to TF-IDF weighted vector."""
        tokens = self.tokenize(query)
        tf = self.compute_tf(tokens)
        
        # Apply IDF weights
        tfidf = {}
        for word, tf_score in tf.items():
            if word in self.idf_scores:
                tfidf[word] = tf_score * self.idf_scores[word]
        
        return tfidf
    
    def compute_document_vector(self, text: str) -> Dict[str, float]:
        """Compute TF-IDF vector for a document."""
        tokens = self.tokenize(text)
        tf = self.compute_tf(tokens)
        
        tfidf = {}
        for word, tf_score in tf.items():
            if word in self.idf_scores:
                tfidf[word] = tf_score * self.idf_scores[word]
        
        return tfidf
    
    def cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Compute cosine similarity between two sparse vectors."""
        if not vec1 or not vec2:
            return 0.0
        
        # Dot product
        dot_product = sum(vec1.get(word, 0) * vec2.get(word, 0) for word in set(vec1.keys()) | set(vec2.keys()))
        
        # Magnitudes
        mag1 = math.sqrt(sum(v**2 for v in vec1.values()))
        mag2 = math.sqrt(sum(v**2 for v in vec2.values()))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)


class MemoryStore:
    """
    SQLite-backed memory store with TF-IDF search capabilities.
    Stores prompts, contexts, and artifacts with content hashing.
    """
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.db_path = Path(f"./.devhive/memory.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.vectorizer = TFIDFVectorizer()
        self._init_db()
        
    def _init_db(self):
        """Initialize SQLite database schema."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Memory chunks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT UNIQUE NOT NULL,
                chunk_type TEXT NOT NULL,
                agent_name TEXT,
                step_name TEXT,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index on content_hash for fast lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_content_hash 
            ON memory_chunks(content_hash)
        """)
        
        # Create index on chunk_type for filtering
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chunk_type 
            ON memory_chunks(chunk_type)
        """)
        
        conn.commit()
        conn.close()
        
        logger.info(f"MemoryStore initialized for project: {self.project_name}")
    
    def _hash_content(self, content: str) -> str:
        """Generate SHA-256 hash of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def store_memory(
        self, 
        chunk_type: str, 
        content: str, 
        agent_name: Optional[str] = None,
        step_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store a memory chunk in the database.
        
        Args:
            chunk_type: Type of memory (prompt, context, artifact, response)
            content: Text content to store
            agent_name: Name of the agent (optional)
            step_name: Step/artifact name (optional)
            metadata: Additional metadata (optional)
        
        Returns:
            content_hash: SHA-256 hash of the content
        """
        content_hash = self._hash_content(content)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO memory_chunks 
                (content_hash, chunk_type, agent_name, step_name, content, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                content_hash,
                chunk_type,
                agent_name,
                step_name,
                content,
                json.dumps(metadata) if metadata else None
            ))
            conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Stored {chunk_type} memory: {content_hash[:8]}... (agent={agent_name})")
            else:
                logger.debug(f"Memory chunk already exists: {content_hash[:8]}...")
                
        except sqlite3.Error as e:
            logger.error(f"Failed to store memory: {e}")
        finally:
            conn.close()
        
        return content_hash
    
    def search_memory(
        self, 
        query: str, 
        top_k: int = 5, 
        chunk_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search memory using TF-IDF similarity.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            chunk_types: Filter by chunk types (e.g., ['artifact', 'context'])
        
        Returns:
            List of memory chunks sorted by relevance
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Fetch all memories (with optional type filter)
        if chunk_types:
            placeholders = ','.join('?' * len(chunk_types))
            cursor.execute(f"""
                SELECT id, content_hash, chunk_type, agent_name, step_name, content, metadata
                FROM memory_chunks
                WHERE chunk_type IN ({placeholders})
                ORDER BY created_at DESC
            """, chunk_types)
        else:
            cursor.execute("""
                SELECT id, content_hash, chunk_type, agent_name, step_name, content, metadata
                FROM memory_chunks
                ORDER BY created_at DESC
            """)
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return []
        
        # Build TF-IDF index on-the-fly
        documents = [(str(row[0]), row[5]) for row in rows]  # (id, content)
        self.vectorizer.fit(documents)
        
        # Transform query
        query_vec = self.vectorizer.transform_query(query)
        
        # Compute similarities
        results = []
        for row in rows:
            doc_id, content_hash, chunk_type, agent_name, step_name, content, metadata = row
            doc_vec = self.vectorizer.compute_document_vector(content)
            similarity = self.vectorizer.cosine_similarity(query_vec, doc_vec)
            
            results.append({
                "id": doc_id,
                "content_hash": content_hash,
                "chunk_type": chunk_type,
                "agent_name": agent_name,
                "step_name": step_name,
                "content": content,
                "metadata": json.loads(metadata) if metadata else None,
                "relevance_score": similarity
            })
        
        # Sort by relevance and return top_k
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:top_k]
    
    def get_recent_memories(
        self, 
        limit: int = 10, 
        chunk_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get most recent memory chunks.
        
        Args:
            limit: Number of memories to return
            chunk_types: Filter by chunk types
        
        Returns:
            List of recent memory chunks
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        if chunk_types:
            placeholders = ','.join('?' * len(chunk_types))
            cursor.execute(f"""
                SELECT id, content_hash, chunk_type, agent_name, step_name, content, metadata, created_at
                FROM memory_chunks
                WHERE chunk_type IN ({placeholders})
                ORDER BY created_at DESC
                LIMIT ?
            """, (*chunk_types, limit))
        else:
            cursor.execute("""
                SELECT id, content_hash, chunk_type, agent_name, step_name, content, metadata, created_at
                FROM memory_chunks
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{
            "id": row[0],
            "content_hash": row[1],
            "chunk_type": row[2],
            "agent_name": row[3],
            "step_name": row[4],
            "content": row[5],
            "metadata": json.loads(row[6]) if row[6] else None,
            "created_at": row[7]
        } for row in rows]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory store statistics."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Total chunks
        cursor.execute("SELECT COUNT(*) FROM memory_chunks")
        total_chunks = cursor.fetchone()[0]
        
        # Chunks by type
        cursor.execute("""
            SELECT chunk_type, COUNT(*) 
            FROM memory_chunks 
            GROUP BY chunk_type
        """)
        chunks_by_type = dict(cursor.fetchall())
        
        # Database size
        db_size_bytes = self.db_path.stat().st_size if self.db_path.exists() else 0
        
        conn.close()
        
        return {
            "project_name": self.project_name,
            "total_chunks": total_chunks,
            "chunks_by_type": chunks_by_type,
            "db_size_mb": round(db_size_bytes / (1024 * 1024), 2),
            "db_path": str(self.db_path)
        }
