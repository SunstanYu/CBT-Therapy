"""
统一的数据库Base
所有模型都应该从这个Base继承
"""
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

