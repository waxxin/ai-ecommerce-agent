"""
History Service - Generation History Management
Enterprise Design:
- Structured storage of generation records
- Full input/output tracking
- Token usage statistics
- Query and export support
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.models import GenerationHistory


class HistoryService:
    """Generation history management service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_record(self, data: Dict[str, Any]) -> GenerationHistory:
        """
        Create new generation record
        
        Args:
            data: Record data including:
                - user_id
                - product_name
                - category
                - features
                - input_text
                - output_data
                - prompt_id
                - model_name
                - status
                - token usage
                - latency
        
        Returns:
            GenerationHistory: Created record
        """
        record = GenerationHistory(
            user_id=data.get("user_id", 0),
            product_name=data.get("product_name", ""),
            category=data.get("category", ""),
            features=data.get("features", []),
            input_text=data.get("input_text", ""),
            output_data=data.get("output_data", {}),
            prompt_id=data.get("prompt_id", 0),
            model_name=data.get("model_name", ""),
            status=data.get("status", "success"),
            input_tokens=data.get("input_tokens", 0),
            output_tokens=data.get("output_tokens", 0),
            total_tokens=data.get("total_tokens", 0),
            latency_ms=data.get("latency_ms", 0),
            error_message=data.get("error_message", "")
        )
        
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        
        return record
    
    def get_record(self, record_id: int) -> GenerationHistory:
        """Get record by ID"""
        return self.db.query(GenerationHistory).filter(
            GenerationHistory.id == record_id
        ).first()
    
    def list_records(self, user_id: int = None, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List generation records
        
        Args:
            user_id: Filter by user ID
            limit: Number of records per page
            offset: Page offset
        
        Returns:
            List[Dict]: List of records
        """
        query = self.db.query(GenerationHistory)
        
        if user_id:
            query = query.filter(GenerationHistory.user_id == user_id)
        
        records = query.order_by(GenerationHistory.created_at.desc()).offset(offset).limit(limit).all()
        
        return [{
            "id": r.id,
            "user_id": r.user_id,
            "product_name": r.product_name,
            "category": r.category,
            "features": r.features,
            "output_data": r.output_data,
            "model_name": r.model_name,
            "status": r.status,
            "total_tokens": r.total_tokens,
            "latency_ms": r.latency_ms,
            "created_at": r.created_at.isoformat() if r.created_at else None
        } for r in records]
    
    def get_stats(self, user_id: int = None) -> Dict[str, Any]:
        """
        Get generation statistics
        
        Args:
            user_id: Filter by user ID
        
        Returns:
            Dict: Statistics including total calls, tokens, etc.
        """
        query = self.db.query(GenerationHistory)
        
        if user_id:
            query = query.filter(GenerationHistory.user_id == user_id)
        
        total_calls = query.count()
        success_calls = query.filter(GenerationHistory.status == "success").count()
        total_tokens = query.with_entities(
            sum(GenerationHistory.total_tokens)
        ).scalar() or 0
        
        today = datetime.now().date()
        today_calls = query.filter(
            GenerationHistory.created_at >= datetime(today.year, today.month, today.day)
        ).count()
        
        return {
            "total_calls": total_calls,
            "success_calls": success_calls,
            "failed_calls": total_calls - success_calls,
            "success_rate": success_calls / total_calls if total_calls > 0 else 0,
            "total_tokens": total_tokens,
            "today_calls": today_calls
        }
    
    def delete_record(self, record_id: int) -> bool:
        """Delete record by ID"""
        record = self.get_record(record_id)
        if not record:
            return False
        
        self.db.delete(record)
        self.db.commit()
        
        return True


def sum(*args):
    from sqlalchemy import func
    return func.sum(*args)
