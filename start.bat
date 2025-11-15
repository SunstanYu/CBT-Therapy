@echo off
REM Windows启动脚本

echo 🚀 启动CBT Therapy Assistant...

REM 检查Docker是否运行
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker未运行，请先启动Docker
    exit /b 1
)

REM 构建并启动服务
echo 📦 构建Docker镜像...
docker-compose up -d --build

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 5 /nobreak >nul

REM 初始化数据库
echo 🗄️  初始化数据库...
docker-compose exec -T backend python -m backend.db.init_data

echo ✅ 服务已启动！
echo.
echo 📝 访问地址：
echo    - API文档: http://localhost:8000/docs
echo    - 健康检查: http://localhost:8000/health
echo.
echo 💡 查看日志: docker-compose logs -f backend
echo 💡 停止服务: docker-compose down

pause

