"""
Agent A - 对话式CBT引导者
负责与用户进行结构化的CBT风格对话
使用 OpenAI GPT-4o-mini 实现
"""
from typing import List, Dict, Optional
import json
from datetime import datetime
import os

# 尝试导入 OpenAI 库
OPENAI_AVAILABLE = False
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    print("警告: OpenAI库未安装，将使用规则基础的回退模式")


# CBT 系统提示词
CBT_SYSTEM_PROMPT = """You are a CBT (Cognitive Behavioral Therapy) conversational assistant.

Your job is to gently guide the user through a structured CBT daily session.

You must follow these rules:

CBT Treatment Structure You Must Follow

Guide the user step by step to talk about the following nine items:

Presenting Problem – what bothered them today

Situation Description – what happened, where, when, with whom

Emotion Identification – what emotions they felt, intensity 0–100

Physical/Somatic Reactions

Automatic Thoughts – first thoughts that popped up

Behavioral Response

Consequences / After-effects

Desired Change – what they hope to improve

Anything else they want to add

Communication Style Requirements

Be warm, supportive, and non-judgmental

Use short, simple, emotionally safe language

Ask one question at a time

Never diagnose, label, or give medical advice

Never invalidate feelings

Never rush the user

Examples of tone:

"We can take this slowly."

"You don't need to be perfect here."

"You can say as much or as little as you feel comfortable."

"It's okay if you are unsure—you're doing fine."

Conversation Flow

Start with a grounding, warm welcome

Ask about today's biggest challenge (Presenting Problem)

Move through each CBT step in order

Allow the user to respond fully

Only proceed when the user is ready

When the user says they're done, end with a calm closing summary

When the User Says the Session Is Finished

Politely:

Reflect key points of what they shared

Validate their effort

Offer emotional grounding

Tell them they can come back anytime

Do NOT make clinical judgments or diagnoses.

Your Output

Your role is only to guide the conversation.

Do NOT produce analysis or scores.

Do NOT output JSON.

Those are handled by another agent.

Note: Your reply should be as brief as possible, avoid bolding or other formatting, and keep the reader engaged, encouraging them to say as much as possible.
Use English answer me please.
"""


