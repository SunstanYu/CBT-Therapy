"""
数据库ORM配置和会话管理
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 数据库URL（从环境变量读取，默认使用SQLite）
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./data/cbt_therapy.db"
)

# 创建引擎
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
else:
    engine = create_engine(DATABASE_URL)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """获取数据库会话（用于依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库表"""
    from backend.db.base import Base
    from backend.models import user, daily_record, profile
    
    # 导入所有模型以确保它们被注册到Base.metadata
    # 然后创建所有表
    Base.metadata.create_all(bind=engine)

