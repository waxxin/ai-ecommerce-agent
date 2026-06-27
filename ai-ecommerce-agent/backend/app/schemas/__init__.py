"""
API Schema Definitions
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class ProductInfo(BaseModel):
    """Product information input"""
    product_name: str = Field(..., description="商品名称")
    category: Optional[str] = Field("general", description="商品类目")
    features: Optional[List[str]] = Field([], description="商品特点")
    description: Optional[str] = Field("", description="商品描述")


class GenerationRequest(BaseModel):
    """Content generation request"""
    user_input: str = Field(..., description="用户请求")
    context: ProductInfo = Field(..., description="商品信息")


class GenerationResponse(BaseModel):
    """Content generation response"""
    success: bool
    titles: Dict[str, str] = Field(..., description="多平台标题")
    selling_points: List[str] = Field(..., description="卖点列表")
    faq: List[Dict[str, str]] = Field(..., description="FAQ列表")
    raw_notes: str = Field("", description="原始备注")
    execution_stats: Dict[str, int] = Field(..., description="执行统计")


class HistoryRecord(BaseModel):
    """Generation history record"""
    id: int
    product_name: str
    category: str
    features: List[str]
    output_data: Dict[str, Any]
    model_name: str
    status: str
    total_tokens: int
    latency_ms: int
    created_at: str


class HistoryListResponse(BaseModel):
    """History list response"""
    records: List[HistoryRecord]
    total: int


class PromptTemplate(BaseModel):
    """Prompt template model"""
    id: int
    name: str
    description: str
    template_type: str
    variables: Dict[str, str]
    created_at: str


class PromptListResponse(BaseModel):
    """Prompt list response"""
    templates: List[PromptTemplate]


class StatsResponse(BaseModel):
    """Statistics response"""
    total_calls: int
    success_calls: int
    failed_calls: int
    success_rate: float
    total_tokens: int
    today_calls: int


class UserCreate(BaseModel):
    """User creation request"""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    """User response"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool


class LoginRequest(BaseModel):
    """Login request"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response"""
    access_token: str
    token_type: str
    user: UserResponse
