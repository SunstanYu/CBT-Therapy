"""
Orchestrator - 协调Agent A和Agent B的工作流程
"""
from typing import Dict, Optional
from datetime import datetime
import sys
from .agent_conversation import AgentConversation
from .agent_analysis import AgentAnalysis


class CBTOrchestrator:
    """协调两个Agent的工作"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化协调器
        Args:
            api_key: API密钥（可选）
        """
        self.agent_a = AgentConversation(api_key=api_key)
        self.agent_b = AgentAnalysis(api_key=api_key)
        self.current_user_id: Optional[str] = None
        self.session_active: bool = False
    
    def start_session(self, user_id: str) -> str:
        """
        开始新的CBT会话
        Args:
            user_id: 用户ID
        Returns:
            Agent A的初始问候
        """
        self.current_user_id = user_id
        self.session_active = True
        return self.agent_a.start_session(user_id)
    
    def process_user_message(self, user_input: str) -> Dict:
        """
        处理用户消息
        Args:
            user_input: 用户输入
        Returns:
            包含Agent A回复和分析结果的字典
        """
        if not self.session_active:
            raise ValueError("会话未激活，请先调用start_session")
        
        # Agent A处理用户输入并生成回复
        agent_a_response = self.agent_a.process_user_input(user_input)
        
        # 每次用户输入后，Agent B 都进行评估分析
        # 使用用户输入作为评估内容
        analysis_result = None
        try:
            print("="*80, flush=True)
            print("🔄 Orchestrator: 开始调用 Agent B 进行分析...", flush=True)
            print("="*80, flush=True)
            
            analysis_result = self.agent_b.analyze(user_input)
            
            # 注意：详细的评估结果已经在 agent_b.analyze() 内部打印了
            # 这里只打印一个简短的确认信息
            if analysis_result:
                print("="*80, flush=True)
                print(f"✅ Orchestrator: Agent B 已完成单次评估 (日期: {analysis_result.get('date', 'N/A')})", flush=True)
                print("="*80, flush=True)
        except Exception as e:
            print("="*80, flush=True)
            print(f"⚠ Orchestrator: Agent B 评估失败: {type(e).__name__}: {e}", flush=True)
            import traceback
            traceback.print_exc()
            print("="*80, flush=True)
        
        # 如果会话结束，进行最终综合分析
        if self.agent_a.is_session_ended():
            self.session_active = False
            summary = self.agent_a.get_summary_for_analysis()
            # 进行最终综合分析
            try:
                print("="*80, flush=True)
                print("🔄 Orchestrator: 开始进行最终综合分析...", flush=True)
                print("="*80, flush=True)
                
                final_analysis = self.agent_b.analyze(summary)
                analysis_result = final_analysis  # 使用最终综合分析结果
                
                print("="*80, flush=True)
                print(f"✅ Orchestrator: Agent B 已完成最终综合分析 (日期: {final_analysis.get('date', 'N/A')})", flush=True)
                print("="*80, flush=True)
            except Exception as e:
                print("="*80, flush=True)
                print(f"⚠ Orchestrator: Agent B 最终分析失败: {type(e).__name__}: {e}", flush=True)
                import traceback
                traceback.print_exc()
                print("="*80, flush=True)
        
        return {
            "response": agent_a_response,
            "session_ended": self.agent_a.is_session_ended(),
            "analysis": analysis_result
        }
    
    def end_session(self) -> Dict:
        """
        主动结束会话并返回完整分析
        Returns:
            包含对话记录和分析结果的字典
        """
        if not self.session_active:
            raise ValueError("会话未激活")
        
        # 获取会话摘要
        summary = self.agent_a.get_summary_for_analysis()
        
        # Agent B进行分析
        analysis_result = self.agent_b.analyze(summary)
        
        # 获取完整对话记录
        transcript = self.agent_a.get_conversation_transcript()
        
        self.session_active = False
        
        return {
            "transcript": transcript,
            "summary": summary,
            "analysis": analysis_result
        }
    
    def get_conversation_transcript(self) -> str:
        """获取当前会话的完整记录"""
        return self.agent_a.get_conversation_transcript()
    
    def is_session_active(self) -> bool:
        """检查会话是否活跃"""
        return self.session_active
    
    def get_user_id(self) -> Optional[str]:
        """获取当前用户ID"""
        return self.current_user_id

