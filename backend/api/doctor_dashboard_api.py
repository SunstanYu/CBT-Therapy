"""
医生后台API - 供医生查看用户记录和档案
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from backend.db.orm import get_db
from backend.models.user import User
from backend.models.daily_record import DailyRecord
from backend.models.profile import UserProfile

router = APIRouter(prefix="/api/doctor", tags=["doctor"])


class NotesRequest(BaseModel):
    notes: str


@router.get("/users")
async def get_all_users(db: Session = Depends(get_db)):
    """获取所有用户列表"""
    users = db.query(User).all()
    return {
        "success": True,
        "users": [user.to_dict() for user in users]
    }


@router.get("/user/{user_id}/profile")
async def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """获取用户完整心理档案"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    # 获取最近的记录
    recent_records = db.query(DailyRecord).filter(
        DailyRecord.user_id == user_id
    ).order_by(DailyRecord.date.desc()).limit(10).all()
    
    return {
        "success": True,
        "user": user.to_dict(),
        "profile": profile.to_dict() if profile else None,
        "recent_records": [record.to_dict() for record in recent_records]
    }


@router.get("/user/{user_id}/records")
async def get_user_records(
    user_id: int, 
    limit: Optional[int] = 50,
    db: Session = Depends(get_db)
):
    """获取用户的所有会话记录"""
    records = db.query(DailyRecord).filter(
        DailyRecord.user_id == user_id
    ).order_by(DailyRecord.date.desc()).limit(limit).all()
    
    return {
        "success": True,
        "user_id": user_id,
        "records": [record.to_dict() for record in records]
    }


@router.get("/user/{user_id}/record/{record_id}")
async def get_record_detail(
    user_id: int,
    record_id: int,
    db: Session = Depends(get_db)
):
    """获取特定记录的详细信息"""
    record = db.query(DailyRecord).filter(
        DailyRecord.id == record_id,
        DailyRecord.user_id == user_id
    ).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="记录不存在")
    
    return {
        "success": True,
        "record": record.to_dict()
    }


@router.post("/user/{user_id}/profile/notes")
async def update_therapist_notes(
    user_id: int,
    request: NotesRequest,
    db: Session = Depends(get_db)
):
    """更新治疗师备注"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    if not profile:
        profile = UserProfile(user_id=user_id, therapist_notes=request.notes)
        db.add(profile)
    else:
        profile.therapist_notes = request.notes
    
    db.commit()
    
    return {
        "success": True,
        "message": "备注已更新"
    }

