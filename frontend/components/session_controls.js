/**
 * 会话控制组件
 */
// 使用全局配置（从 config.js 加载）
// 确保全局变量已定义
if (typeof window.API_BASE === 'undefined') {
    window.API_BASE = 'http://localhost:8000';
}
if (typeof window.currentUserId === 'undefined') {
    window.currentUserId = 1;
}
let sessionActive = false;

async function startSession() {
    const userId = window.currentUserId || 1;
    console.log('开始会话按钮被点击，用户ID:', userId);
    
    // 如果前端认为会话已激活，先重置状态
    if (sessionActive) {
        console.log('检测到前端会话状态为激活，重置状态');
        sessionActive = false;
        updateSessionStatus('未开始');
    }
    
    try {
        const apiBase = window.API_BASE || 'http://localhost:8000';
        const response = await fetch(`${apiBase}/api/session/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId
            })
        });
        
        console.log('API响应状态:', response.status);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: '未知错误' }));
            // 后端现在会自动清理旧会话，所以这个错误应该不会再出现
            // 但如果出现，可以提示用户
            throw new Error(errorData.detail || `HTTP错误: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('API响应数据:', data);
        
        if (data.success) {
            sessionActive = true;
            updateSessionStatus('进行中');
            
            // 启用输入
            document.getElementById('messageInput').disabled = false;
            document.getElementById('sendBtn').disabled = false;
            document.getElementById('endSessionBtn').disabled = false;
            document.getElementById('startSessionBtn').disabled = true;
            
            // 清空聊天记录
            document.getElementById('chatMessages').innerHTML = '';
            
            // 显示初始消息
            const chatWindow = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message assistant-message';
            messageDiv.textContent = data.message;
            chatWindow.appendChild(messageDiv);
            
            // 隐藏分析结果
            document.getElementById('analysisResult').style.display = 'none';
        } else {
            console.error('开始会话失败，响应数据:', data);
            alert('开始会话失败: ' + (data.detail || '未知错误'));
        }
    } catch (error) {
        console.error('开始会话失败:', error);
        alert('开始会话失败: ' + error.message);
    }
}

async function endSession() {
    if (!sessionActive) return;
    
    try {
        const apiBase = window.API_BASE || 'http://localhost:8000';
        const userId = window.currentUserId || 1;
        const response = await fetch(`${apiBase}/api/session/end`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_id: userId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            sessionActive = false;
            updateSessionStatus('已结束');
            
            // 禁用输入
            document.getElementById('messageInput').disabled = true;
            document.getElementById('sendBtn').disabled = true;
            document.getElementById('endSessionBtn').disabled = true;
            document.getElementById('startSessionBtn').disabled = false;
            
            // 显示分析结果
            if (data.analysis) {
                showAnalysisResult(data.analysis);
            }
        } else {
            alert('结束会话失败');
        }
    } catch (error) {
        console.error('结束会话失败:', error);
        alert('网络错误，请检查连接');
    }
}

function updateSessionStatus(status) {
    const statusIndicator = document.getElementById('sessionStatus');
    statusIndicator.textContent = `状态: ${status}`;
    
    if (status === '进行中') {
        statusIndicator.className = 'status-indicator active';
    } else {
        statusIndicator.className = 'status-indicator';
    }
}

function showAnalysisResult(analysis) {
    const analysisResult = document.getElementById('analysisResult');
    const analysisContent = document.getElementById('analysisContent');
    
    analysisContent.textContent = JSON.stringify(analysis, null, 2);
    analysisResult.style.display = 'block';
}

// 绑定按钮事件 - 确保DOM加载完成
function initSessionControls() {
    const startBtn = document.getElementById('startSessionBtn');
    const endBtn = document.getElementById('endSessionBtn');
    
    if (startBtn) {
        startBtn.addEventListener('click', startSession);
        console.log('开始会话按钮事件已绑定');
    } else {
        console.error('找不到开始会话按钮');
    }
    
    if (endBtn) {
        endBtn.addEventListener('click', endSession);
        console.log('结束会话按钮事件已绑定');
    } else {
        console.error('找不到结束会话按钮');
    }
}

// 如果DOM已加载，立即执行；否则等待DOMContentLoaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSessionControls);
} else {
    initSessionControls();
}

