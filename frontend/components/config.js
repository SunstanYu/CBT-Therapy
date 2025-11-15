/**
 * 共享配置文件
 * 定义全局配置变量
 */

// 检查是否已经声明，避免重复声明
if (typeof window.API_BASE === 'undefined') {
    window.API_BASE = 'http://localhost:8000';
}

if (typeof window.currentUserId === 'undefined') {
    window.currentUserId = 1; // 默认用户ID
}

