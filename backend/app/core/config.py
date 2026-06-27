"""
Configuration Module
Handles environment variables and application settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    debug: bool = True
    secret_key: str = "your-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "ai_ecommerce"
    
    llm_provider: str = "alibaba"
    alibaba_api_key: str = ""
    alibaba_api_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    alibaba_model_id: str = "qwen-max"
    
    deepseek_api_key: str = ""
    deepseek_api_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model_id: str = "deepseek-chat"
    
    log_level: str = "INFO"
    
    @property
    def database_url(self) -> str:
        """Build database URL"""
        return f"mysql+mysqlconnector://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