class AgentConversation:
    """Agent A: 负责引导用户进行CBT对话"""

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化对话Agent
        Args:
            api_key: OpenAI API密钥（可选，如果未提供则从环境变量读取）
        """
        self.api_key = api_key
        self.conversation_history: List[Dict] = []
        self.session_summary: str = ""
        self.current_phase: str = "greeting"  # greeting, active, closing, ended

        # 初始化 OpenAI 客户端
        self.use_ai = False
        self.client = None
        self.ai_model = "gpt-5.1"  

        # 自动从环境变量读取API密钥（如果没有直接传入）
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")

        # 尝试初始化 OpenAI 客户端
        if api_key and OPENAI_AVAILABLE:
            try:
                self.client = OpenAI(api_key=api_key)
                self.use_ai = True
                print(f"✓ OpenAI客户端初始化成功，使用模型: {self.ai_model}")
            except Exception as e:
                print(f"⚠ 初始化OpenAI客户端失败: {type(e).__name__}: {e}")
                print(f"api_key: {api_key}")
                print("将使用规则基础的回退模式")
                self.use_ai = False
                self.client = None
        else:
            if not api_key:
                print("⚠ 未提供OpenAI API密钥，将使用规则基础的回退模式")
            if not OPENAI_AVAILABLE:
                print("⚠ OpenAI库未安装，将使用规则基础的回退模式")
        
    def start_session(self, user_id: str) -> str:
        """开始新的CBT会话"""
        self.conversation_history = []
        self.current_phase = "active"
        
        # 使用指定的欢迎语
        greeting = "Welcome back, let's get started. Is there anything you feel you need to discuss today？"
        
        self._add_to_history("assistant", greeting)
        return greeting
    
    def process_user_input(self, user_input: str) -> str:
        """
        处理用户输入并返回引导性回复
        Args:
            user_input: 用户的输入
        Returns:
            Agent的回复
        """
        # 检查用户是否想结束会话
        if self._check_end_session(user_input):
            return self._end_session()

        # 添加用户消息到历史
        self._add_to_history("user", user_input)

        # 根据是否有AI客户端生成回复
        if self.use_ai and self.client:
            response = self._generate_response_with_openai(user_input)
        else:
            response = self._generate_response_fallback(user_input)

        self._add_to_history("assistant", response)

        # 检查回复是否表示会话结束
        if self._check_response_ends_session(response):
            self.current_phase = "ended"

        return response
    
    def _check_end_session(self, user_input: str) -> bool:
        """检查用户是否想结束会话"""
        end_keywords = [
            "结束", "完成", "没有了", "没什么了", "就这些", 
            "结束会话", "完成对话", "说完了", "就这些了",
            "done", "finished", "that's all", "nothing else"
        ]
        user_input_lower = user_input.lower()
        return any(keyword in user_input_lower for keyword in end_keywords)
    
    def _check_response_ends_session(self, response: str) -> bool:
        """检查回复是否表示会话结束"""
        end_indicators = [
            "下次再见", "随时回来", "可以回来", "come back anytime"
        ]
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in end_indicators)
    
    def _generate_response_with_openai(self, user_input: str) -> str:
        """
        使用 OpenAI GPT API 生成回复
        """
        try:
            # 构建消息列表
            messages = [
                {"role": "system", "content": CBT_SYSTEM_PROMPT}
            ]

            # 添加对话历史（只包含用户和助手的消息，不包括timestamp）
            for msg in self.conversation_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

            # 调用 OpenAI API（标准方式，不使用流式）
            response = self.client.chat.completions.create(
                model=self.ai_model,
                messages=messages,
                max_completion_tokens=500,
            )

            # 提取回复文本
            print(response.model_dump())
            reply = response.choices[0].message.content.strip()

            if not reply:
                print("OpenAI API 返回空响应，使用回退模式")
                return self._generate_response_fallback(user_input)

            return reply

        except Exception as e:
            print(f"OpenAI API调用失败: {type(e).__name__}: {e}")
            print("使用回退模式")
            return self._generate_response_fallback(user_input)

    def _generate_response_fallback(self, user_input: str) -> str:
        """
        回退模式：使用规则基础的回复生成
        当GPT不可用时使用
        """
        # 简化的规则基础回复生成
        if self.current_phase == "greeting":
            self.current_phase = "active"
            return (
                "谢谢你的分享。我注意到你提到了一些感受。\n\n"
                "让我们更深入地了解一下：你能描述一下这种感受的强度吗？"
                "（可以用0-10的数字，0表示完全没有，10表示非常强烈）"
            )
        
        elif self.current_phase == "active":
            # 根据用户输入的关键词给出不同的回复
            user_lower = user_input.lower()
            
            if any(word in user_lower for word in ["感觉", "感受", "情绪", "心情"]):
                return (
                    "我理解你的感受。能告诉我，当你有这种感受时，"
                    "你的身体有什么反应吗？比如心跳加快、紧张、或者其他的身体感觉？"
                )
            elif any(word in user_lower for word in ["发生", "事情", "情况", "当时"]):
                return (
                    "明白了。当这件事发生时，你脑海中出现了什么想法？\n\n"
                    "试着描述一下当时你对自己、对他人、或对情况的看法。"
                )
            elif any(word in user_lower for word in ["想法", "认为", "觉得", "以为"]):
                return (
                    "好的，我听到了你的想法。\n\n"
                    "那么，当你有这些想法和感受时，你做了什么？"
                    "或者你当时想做什么但没有做？"
                )
            elif any(word in user_lower for word in ["做", "行动", "行为", "反应"]):
                return (
                    "我理解了你的行为反应。\n\n"
                    "现在让我们换个角度思考：对于同样的情况，"
                    "有没有其他可能的解释或想法？"
                )
            else:
                return (
                    "谢谢你的分享。能告诉我更多关于这件事的细节吗？"
                    "比如它发生在什么时候、什么地方，还有谁在场？"
                )
        
        else:
            return (
                "我理解。如果你还有其他想说的，随时告诉我。\n"
                "如果没有，我们可以结束今天的会话。"
            )
    
    def _add_to_history(self, role: str, content: str):
        """添加消息到对话历史"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def _end_session(self) -> str:
        """结束会话并生成总结"""
        if self.use_ai and self.client:
            try:
                closing_message = self._end_session_with_openai()
                
                if not closing_message:
                    return self._end_session_fallback()

                self._add_to_history("assistant", closing_message)
                self.current_phase = "ended"
                return closing_message

            except Exception as e:
                print(f"生成结束语失败: {type(e).__name__}: {e}")
                return self._end_session_fallback()
        else:
            return self._end_session_fallback()

    def _end_session_with_openai(self) -> Optional[str]:
        """使用OpenAI生成结束语"""
        try:
            messages = [
                {"role": "system", "content": CBT_SYSTEM_PROMPT}
            ]

            # 添加完整对话历史
            for msg in self.conversation_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

            # 添加结束提示
            messages.append({
                "role": "user",
                "content": "I've finished speaking and would like to conclude today's conversation. Please give me a warm and encouraging closing remark."
            })

            response = self.client.chat.completions.create(
                model=self.ai_model,
                messages=messages,
                temperature=0.7,
                max_tokens=300,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"OpenAI生成结束语失败: {type(e).__name__}: {e}")
            return None
    
    def _end_session_fallback(self) -> str:
        """回退模式的结束语"""
        closing_message = (
            "好的，今天的会话就到这里。\n\n"
            "你今天分享了很多有价值的内容，这需要很大的勇气。\n"
            "请记住，改变需要时间，你已经迈出了重要的一步。\n\n"
            "我们下次再见！"
        )
        
        self._add_to_history("assistant", closing_message)
        self.current_phase = "ended"
        return closing_message
    
    def get_conversation_transcript(self) -> str:
        """获取完整的对话记录（Markdown格式）"""
        transcript = "# CBT会话记录\n\n"
        transcript += f"**日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        transcript += "---\n\n"
        
        for msg in self.conversation_history:
            role_name = "助手" if msg["role"] == "assistant" else "用户"
            transcript += f"**{role_name}** ({msg['timestamp']}):\n\n"
            transcript += f"{msg['content']}\n\n"
            transcript += "---\n\n"
        
        return transcript
    
    def get_summary_for_analysis(self) -> str:
        """
        生成供Agent B分析的关键信息摘要
        提取用户的重要陈述
        """
        user_messages = [
            msg["content"] for msg in self.conversation_history 
            if msg["role"] == "user"
        ]
        
        summary = "用户今日会话摘要：\n\n"
        summary += "\n".join([f"- {msg}" for msg in user_messages])
        
        return summary
    
    def is_session_ended(self) -> bool:
        """检查会话是否已结束"""
        return self.current_phase == "ended"
