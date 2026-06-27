"""
RAG Service - Knowledge Retrieval
Enterprise Design:
- Standard RAG pipeline: embedding → vector search → context
- Lightweight implementation for portfolio
- Supports rule augmentation for content generation
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models import Knowledge


class RAGService:
    """Retrieval-Augmented Generation service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.embedding_model = None
        self.vector_store = {}
        self._init_embedding()
    
    def _init_embedding(self):
        """Initialize embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self._build_vector_store()
        except Exception:
            pass
    
    def _build_vector_store(self):
        """Build vector store from knowledge base"""
        if not self.embedding_model:
            return
        
        knowledge_items = self.db.query(Knowledge).filter(
            Knowledge.is_active == True
        ).all()
        
        for item in knowledge_items:
            if item.embedding:
                self.vector_store[item.id] = {
                    "embedding": item.embedding,
                    "content": item.content,
                    "title": item.title,
                    "category": item.category
                }
    
    def _compute_embedding(self, text: str) -> List[float]:
        """Compute embedding for text"""
        if not self.embedding_model:
            return [0.0] * 384
        
        return self.embedding_model.encode(text).tolist()
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve relevant knowledge for query
        
        Args:
            query: User query text
            top_k: Number of results to return
        
        Returns:
            List[Dict]: Retrieved knowledge items with relevance score
        """
        if not self.embedding_model or not self.vector_store:
            return self._fallback_retrieve(query, top_k)
        
        query_embedding = self._compute_embedding(query)
        
        results = []
        for item_id, item_data in self.vector_store.items():
            similarity = self._cosine_similarity(query_embedding, item_data["embedding"])
            if similarity > 0.3:
                results.append({
                    "id": item_id,
                    "title": item_data["title"],
                    "content": item_data["content"],
                    "category": item_data["category"],
                    "similarity": round(similarity, 4)
                })
        
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]
    
    def _fallback_retrieve(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Fallback retrieval without embedding"""
        knowledge_items = self.db.query(Knowledge).filter(
            Knowledge.is_active == True
        ).all()
        
        results = []
        for item in knowledge_items:
            if any(kw in query for kw in ["标题", "title", "规则", "rule"]):
                if "标题" in item.category or "规则" in item.category:
                    results.append({
                        "id": item.id,
                        "title": item.title,
                        "content": item.content,
                        "category": item.category,
                        "similarity": 0.5
                    })
        
        return results[:top_k]
    
    def get_rules_for_category(self, category: str) -> str:
        """Get rules for specific category"""
        knowledge_items = self.db.query(Knowledge).filter(
            Knowledge.category == category,
            Knowledge.is_active == True
        ).all()
        
        if not knowledge_items:
            return ""
        
        return "\n\n".join([f"【{item.title}】\n{item.content}" for item in knowledge_items])
    
    def add_knowledge(self, title: str, content: str, category: str) -> Knowledge:
        """Add new knowledge to database"""
        embedding = self._compute_embedding(content) if self.embedding_model else None
        
        knowledge = Knowledge(
            title=title,
            content=content,
            category=category,
            embedding=embedding
        )
        
        self.db.add(knowledge)
        self.db.commit()
        self.db.refresh(knowledge)
        
        if self.vector_store:
            self.vector_store[knowledge.id] = {
                "embedding": embedding,
                "content": content,
                "title": title,
                "category": category
            }
        
        return knowledge
