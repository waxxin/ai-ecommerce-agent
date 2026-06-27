"""
LLM Service - Unified LLM Call Layer
Enterprise Design:
- All AI calls must go through this service
- Supports multiple providers (Alibaba, DeepSeek, OpenAI)
- Unified error handling and logging
- Structured JSON output validation
"""
import json
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass

from app.core.config import settings


@dataclass
class LLMResponse:
    """Standard LLM response"""
    success: bool
    content: str = ""
    error: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    latency_ms: int = 0
    model_name: str = ""


class LLMClient:
    """Base LLM client interface"""
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        raise NotImplementedError


class AlibabaLLMClient(LLMClient):
    """Alibaba DashScope LLM client"""
    
    def __init__(self, api_key: str, api_base_url: str, model_id: str):
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.model_id = model_id
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        import requests
        
        start_time = time.time()
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model_id,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2048),
                "top_p": kwargs.get("top_p", 0.9)
            }
            
            response = requests.post(
                f"{self.api_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                return LLMResponse(
                    success=False,
                    error=f"API Error: {response.status_code} - {response.text}",
                    latency_ms=int((time.time() - start_time) * 1000)
                )
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            usage = data.get("usage", {})
            
            return LLMResponse(
                success=True,
                content=content,
                input_tokens=usage.get("prompt_tokens", 0),
                output_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
                latency_ms=int((time.time() - start_time) * 1000),
                model_name=self.model_id
            )
            
        except Exception as e:
            return LLMResponse(
                success=False,
                error=str(e),
                latency_ms=int((time.time() - start_time) * 1000),
                model_name=self.model_id
            )


class DeepSeekLLMClient(LLMClient):
    """DeepSeek LLM client"""
    
    def __init__(self, api_key: str, api_base_url: str, model_id: str):
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.model_id = model_id
    
    def generate(self, prompt: str, **kwargs) -> LLMResponse:
        import requests
        
        start_time = time.time()
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model_id,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2048),
                "top_p": kwargs.get("top_p", 0.9)
            }
            
            response = requests.post(
                f"{self.api_base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code != 200:
                return LLMResponse(
                    success=False,
                    error=f"API Error: {response.status_code} - {response.text}",
                    latency_ms=int((time.time() - start_time) * 1000)
                )
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            usage = data.get("usage", {})
            
            return LLMResponse(
                success=True,
                content=content,
                input_tokens=usage.get("prompt_tokens", 0),
                output_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
                latency_ms=int((time.time() - start_time) * 1000),
                model_name=self.model_id
            )
            
        except Exception as e:
            return LLMResponse(
                success=False,
                error=str(e),
                latency_ms=int((time.time() - start_time) * 1000),
                model_name=self.model_id
            )


class LLMService:
    """Unified LLM service"""
    
    def __init__(self):
        self.clients: Dict[str, LLMClient] = {}
        self._init_clients()
    
    def _init_clients(self):
        """Initialize LLM clients based on config"""
        if settings.alibaba_api_key:
            self.clients["alibaba"] = AlibabaLLMClient(
                api_key=settings.alibaba_api_key,
                api_base_url=settings.alibaba_api_base_url,
                model_id=settings.alibaba_model_id
            )
        
        if settings.deepseek_api_key:
            self.clients["deepseek"] = DeepSeekLLMClient(
                api_key=settings.deepseek_api_key,
                api_base_url=settings.deepseek_api_base_url,
                model_id=settings.deepseek_model_id
            )
    
    def call(self, prompt: str, provider: str = None, **kwargs) -> LLMResponse:
        """
        Unified LLM call interface
        
        Args:
            prompt: The prompt text
            provider: LLM provider ("alibaba", "deepseek", or None for default)
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            LLMResponse: Standardized response
        """
        target_provider = provider or settings.llm_provider
        
        if target_provider not in self.clients:
            return LLMResponse(
                success=False,
                error=f"Provider {target_provider} not configured"
            )
        
        return self.clients[target_provider].generate(prompt, **kwargs)
    
    def call_structured(self, prompt: str, expected_schema: Dict[str, str], provider: str = None, **kwargs) -> LLMResponse:
        """
        Call LLM with structured JSON output requirement
        
        Args:
            prompt: The prompt text
            expected_schema: Expected JSON schema with field descriptions
            provider: LLM provider
            **kwargs: Additional parameters
        
        Returns:
            LLMResponse: Response with validated JSON content
        """
        fields_desc = "\n".join([f"  \"{k}\": {v}" for k, v in expected_schema.items()])
        structured_prompt = f"""{prompt}

请严格按照以下JSON格式输出，不要包含任何其他文字、markdown格式或解释：
{{
{fields_desc}
}}"""
        
        result = self.call(structured_prompt, provider, **kwargs)
        
        if result.success:
            is_valid, _ = self.validate_json(result.content)
            if not is_valid:
                result.success = False
                result.error = "Invalid JSON output"
        
        return result
    
    def validate_json(self, content: str) -> tuple:
        """
        Validate if content is valid JSON
        
        Returns:
            (is_valid: bool, parsed_data: dict or error: str)
        """
        try:
            parsed = json.loads(content)
            return True, parsed
        except json.JSONDecodeError as e:
            return False, str(e)


llm_service = LLMService()
