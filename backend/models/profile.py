"""
用户心理档案模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.db.base import Base


class UserProfile(Base):
    """用户长期心理档案表"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # 长期趋势数据（JSON格式存储时间序列）
    anxiety_trend = Column(JSON)  # [{"date": "2024-01-01", "score": 5}, ...]
    depression_trend = Column(JSON)
    stress_trend = Column(JSON)
    
    # 常见认知扭曲模式
    common_distortions = Column(JSON)  # ["全有或全无思维", "灾难化", ...]
    
    # 行为模式
    behavior_patterns = Column(JSON)  # ["回避", "拖延", ...]
    
    # 治疗师备注
    therapist_notes = Column(Text)
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = relationship("User", backref="profile")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "anxiety_trend": self.anxiety_trend or [],
            "depression_trend": self.depression_trend or [],
            "stress_trend": self.stress_trend or [],
            "common_distortions": self.common_distortions or [],
            "behavior_patterns": self.behavior_patterns or [],
            "therapist_notes": self.therapist_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def update_from_analysis(self, analysis_json: dict):
        """根据分析结果更新档案"""
        date = analysis_json.get("date")
        clinical_scores = analysis_json.get("clinical_scores", {})
        cbt_indicators = analysis_json.get("cbt_indicators", {})
        
        # 更新趋势数据
        if not self.anxiety_trend:
            self.anxiety_trend = []
        if not self.depression_trend:
            self.depression_trend = []
        if not self.stress_trend:
            self.stress_trend = []
        
        self.anxiety_trend.append({
            "date": date,
            "score": clinical_scores.get("anxiety_0_10", 0)
        })
        self.depression_trend.append({
            "date": date,
            "score": clinical_scores.get("depression_0_10", 0)
        })
        self.stress_trend.append({
            "date": date,
            "score": clinical_scores.get("stress_0_10", 0)
        })
        
        # 更新认知扭曲模式（累积）
        if not self.common_distortions:
            self.common_distortions = []
        new_distortions = cbt_indicators.get("cognitive_distortions", [])
        for dist in new_distortions:
            if dist not in self.common_distortions:
                self.common_distortions.append(dist)
        
        # 更新行为模式（累积）
        if not self.behavior_patterns:
            self.behavior_patterns = []
        new_behaviors = cbt_indicators.get("behavior_patterns", [])
        for beh in new_behaviors:
            if beh not in self.behavior_patterns:
                self.behavior_patterns.append(beh)
        
        self.updated_at = datetime.utcnow()

