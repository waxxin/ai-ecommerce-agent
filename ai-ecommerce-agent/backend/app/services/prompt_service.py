"""
Prompt Service - Prompt Template Management
Enterprise Design:
- Template version control
- Variable substitution
- Category management
- Structured prompt generation
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models import PromptTemplate


class PromptService:
    """Prompt template management service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get prompt template by name"""
        return self.db.query(PromptTemplate).filter(
            PromptTemplate.name == name,
            PromptTemplate.is_active == True
        ).first()
    
    def get_template_by_type(self, template_type: str) -> Optional[PromptTemplate]:
        """Get prompt template by type"""
        return self.db.query(PromptTemplate).filter(
            PromptTemplate.template_type == template_type,
            PromptTemplate.is_active == True
        ).first()
    
    def render_prompt(self, template_name: str, variables: Dict[str, Any]) -> str:
        """
        Render prompt template with variables
        
        Args:
            template_name: Template name
            variables: Dictionary of variables to substitute
        
        Returns:
            str: Rendered prompt
        """
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        prompt = template.content
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            if isinstance(value, list):
                value_str = "\n".join(f"- {item}" for item in value)
                prompt = prompt.replace(placeholder, value_str)
            else:
                prompt = prompt.replace(placeholder, str(value))
        
        return prompt
    
    def create_template(self, data: Dict[str, Any]) -> PromptTemplate:
        """Create new prompt template"""
        template = PromptTemplate(
            name=data["name"],
            description=data.get("description", ""),
            template_type=data.get("template_type", "general"),
            content=data["content"],
            variables=data.get("variables", {})
        )
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template
    
    def update_template(self, name: str, data: Dict[str, Any]) -> Optional[PromptTemplate]:
        """Update existing template"""
        template = self.get_template(name)
        if not template:
            return None
        
        if "description" in data:
            template.description = data["description"]
        if "content" in data:
            template.content = data["content"]
        if "variables" in data:
            template.variables = data["variables"]
        if "is_active" in data:
            template.is_active = data["is_active"]
        
        self.db.commit()
        self.db.refresh(template)
        return template
    
    def list_templates(self) -> list:
        """List all active templates"""
        templates = self.db.query(PromptTemplate).filter(
            PromptTemplate.is_active == True
        ).all()
        
        return [{
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "template_type": t.template_type,
            "variables": t.variables,
            "created_at": t.created_at.isoformat() if t.created_at else None
        } for t in templates]
