"""
分析API - 返回JSON格式的分析结果
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from backend.db.orm import get_db
from backend.models.daily_record import DailyRecord

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


class GetAnalysisRequest(BaseModel):
    user_id: int
    date: Optional[str] = None  # YYYY-MM-DD格式，不提供则返回最新的


@router.post("/get")
async def get_analysis(request: GetAnalysisRequest, db: Session = Depends(get_db)):
    """获取指定日期的分析结果"""
    query = db.query(DailyRecord).filter(DailyRecord.user_id == request.user_id)
    
    if request.date:
        query = query.filter(DailyRecord.date == request.date)
        record = query.first()
    else:
        # 获取最新的记录
        record = query.order_by(DailyRecord.date.desc()).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="未找到分析记录")
    
    return {
        "success": True,
        "date": record.date,
        "analysis": record.analysis_json
    }


@router.get("/user/{user_id}/history")
async def get_analysis_history(user_id: int, db: Session = Depends(get_db)):
    """获取用户的所有分析历史"""
    records = db.query(DailyRecord).filter(
        DailyRecord.user_id == user_id
    ).order_by(DailyRecord.date.desc()).all()
    
    history = []
    for record in records:
        history.append({
            "date": record.date,
            "analysis": record.analysis_json
        })
    
    return {
        "success": True,
        "user_id": user_id,
        "history": history
    }


@router.get("/user/{user_id}/latest")
async def get_latest_analysis(user_id: int, db: Session = Depends(get_db)):
    """获取用户最新的分析结果（用于实时显示）"""
    record = db.query(DailyRecord).filter(
        DailyRecord.user_id == user_id
    ).order_by(DailyRecord.date.desc()).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="未找到分析记录")
    
    return {
        "success": True,
        "date": record.date,
        "analysis": record.analysis_json
    }

