"""
Agent Service - Task Decomposition Engine
Enterprise Design:
- Standard Agent workflow: Plan → Decide → Execute → Merge
- Multi-step content generation pipeline
- RAG augmentation integration
- Structured output guarantee
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session
import time

from app.services.llm_service import llm_service, LLMResponse
from app.services.rag_service import RAGService
from app.services.prompt_service import PromptService


class EcommerceAgent:
    """
    E-commerce Content Generation Agent
    
    Workflow:
    1. Plan: Analyze user input, decompose into tasks
    2. Decide: Determine if RAG is needed
    3. Execute: Run each step with LLM
    4. Merge: Combine results into unified output
    
    Output Structure:
    {
        "titles": { "pdd": "", "tb": "", "xhs": "" },
        "selling_points": [],
        "faq": [],
        "raw_notes": ""
    }
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.rag_service = RAGService(db)
        self.prompt_service = PromptService(db)
    
    def run(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute full agent workflow
        
        Args:
            user_input: User's e-commerce content request
            context: Additional context (product info, etc.)
        
        Returns:
            Dict: Structured output with titles, selling points, etc.
        """
        start_time = time.time()
        
        # 1. Plan: Decompose task into steps
        plan = self._plan(user_input, context)
        
        # 2. Decide: Check if RAG is needed
        rules_context = ""
        if plan["requires_rag"]:
            rules_context = self._retrieve_rules(plan["category"])
        
        # 3. Execute: Run each step
        step_results = []
        for step in plan["steps"]:
            result = self._execute_step(step, rules_context, context)
            step_results.append(result)
        
        # 4. Merge: Combine results
        final_result = self._merge_results(step_results)
        
        # Calculate total latency
        total_latency_ms = int((time.time() - start_time) * 1000)
        
        return {
            **final_result,
            "execution_stats": {
                "total_latency_ms": total_latency_ms,
                "step_count": len(step_results),
                "success_steps": sum(1 for r in step_results if r["success"])
            }
        }
    
    def _plan(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Task decomposition - plan the execution steps
        
        Returns:
            Dict: Execution plan with steps and RAG requirement
        """
        product_name = context.get("product_name", "")
        category = context.get("category", "general")
        
        plan = {
            "task_type": "content_generation",
            "category": category,
            "requires_rag": True,
            "steps": [
                {
                    "step_id": 1,
                    "name": "generate_titles",
                    "description": "生成多平台商品标题",
                    "prompt_template": "title_generation",
                    "schema": {
                        "pdd": "拼多多标题，30字以内，包含关键词",
                        "tb": "淘宝标题，60字以内，包含营销词",
                        "xhs": "小红书标题，吸引眼球，带话题"
                    }
                },
                {
                    "step_id": 2,
                    "name": "extract_selling_points",
                    "description": "提取商品核心卖点",
                    "prompt_template": "selling_points_extraction",
                    "schema": {
                        "selling_points": "卖点列表，每个卖点不超过20字"
                    }
                },
                {
                    "step_id": 3,
                    "name": "generate_faq",
                    "description": "生成客服常见问题",
                    "prompt_template": "faq_generation",
                    "schema": {
                        "faq": "FAQ列表，包含问题和答案"
                    }
                }
            ]
        }
        
        return plan
    
    def _retrieve_rules(self, category: str) -> str:
        """Retrieve relevant rules from knowledge base"""
        rules = []
        
        # Title rules
        title_rules = self.rag_service.get_rules_for_category("title_rules")
        if title_rules:
            rules.append(f"【标题规范】\n{title_rules}")
        
        # Category rules
        category_rules = self.rag_service.get_rules_for_category(f"{category}_rules")
        if category_rules:
            rules.append(f"【类目规则】\n{category_rules}")
        
        return "\n\n".join(rules)
    
    def _execute_step(self, step: Dict[str, Any], rules_context: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single step
        
        Args:
            step: Step definition
            rules_context: RAG retrieved context
            context: User context
        
        Returns:
            Dict: Step execution result
        """
        product_name = context.get("product_name", "")
        features = context.get("features", [])
        description = context.get("description", "")
        
        # Build prompt with rules augmentation
        prompt = f"""你是一个专业的电商运营助手。
        
商品信息：
- 商品名称：{product_name}
- 商品特点：{', '.join(features) if features else '暂无'}
- 商品描述：{description}

{rules_context}

任务：{step['description']}

请根据以上信息完成任务。"""
        
        # Call LLM with structured output
        result = llm_service.call_structured(
            prompt=prompt,
            expected_schema=step["schema"],
            temperature=0.7,
            max_tokens=1024
        )
        
        if result.success:
            _, parsed_data = llm_service.validate_json(result.content)
            return {
                "step_id": step["step_id"],
                "name": step["name"],
                "success": True,
                "data": parsed_data,
                "latency_ms": result.latency_ms,
                "tokens": {
                    "input": result.input_tokens,
                    "output": result.output_tokens,
                    "total": result.total_tokens
                }
            }
        
        return {
            "step_id": step["step_id"],
            "name": step["name"],
            "success": False,
            "data": {},
            "error": result.error,
            "latency_ms": result.latency_ms
        }
    
    def _merge_results(self, step_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge step results into unified output
        
        Args:
            step_results: List of step execution results
        
        Returns:
            Dict: Unified structured output
        """
        merged = {
            "titles": {
                "pdd": "",
                "tb": "",
                "xhs": ""
            },
            "selling_points": [],
            "faq": [],
            "raw_notes": ""
        }
        
        for result in step_results:
            if not result["success"] or not result["data"]:
                continue
            
            data = result["data"]
            
            if result["name"] == "generate_titles":
                merged["titles"]["pdd"] = data.get("pdd", "")
                merged["titles"]["tb"] = data.get("tb", "")
                merged["titles"]["xhs"] = data.get("xhs", "")
            
            elif result["name"] == "extract_selling_points":
                merged["selling_points"] = data.get("selling_points", [])
            
            elif result["name"] == "generate_faq":
                merged["faq"] = data.get("faq", [])
        
        return merged


class AgentService:
    """Agent service wrapper for API"""
    
    def __init__(self, db: Session):
        self.db = db
        self.agent = EcommerceAgent(db)
    
    def generate_content(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate e-commerce content via Agent
        
        Args:
            user_input: User request
            context: Product context
        
        Returns:
            Dict: Generated content with execution stats
        """
        return self.agent.run(user_input, context)
