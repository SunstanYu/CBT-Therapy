"""
用户会话API - 处理CBT每日会话的开始和结束
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from backend.db.orm import get_db
from backend.agents.orchestrator import CBTOrchestrator
from backend.models.user import User
from backend.models.daily_record import DailyRecord
from backend.models.profile import UserProfile
from backend.config import config

router = APIRouter(prefix="/api/session", tags=["session"])

# 存储活跃会话（实际部署时应该使用Redis等）
active_sessions: dict = {}


class StartSessionRequest(BaseModel):
    user_id: int


class UserMessageRequest(BaseModel):
    user_id: int
    message: str


class EndSessionRequest(BaseModel):
    user_id: int


@router.post("/start")
async def start_session(request: StartSessionRequest, db: Session = Depends(get_db)):
    """开始新的CBT会话"""
    # 检查用户是否存在
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 如果已有活跃会话，先清理它（允许重新开始会话）
    if request.user_id in active_sessions:
        try:
            # 尝试保存旧会话（如果可能）
            old_orchestrator = active_sessions[request.user_id]
            if old_orchestrator.is_session_active():
                # 如果会话还在进行中，尝试结束它
                try:
                    result = old_orchestrator.end_session()
                    await _save_session_record(
                        db, request.user_id, old_orchestrator, result["analysis"]
                    )
                except Exception as e:
                    # 如果结束失败，只记录日志，继续清理
                    print(f"清理旧会话时出错: {e}")
        except Exception as e:
            print(f"处理旧会话时出错: {e}")
        finally:
            # 清理旧会话
            del active_sessions[request.user_id]
    
    # 创建新的协调器实例（从环境变量读取API密钥）
    api_key = config.get_api_key()
    orchestrator = CBTOrchestrator(api_key=api_key)
    initial_message = orchestrator.start_session(str(request.user_id))
    
    # 保存会话
    active_sessions[request.user_id] = orchestrator
    
    return {
        "success": True,
        "message": initial_message,
        "user_id": request.user_id
    }


@router.post("/message")
async def send_message(request: UserMessageRequest, db: Session = Depends(get_db)):
    """发送用户消息并获取回复"""
    # 检查会话是否存在
    if request.user_id not in active_sessions:
        raise HTTPException(status_code=404, detail="会话不存在，请先开始会话")
    
    orchestrator = active_sessions[request.user_id]
    
    try:
        result = orchestrator.process_user_message(request.message)
        
        response_data = {
            "success": True,
            "response": result["response"],
            "session_ended": result["session_ended"]
        }
        
        # 每次有评估结果时，都保存/更新到数据库（实时更新）
        if result.get("analysis"):
            try:
                await _save_session_record(
                    db, request.user_id, orchestrator, result["analysis"]
                )
                print(f"✅ 已保存用户 {request.user_id} 的最新评估到数据库", flush=True)
            except Exception as e:
                print(f"⚠ 保存评估记录失败: {e}", flush=True)
        
        # 如果会话结束，清理活跃会话
        if result["session_ended"]:
            if result.get("analysis"):
                response_data["analysis"] = result["analysis"]
            # 清理活跃会话
            del active_sessions[request.user_id]
        
        return response_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理消息时出错: {str(e)}")


@router.post("/end")
async def end_session(request: EndSessionRequest, db: Session = Depends(get_db)):
    """主动结束会话"""
    if request.user_id not in active_sessions:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    orchestrator = active_sessions[request.user_id]
    
    try:
        result = orchestrator.end_session()
        
        # 保存记录
        await _save_session_record(
            db, request.user_id, orchestrator, result["analysis"]
        )
        
        # 清理活跃会话
        del active_sessions[request.user_id]
        
        return {
            "success": True,
            "transcript": result["transcript"],
            "summary": result["summary"],
            "analysis": result["analysis"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"结束会话时出错: {str(e)}")


async def _save_session_record(
    db: Session, 
    user_id: int, 
    orchestrator: CBTOrchestrator,
    analysis: dict
):
    """保存会话记录到数据库"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 检查今天是否已有记录
    existing_record = db.query(DailyRecord).filter(
        DailyRecord.user_id == user_id,
        DailyRecord.date == today
    ).first()
    
    transcript = orchestrator.get_conversation_transcript()
    summary = orchestrator.agent_a.get_summary_for_analysis()
    
    if existing_record:
        # 更新现有记录（每次评估都更新，保持最新状态）
        existing_record.conversation_transcript = transcript
        existing_record.conversation_summary = summary
        existing_record.analysis_json = analysis
        existing_record.updated_at = datetime.utcnow()
    else:
        # 创建新记录
        new_record = DailyRecord(
            user_id=user_id,
            date=today,
            conversation_transcript=transcript,
            conversation_summary=summary,
            analysis_json=analysis
        )
        db.add(new_record)
    
    # 更新用户档案
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)
    
    profile.update_from_analysis(analysis)
    
    db.commit()

