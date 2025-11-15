"""
每日记录模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.db.base import Base


class DailyRecord(Base):
    """每日CBT会话记录表"""
    __tablename__ = "daily_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    conversation_transcript = Column(Text)  # Agent A的完整对话记录
    conversation_summary = Column(Text)  # 供分析用的摘要
    analysis_json = Column(JSON)  # Agent B的JSON分析结果
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", backref="daily_records")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date,
            "conversation_transcript": self.conversation_transcript,
            "conversation_summary": self.conversation_summary,
            "analysis_json": self.analysis_json,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

