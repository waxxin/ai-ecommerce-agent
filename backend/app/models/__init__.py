"""
Database Models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PromptTemplate(Base):
    """Prompt template model"""
    __tablename__ = "prompt_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(String(500))
    template_type = Column(String(50))
    content = Column(Text)
    variables = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class GenerationHistory(Base):
    """Generation history model"""
    __tablename__ = "generation_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    product_name = Column(String(200))
    category = Column(String(100))
    features = Column(JSON)
    input_text = Column(Text)
    output_data = Column(JSON)
    prompt_id = Column(Integer, index=True)
    model_name = Column(String(100))
    status = Column(String(20))
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    total_tokens = Column(Integer)
    latency_ms = Column(Integer)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AILog(Base):
    """AI call log model"""
    __tablename__ = "ai_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    model_name = Column(String(100))
    prompt = Column(Text)
    response = Column(Text)
    status = Column(String(20))
    error_message = Column(Text)
    latency_ms = Column(Integer)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    total_tokens = Column(Integer)
    extra_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Knowledge(Base):
    """Knowledge base model"""
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    content = Column(Text)
    category = Column(String(100))
    source = Column(String(200))
    embedding = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ModelConfig(Base):
    """Model configuration model"""
    __tablename__ = "model_config"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), unique=True, index=True)
    provider = Column(String(50))
    model_id = Column(String(100))
    api_key = Column(String(255))
    api_base_url = Column(String(255))
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=2048)
    top_p = Column(Float, default=0.9)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
