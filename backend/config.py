"""
应用配置模块
从环境变量读取配置
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """应用配置类"""
    
    # OpenAI API 密钥
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # 数据库配置
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./data/cbt_therapy.db"
    )
    
    # 应用配置
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    @classmethod
    def get_api_key(cls) -> str:
        """获取API密钥"""
        return cls.OPENAI_API_KEY or None


# 创建全局配置实例
config = Config()

