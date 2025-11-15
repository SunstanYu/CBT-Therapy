"""
FastAPI 主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from backend.api import user_session_api, analysis_api, doctor_dashboard_api, speech_api
from backend.db.orm import init_db

# 创建FastAPI应用
app = FastAPI(
    title="CBT Therapy Assistant API",
    description="认知行为疗法治疗助手API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加缓存控制中间件（禁用静态文件缓存，便于开发）
class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/static/"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

app.add_middleware(NoCacheMiddleware)

# 注册路由
app.include_router(user_session_api.router)
app.include_router(analysis_api.router)
app.include_router(doctor_dashboard_api.router)
app.include_router(speech_api.router)


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    init_db()
    print("数据库初始化完成")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


# 提供静态文件服务（前端页面）
# 注意：静态文件路由应该在API路由之后注册
import os
from pathlib import Path

# 获取项目根目录
BASE_DIR = Path(__file__).parent.parent

# 提供前端静态文件
frontend_dir = BASE_DIR / "frontend"
if frontend_dir.exists():
    # 提供前端静态资源（CSS、JS等）
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")
    
    # 提供前端页面
    @app.get("/")
    async def index():
        """首页 - 主界面"""
        landing_path = frontend_dir / "pages" / "landing.html"
        if landing_path.exists():
            return FileResponse(str(landing_path))
        return {"message": "CBT Therapy Assistant API", "docs": "/docs"}
    
    @app.get("/chat")
    async def chat():
        """对话界面"""
        chat_path = frontend_dir / "pages" / "chat.html"
        if chat_path.exists():
            return FileResponse(str(chat_path))
        return {"error": "Chat page not found"}
    
    @app.get("/history")
    async def history():
        """历史记录页面"""
        history_path = frontend_dir / "pages" / "history.html"
        if history_path.exists():
            return FileResponse(str(history_path))
        return {"error": "History page not found"}
    
    @app.get("/dashboard")
    async def dashboard():
        """医生后台页面"""
        dashboard_path = frontend_dir / "pages" / "dashboard.html"
        if dashboard_path.exists():
            return FileResponse(str(dashboard_path))
        return {"error": "Dashboard page not found"}
    
    @app.get("/patient-report")
    async def patient_report():
        """患者评估报告页面"""
        report_path = frontend_dir / "pages" / "patient_report.html"
        if report_path.exists():
            return FileResponse(str(report_path))
        return {"error": "Patient report page not found"}
else:
    @app.get("/")
    async def root():
        """根路径"""
        return {
            "message": "CBT Therapy Assistant API",
            "version": "1.0.0",
            "docs": "/docs"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

