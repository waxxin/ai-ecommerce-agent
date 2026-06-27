"""
Initialize application data
- Create default prompt templates
- Initialize knowledge base
"""
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, init_db
from app.models import PromptTemplate, Knowledge, ModelConfig
from app.core.config import settings


def init_prompt_templates(db: Session):
    """Initialize default prompt templates"""
    templates = [
        {
            "name": "title_generation",
            "description": "生成多平台商品标题",
            "template_type": "title",
            "content": """你是一个专业的电商运营助手。

商品信息：
- 商品名称：{{product_name}}
- 商品特点：{{features}}

{{rules_context}}

任务：请为以下平台生成商品标题

要求：
- 拼多多标题：30字以内，包含核心关键词，突出性价比
- 淘宝标题：60字以内，包含营销词，吸引点击
- 小红书标题：吸引眼球，带话题标签

请严格按照以下JSON格式输出：
{
  "pdd": "拼多多标题",
  "tb": "淘宝标题",
  "xhs": "小红书标题"
}""",
            "variables": {"product_name": "商品名称", "features": "商品特点", "rules_context": "规则上下文"}
        },
        {
            "name": "selling_points_extraction",
            "description": "提取商品核心卖点",
            "template_type": "feature",
            "content": """你是一个专业的电商运营助手。

商品信息：
- 商品名称：{{product_name}}
- 商品特点：{{features}}
- 商品描述：{{description}}

任务：提取商品的核心卖点

要求：
- 提取5-8个核心卖点
- 每个卖点不超过20字
- 突出产品优势和差异化

请严格按照以下JSON格式输出：
{
  "selling_points": ["卖点1", "卖点2", "卖点3"]
}""",
            "variables": {"product_name": "商品名称", "features": "商品特点", "description": "商品描述"}
        },
        {
            "name": "faq_generation",
            "description": "生成客服常见问题",
            "template_type": "faq",
            "content": """你是一个专业的电商运营助手。

商品信息：
- 商品名称：{{product_name}}
- 商品特点：{{features}}

任务：生成客服常见问题及答案

要求：
- 生成3-5个常见问题
- 问题和答案要实用
- 符合电商客服场景

请严格按照以下JSON格式输出：
{
  "faq": [
    {"question": "问题1", "answer": "答案1"},
    {"question": "问题2", "answer": "答案2"}
  ]
}""",
            "variables": {"product_name": "商品名称", "features": "商品特点"}
        }
    ]
    
    for template_data in templates:
        existing = db.query(PromptTemplate).filter(
            PromptTemplate.name == template_data["name"]
        ).first()
        
        if not existing:
            template = PromptTemplate(**template_data)
            db.add(template)
    
    db.commit()


def init_knowledge_base(db: Session):
    """Initialize knowledge base with e-commerce rules"""
    knowledge_items = [
        {
            "title": "拼多多标题规范",
            "content": """拼多多标题规范：
1. 标题长度控制在20-30字
2. 必须包含核心关键词
3. 可以使用营销词如：包邮、特价、限时
4. 禁止使用夸大词汇
5. 不要重复关键词""",
            "category": "title_rules"
        },
        {
            "title": "淘宝标题规范",
            "content": """淘宝标题规范：
1. 标题长度控制在50-60字
2. 包含核心关键词和长尾词
3. 使用营销词提高点击率
4. 按照"品牌+核心词+属性词+营销词"结构
5. 避免堆砌关键词""",
            "category": "title_rules"
        },
        {
            "title": "小红书标题规范",
            "content": """小红书标题规范：
1. 标题要吸引人，使用emoji
2. 包含话题标签，如#好物推荐
3. 使用数字增加可信度
4. 营造紧迫感或好奇心
5. 字数控制在20-30字""",
            "category": "title_rules"
        },
        {
            "title": "3C数码类目规则",
            "content": """3C数码类目规则：
1. 必须标注品牌和型号
2. 说明产品规格参数
3. 突出产品性能特点
4. 可以强调售后服务
5. 注明保修期限""",
            "category": "electronics_rules"
        },
        {
            "title": "服装类目规则",
            "content": """服装类目规则：
1. 标注材质和尺码
2. 说明适用季节
3. 突出设计亮点
4. 可以使用模特展示
5. 注明洗涤方式""",
            "category": "clothing_rules"
        }
    ]
    
    for item_data in knowledge_items:
        existing = db.query(Knowledge).filter(
            Knowledge.title == item_data["title"]
        ).first()
        
        if not existing:
            knowledge = Knowledge(**item_data)
            db.add(knowledge)
    
    db.commit()


def init_model_config(db: Session):
    """Initialize model configuration"""
    models = [
        {
            "model_name": "qwen-max",
            "provider": "alibaba",
            "model_id": "qwen-max",
            "api_key": settings.alibaba_api_key,
            "api_base_url": settings.alibaba_api_base_url,
            "temperature": 0.7,
            "max_tokens": 2048,
            "enabled": True
        },
        {
            "model_name": "deepseek-chat",
            "provider": "deepseek",
            "model_id": "deepseek-chat",
            "api_key": settings.deepseek_api_key,
            "api_base_url": settings.deepseek_api_base_url,
            "temperature": 0.7,
            "max_tokens": 2048,
            "enabled": True
        }
    ]
    
    for model_data in models:
        existing = db.query(ModelConfig).filter(
            ModelConfig.model_name == model_data["model_name"]
        ).first()
        
        if not existing:
            model = ModelConfig(**model_data)
            db.add(model)
    
    db.commit()


def main():
    """Run initialization"""
    print("Initializing application data...")
    
    init_db()
    
    db = SessionLocal()
    
    try:
        print("Creating prompt templates...")
        init_prompt_templates(db)
        
        print("Creating knowledge base...")
        init_knowledge_base(db)
        
        print("Creating model configurations...")
        init_model_config(db)
        
        print("Initialization complete!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
