"""
API Routes
All routes are versioned under /api/v1
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.agent_service import AgentService
from app.services.history_service import HistoryService
from app.services.prompt_service import PromptService
from app.services.rag_service import RAGService
from app.schemas import (
    GenerationRequest,
    GenerationResponse,
    HistoryListResponse,
    HistoryRecord,
    PromptListResponse,
    StatsResponse
)

router = APIRouter()


@router.post("/generate", response_model=GenerationResponse)
async def generate_content(
    request: GenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate e-commerce content via Agent
    
    Workflow:
    1. Agent decomposes task into steps
    2. RAG retrieves relevant rules
    3. LLM generates content for each step
    4. Results are merged and returned
    
    Returns:
        Structured content including titles, selling points, and FAQ
    """
    agent_service = AgentService(db)
    history_service = HistoryService(db)
    
    try:
        # Execute Agent
        result = agent_service.generate_content(
            user_input=request.user_input,
            context=request.context.dict()
        )
        
        # Save to history
        history_service.create_record({
            "user_id": 0,
            "product_name": request.context.product_name,
            "category": request.context.category,
            "features": request.context.features,
            "input_text": request.user_input,
            "output_data": {
                "titles": result.get("titles", {}),
                "selling_points": result.get("selling_points", []),
                "faq": result.get("faq", [])
            },
            "model_name": "qwen-max",
            "status": "success",
            "total_tokens": 0,
            "latency_ms": result.get("execution_stats", {}).get("total_latency_ms", 0)
        })
        
        return GenerationResponse(
            success=True,
            titles=result.get("titles", {}),
            selling_points=result.get("selling_points", []),
            faq=result.get("faq", []),
            raw_notes="",
            execution_stats=result.get("execution_stats", {})
        )
    
    except Exception as e:
        # Save failed record
        history_service.create_record({
            "user_id": 0,
            "product_name": request.context.product_name,
            "category": request.context.category,
            "features": request.context.features,
            "input_text": request.user_input,
            "output_data": {},
            "model_name": "qwen-max",
            "status": "failed",
            "error_message": str(e)
        })
        
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=HistoryListResponse)
async def get_history(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get generation history
    
    Args:
        limit: Number of records per page
        offset: Page offset
    
    Returns:
        List of generation records
    """
    history_service = HistoryService(db)
    records = history_service.list_records(limit=limit, offset=offset)
    
    return HistoryListResponse(
        records=records,
        total=len(records)
    )


@router.get("/history/{record_id}", response_model=HistoryRecord)
async def get_history_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """
    Get single generation record
    
    Args:
        record_id: Record ID
    
    Returns:
        Generation record details
    """
    history_service = HistoryService(db)
    record = history_service.get_record(record_id)
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return HistoryRecord(
        id=record.id,
        product_name=record.product_name,
        category=record.category,
        features=record.features,
        output_data=record.output_data,
        model_name=record.model_name,
        status=record.status,
        total_tokens=record.total_tokens,
        latency_ms=record.latency_ms,
        created_at=record.created_at.isoformat() if record.created_at else ""
    )


@router.delete("/history/{record_id}")
async def delete_history_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete generation record
    
    Args:
        record_id: Record ID
    
    Returns:
        Success message
    """
    history_service = HistoryService(db)
    success = history_service.delete_record(record_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return {"message": "Record deleted successfully"}


@router.get("/prompts", response_model=PromptListResponse)
async def get_prompts(
    db: Session = Depends(get_db)
):
    """
    Get all prompt templates
    
    Returns:
        List of prompt templates
    """
    prompt_service = PromptService(db)
    templates = prompt_service.list_templates()
    
    return PromptListResponse(templates=templates)


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    db: Session = Depends(get_db)
):
    """
    Get generation statistics
    
    Returns:
        Statistics including total calls, tokens, etc.
    """
    history_service = HistoryService(db)
    stats = history_service.get_stats()
    
    return StatsResponse(**stats)


@router.post("/knowledge")
async def add_knowledge(
    title: str,
    content: str,
    category: str,
    db: Session = Depends(get_db)
):
    """
    Add knowledge to knowledge base
    
    Args:
        title: Knowledge title
        content: Knowledge content
        category: Knowledge category
    
    Returns:
        Created knowledge item
    """
    rag_service = RAGService(db)
    knowledge = rag_service.add_knowledge(title, content, category)
    
    return {
        "id": knowledge.id,
        "title": knowledge.title,
        "category": knowledge.category,
        "message": "Knowledge added successfully"
    }
