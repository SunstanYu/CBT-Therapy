"""
Agent B - 心理状态分析器
负责分析用户的心理状态并生成JSON格式的分析报告
使用 GPT 实现评估功能
"""
from typing import Dict, List, Optional
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


# 分析系统提示词
ANALYSIS_SYSTEM_PROMPT = """You are a professional CBT (Cognitive Behavioral Therapy) analysis agent.

Your task is to analyze the user's daily CBT session content and generate a structured JSON output containing:
- extracted CBT elements
- cognitive distortions detected
- clinical symptom severity scores
- risk assessment
- profile updates

You must not include conversational language in the output.
You must output JSON only.
No explanations, no markdown, no extra text.

Your Analysis Duties:

You must extract and analyze the following:

1. CBT Nine Components
From the user's text, extract:
- presenting_problem
- situation_description (when, where, who, what_happened)
- emotions + intensity (0-100 scale)
- physical_reactions
- automatic_thoughts
- behavioral_reactions
- consequences
- desired_change
- additional_notes

2. Cognitive Distortions Detection (必填)
Identify any cognitive distortions present in the user's language.
Possible categories include (but are not limited to):
- all-or-nothing thinking
- catastrophizing
- overgeneralization
- emotional reasoning
- mind reading
- fortune telling
- should statements
- personalization
- self-blame
- labeling
- discounting the positive

If none detected, return an empty list.

3. Clinical Scores (0–10)
Based on the user's content, estimate:
- anxiety_0_10
- depression_0_10
- stress_0_10
- rumination_0_10
- avoidance_0_10
- self_blame_0_10

Scores must be integers from 0–10.

4. Risk Assessment (自杀风险 & 危机等级)
Extract:
- self_harm_risk_0_3
  0 = no risk
  1 = mild thoughts
  2 = moderate ideation without plan
  3 = high risk, intent or plan
- crisis_flag: true/false
  true if:
  - suicidal ideation
  - hopelessness
  - self-harm behavior
  - severe panic/dissociation
  - inability to function

5. Profile Update
You must provide:
- trend_notes
- suggestions_to_therapist

These should be concise summaries.

⚠ Output Format Rules:
- Output valid JSON only
- No additional text
- Not wrapped in code fences
- All keys must be present even if empty
- Strings must not contain trailing commas

IMPORTANT: You must output ONLY valid JSON in the following exact format:
{
  "date": "YYYY-MM-DD",
  "presenting_problem": "",
  "situation_description": {
    "when": "",
    "where": "",
    "who": "",
    "what_happened": ""
  },
  "emotions": [
    {
      "type": "",
      "intensity_0_100": 0
    }
  ],
  "physical_reactions": [],
  "automatic_thoughts": [],
  "behavior_reactions": [],
  "consequences": "",
  "desired_change": "",
  "additional_notes": "",
  "cognitive_distortions": [],
  "clinical_scores": {
    "anxiety_0_10": 0,
    "depression_0_10": 0,
    "stress_0_10": 0,
    "rumination_0_10": 0,
    "avoidance_0_10": 0,
    "self_blame_0_10": 0
  },
  "risk_assessment": {
    "self_harm_risk_0_3": 0,
    "crisis_flag": false
  },
  "profile_update": {
    "trend_notes": "",
    "suggestions_to_therapist": ""
  }
}

▶ Begin analysis when user input is provided. Output JSON only."""


class AgentAnalysis:
    """Agent B: 负责分析用户心理状态"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化分析Agent
        Args:
            api_key: OpenAI API密钥（可选，如果未提供则从环境变量读取）
        """
        self.api_key = api_key
        self.assessment_history: List[Dict] = []  # 记录所有评估历史
        
        # 初始化 OpenAI 客户端
        self.use_gpt = False
        self.client = None
        self.ai_model = "gpt-5.1"  # 使用 GPT-4o-mini 模型
        
        # 自动从环境变量读取API密钥（如果没有直接传入）
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
        
        # 尝试初始化 OpenAI 客户端
        if api_key and OPENAI_AVAILABLE:
            try:
                self.client = OpenAI(api_key=api_key)
                self.use_gpt = True
                print(f"✓ Agent B (评估AI) 初始化成功，使用模型: {self.ai_model}")
            except Exception as e:
                print(f"⚠ 初始化Agent B OpenAI客户端失败: {type(e).__name__}: {e}")
                print("将使用规则基础的回退模式")
                self.use_gpt = False
                self.client = None
        else:
            if not api_key:
                print("⚠ 未提供OpenAI API密钥，Agent B将使用规则基础的回退模式")
            if not OPENAI_AVAILABLE:
                print("⚠ OpenAI库未安装，Agent B将使用规则基础的回退模式")
    
    def analyze(self, conversation_summary: str, date: Optional[str] = None) -> Dict:
        """
        分析用户的心理状态并返回JSON格式报告
        Args:
            conversation_summary: Agent A提供的会话摘要或用户故事
            date: 分析日期（YYYY-MM-DD格式）
        Returns:
            包含完整分析结果的字典（符合CBT Daily Analysis JSON Schema）
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        print("\n" + "="*80, flush=True)
        print(f"🔍 Agent B 开始评估分析 - {date}", flush=True)
        print("="*80, flush=True)
        print(f"📝 用户输入内容:\n{conversation_summary}\n", flush=True)
        
        # 使用 GPT 进行分析
        if self.use_gpt and self.client:
            analysis_result = self._analyze_with_gpt(conversation_summary, date)
        else:
            analysis_result = self._analyze_fallback(conversation_summary, date)
        
        # 记录评估历史
        assessment_record = {
            "timestamp": datetime.now().isoformat(),
            "date": date,
            "input": conversation_summary,
            "assessment": analysis_result
        }
        self.assessment_history.append(assessment_record)
        
        # 打印评估结构
        self._print_assessment_result(analysis_result)
        
        return analysis_result
    
    def _analyze_with_gpt(self, conversation_summary: str, date: str) -> Dict:
        """
        使用 GPT 进行心理状态分析
        返回符合 CBT Daily Analysis JSON Schema 的格式
        """
        try:
            # 构建分析提示
            analysis_prompt = f"""请分析以下用户会话内容，提取CBT结构化信息。

用户会话内容：
{conversation_summary}

请按照要求提取信息并输出JSON格式的分析结果。如果某些信息在用户内容中没有提到，请使用空字符串或空数组。"""
            
            messages = [
                {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": analysis_prompt}
            ]
            
            # 调用 OpenAI API
            response = self.client.chat.completions.create(
                model=self.ai_model,
                messages=messages,
                response_format={"type": "json_object"}  # 强制JSON输出
            )
            
            # 解析JSON响应
            response_text = response.choices[0].message.content.strip()
            
            # 尝试解析JSON
            try:
                analysis_data = json.loads(response_text)
            except json.JSONDecodeError:
                # 如果响应不是纯JSON，尝试提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    analysis_data = json.loads(json_match.group())
                else:
                    raise ValueError("无法从GPT响应中提取JSON")
            
            # 确保日期格式正确
            if "date" not in analysis_data or not analysis_data["date"]:
                analysis_data["date"] = date
            
            # 验证和规范化数据结构
            result = {
                "date": analysis_data.get("date", date),
                "presenting_problem": analysis_data.get("presenting_problem", ""),
                "situation_description": {
                    "when": analysis_data.get("situation_description", {}).get("when", ""),
                    "where": analysis_data.get("situation_description", {}).get("where", ""),
                    "who": analysis_data.get("situation_description", {}).get("who", ""),
                    "what_happened": analysis_data.get("situation_description", {}).get("what_happened", "")
                },
                "emotions": analysis_data.get("emotions", []),
                "physical_reactions": analysis_data.get("physical_reactions", []),
                "automatic_thoughts": analysis_data.get("automatic_thoughts", []),
                "behavior_reactions": analysis_data.get("behavior_reactions", []),
                "consequences": analysis_data.get("consequences", ""),
                "desired_change": analysis_data.get("desired_change", ""),
                "additional_notes": analysis_data.get("additional_notes", ""),
                "cognitive_distortions": analysis_data.get("cognitive_distortions", []),
                "clinical_scores": {
                    "anxiety_0_10": int(analysis_data.get("clinical_scores", {}).get("anxiety_0_10", 0)),
                    "depression_0_10": int(analysis_data.get("clinical_scores", {}).get("depression_0_10", 0)),
                    "stress_0_10": int(analysis_data.get("clinical_scores", {}).get("stress_0_10", 0)),
                    "rumination_0_10": int(analysis_data.get("clinical_scores", {}).get("rumination_0_10", 0)),
                    "avoidance_0_10": int(analysis_data.get("clinical_scores", {}).get("avoidance_0_10", 0)),
                    "self_blame_0_10": int(analysis_data.get("clinical_scores", {}).get("self_blame_0_10", 0))
                },
                "risk_assessment": {
                    "self_harm_risk_0_3": int(analysis_data.get("risk_assessment", {}).get("self_harm_risk_0_3", 0)),
                    "crisis_flag": bool(analysis_data.get("risk_assessment", {}).get("crisis_flag", False))
                },
                "profile_update": {
                    "trend_notes": analysis_data.get("profile_update", {}).get("trend_notes", ""),
                    "suggestions_to_therapist": analysis_data.get("profile_update", {}).get("suggestions_to_therapist", "")
                }
            }
            
            # 确保 emotions 数组中的每个元素都有正确的格式
            normalized_emotions = []
            for emotion in result["emotions"]:
                if isinstance(emotion, dict):
                    normalized_emotions.append({
                        "type": emotion.get("type", ""),
                        "intensity_0_100": int(emotion.get("intensity_0_100", 0))
                    })
            result["emotions"] = normalized_emotions
            
            # 确保 cognitive_distortions 是列表
            if not isinstance(result["cognitive_distortions"], list):
                result["cognitive_distortions"] = []
            
            return result
            
        except Exception as e:
            print(f"⚠ GPT分析失败: {type(e).__name__}: {e}")
            print("使用回退模式进行分析")
            import traceback
            traceback.print_exc()
            return self._analyze_fallback(conversation_summary, date)
    
    def _analyze_fallback(self, conversation_summary: str, date: str) -> Dict:
        """
        回退模式：使用规则基础的分析方法
        当GPT不可用时使用
        返回符合 CBT Daily Analysis JSON Schema 的格式
        """
        import re
        
        text_lower = conversation_summary.lower()
        
        # 提取主要问题
        presenting_problem = ""
        if "问题" in conversation_summary or "困扰" in conversation_summary or "烦恼" in conversation_summary:
            # 尝试提取问题描述
            problem_patterns = [
                r"今天(.*?)(问题|困扰|烦恼|事情)",
                r"我(.*?)(问题|困扰|烦恼)",
                r"觉得(.*?)(问题|困扰|烦恼)"
            ]
            for pattern in problem_patterns:
                match = re.search(pattern, conversation_summary)
                if match:
                    presenting_problem = match.group(1).strip()
                    break
        if not presenting_problem:
            presenting_problem = conversation_summary[:100]  # 使用前100个字符作为问题描述
        
        # 提取情境信息
        when_match = re.search(r"(今天|昨天|前天|早上|下午|晚上|刚才|之前|(\d+月\d+日)|(\d+点))", conversation_summary)
        when = when_match.group(0) if when_match else ""
        
        where_match = re.search(r"(在|到|去)(.*?)(家|公司|学校|医院|公园|办公室|地方)", conversation_summary)
        where = where_match.group(2) + where_match.group(3) if where_match else ""
        
        who_match = re.search(r"(和|与|跟)(.*?)(一起|见面|说话|聊天)", conversation_summary)
        who = who_match.group(2) if who_match else ""
        
        what_happened = conversation_summary[:200]  # 使用前200个字符作为事件描述
        
        # 分析情绪状态
        emotion_keywords = {
            "焦虑": ["焦虑", "担心", "紧张", "不安", "害怕", "恐惧"],
            "抑郁": ["抑郁", "沮丧", "低落", "绝望", "无助", "悲伤"],
            "愤怒": ["愤怒", "生气", "恼火", "烦躁", "不满"],
            "压力": ["压力", "累", "疲惫", "负担", "压力大"],
            "平静": ["平静", "放松", "还好", "一般", "正常"]
        }
        
        emotions = []
        for emotion_type, keywords in emotion_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > 0:
                # 提取强度
                intensity_match = re.search(r'(\d+)[分个]?[的]?(强度|程度|感觉)', conversation_summary)
                if intensity_match:
                    intensity = min(100, max(0, int(intensity_match.group(1)) * 10))
                else:
                    intensity = min(100, count * 20)  # 根据关键词数量估算
                
                emotions.append({
                    "type": emotion_type,
                    "intensity_0_100": intensity
                })
        
        if not emotions:
            emotions.append({
                "type": "平静",
                "intensity_0_100": 30
            })
        
        # 提取身体反应
        physical_keywords = ["心跳", "头痛", "紧张", "出汗", "发抖", "胸闷", "胃痛", "失眠", "疲劳"]
        physical_reactions = [kw for kw in physical_keywords if kw in text_lower]
        
        # 提取自动思维
        thought_patterns = [
            r"我想(.*?)[。，]",
            r"我觉得(.*?)[。，]",
            r"我认为(.*?)[。，]",
            r"我以为(.*?)[。，]"
        ]
        automatic_thoughts = []
        for pattern in thought_patterns:
            matches = re.findall(pattern, conversation_summary)
            automatic_thoughts.extend(matches[:3])  # 最多3个
        
        # 提取行为反应
        behavior_keywords = {
            "回避": ["避免", "不想", "躲开", "逃避"],
            "拖延": ["拖延", "推迟", "不想做"],
            "过度工作": ["一直工作", "停不下来", "必须完成"],
            "社交退缩": ["不想见人", "不想说话", "一个人"],
            "哭泣": ["哭", "流泪"],
            "争吵": ["吵架", "争论", "争执"]
        }
        behavior_reactions = []
        for behavior, keywords in behavior_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                behavior_reactions.append(behavior)
        
        # 提取后果
        consequences = ""
        consequence_patterns = [
            r"结果(.*?)[。，]",
            r"导致(.*?)[。，]",
            r"所以(.*?)[。，]",
            r"后来(.*?)[。，]"
        ]
        for pattern in consequence_patterns:
            match = re.search(pattern, conversation_summary)
            if match:
                consequences = match.group(1).strip()
                break
        
        # 提取期望改变
        desired_change = ""
        change_patterns = [
            r"希望(.*?)[。，]",
            r"想要(.*?)[。，]",
            r"希望(.*?)[。，]",
            r"改善(.*?)[。，]"
        ]
        for pattern in change_patterns:
            match = re.search(pattern, conversation_summary)
            if match:
                desired_change = match.group(1).strip()
                break
        
        # 识别认知扭曲
        cognitive_distortions = []
        cognitive_keywords = {
            "all-or-nothing thinking": ["总是", "从不", "完全", "绝对", "一定", "永远"],
            "catastrophizing": ["完蛋了", "太糟糕了", "最坏的情况", "无法承受", "灾难"],
            "overgeneralization": ["总是这样", "从来都", "每次", "所有人", "从来"],
            "emotional reasoning": ["感觉", "觉得", "应该是", "感觉就是"],
            "mind reading": ["他一定觉得", "他们肯定", "别人认为", "他肯定想"],
            "fortune telling": ["肯定会", "一定会", "注定", "未来肯定"],
            "should statements": ["应该", "必须", "一定得", "应该要"],
            "personalization": ["都是因为我", "我的错", "怪我", "因为我"],
            "self-blame": ["我不好", "我不行", "我错了", "我的问题"],
            "labeling": ["我是个", "他就是个", "这就是", "我就是"],
            "discounting the positive": ["不算什么", "只是运气", "不值得一提", "没什么"]
        }
        for distortion, keywords in cognitive_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                cognitive_distortions.append(distortion)
        
        # 计算扩展的临床评分
        anxiety_keywords = ["焦虑", "担心", "紧张", "不安", "害怕", "恐惧", "恐慌"]
        anxiety_score = min(10, sum(1 for kw in anxiety_keywords if kw in text_lower) * 2)
        
        depression_keywords = ["抑郁", "沮丧", "低落", "绝望", "无助", "悲伤", "想哭", "没意思"]
        depression_score = min(10, sum(1 for kw in depression_keywords if kw in text_lower) * 2)
        
        stress_keywords = ["压力", "累", "疲惫", "负担", "压力大", "受不了", "崩溃"]
        stress_score = min(10, sum(1 for kw in stress_keywords if kw in text_lower) * 2)
        
        rumination_keywords = ["反复想", "一直想", "停不下来", "想不通", "纠结", "反复思考"]
        rumination_score = min(10, sum(1 for kw in rumination_keywords if kw in text_lower) * 2)
        
        avoidance_score = min(10, sum(1 for beh in behavior_reactions if "回避" in beh or "逃避" in beh) * 3)
        
        self_blame_keywords = ["我的错", "怪我", "我不行", "我不好", "我的问题", "都怪我"]
        self_blame_score = min(10, sum(1 for kw in self_blame_keywords if kw in text_lower) * 2)
        
        # 风险评估
        high_risk_keywords = ["不想活了", "死了算了", "自杀", "自伤", "伤害自己", "结束生命"]
        medium_risk_keywords = ["没意思", "没希望", "绝望", "看不到未来", "活着没意义"]
        
        risk_score = 0
        crisis_flag = False
        
        if any(kw in text_lower for kw in high_risk_keywords):
            risk_score = 3
            crisis_flag = True
        elif any(kw in text_lower for kw in medium_risk_keywords):
            risk_score = 2
        elif "难过" in text_lower or "痛苦" in text_lower:
            risk_score = 1
        
        # 生成趋势和建议
        trend_notes = []
        if anxiety_score >= 7:
            trend_notes.append("焦虑水平较高，需要关注")
        if depression_score >= 7:
            trend_notes.append("抑郁情绪明显，建议专业评估")
        if stress_score >= 7:
            trend_notes.append("压力水平较高，需要减压策略")
        if rumination_score >= 7:
            trend_notes.append("反刍思维明显，需要认知干预")
        
        suggestions = []
        if anxiety_score >= 7:
            suggestions.append("考虑教授放松技巧和认知重构")
        if depression_score >= 7:
            suggestions.append("评估是否需要药物治疗或转介")
        if stress_score >= 7:
            suggestions.append("建议压力管理和时间管理策略")
        if cognitive_distortions:
            suggestions.append(f"识别到认知扭曲: {', '.join(cognitive_distortions[:3])}，建议进行认知重构")
        
        result = {
            "date": date,
            "presenting_problem": presenting_problem,
            "situation_description": {
                "when": when,
                "where": where,
                "who": who,
                "what_happened": what_happened
            },
            "emotions": emotions,
            "physical_reactions": physical_reactions,
            "automatic_thoughts": automatic_thoughts[:5],  # 最多5个
            "behavior_reactions": behavior_reactions,
            "consequences": consequences,
            "desired_change": desired_change,
            "additional_notes": "",
            "cognitive_distortions": list(set(cognitive_distortions)),
            "clinical_scores": {
                "anxiety_0_10": min(10, anxiety_score),
                "depression_0_10": min(10, depression_score),
                "stress_0_10": min(10, stress_score),
                "rumination_0_10": min(10, rumination_score),
                "avoidance_0_10": min(10, avoidance_score),
                "self_blame_0_10": min(10, self_blame_score)
            },
            "risk_assessment": {
                "self_harm_risk_0_3": risk_score,
                "crisis_flag": crisis_flag
            },
            "profile_update": {
                "trend_notes": "；".join(trend_notes) if trend_notes else "整体状态稳定",
                "suggestions_to_therapist": "；".join(suggestions) if suggestions else "继续当前治疗方案"
            }
        }
        
        return result
    
    def _print_assessment_result(self, result: Dict):
        """
        打印评估结果结构（符合 CBT Daily Analysis JSON Schema）
        """
        print("\n" + "="*80, flush=True)
        print("📊 Agent B 评估结果", flush=True)
        print("="*80, flush=True)
        
        # 日期和主要问题
        print(f"\n【日期】{result.get('date', '未知')}")
        print(f"\n【主要问题】")
        print(f"  {result.get('presenting_problem', '未提及')}")
        
        # 情境描述
        print("\n【情境描述】")
        situation = result.get("situation_description", {})
        print(f"  时间: {situation.get('when', '未提及')}")
        print(f"  地点: {situation.get('where', '未提及')}")
        print(f"  人物: {situation.get('who', '未提及')}")
        print(f"  事件: {situation.get('what_happened', '未提及')}")
        
        # 情绪
        print("\n【情绪】")
        emotions = result.get("emotions", [])
        if emotions:
            for emotion in emotions:
                print(f"  - {emotion.get('type', '未知')}: {emotion.get('intensity_0_100', 0)}/100")
        else:
            print("  未提及")
        
        # 身体反应
        print("\n【身体反应】")
        physical = result.get("physical_reactions", [])
        if physical:
            for reaction in physical:
                print(f"  - {reaction}")
        else:
            print("  未提及")
        
        # 自动思维
        print("\n【自动思维】")
        thoughts = result.get("automatic_thoughts", [])
        if thoughts:
            for thought in thoughts:
                print(f"  - {thought}")
        else:
            print("  未提及")
        
        # 行为反应
        print("\n【行为反应】", flush=True)
        behaviors = result.get("behavior_reactions", [])
        if behaviors:
            for behavior in behaviors:
                print(f"  - {behavior}", flush=True)
        else:
            print("  未提及", flush=True)
        
        # 后果
        print("\n【后果】", flush=True)
        consequences = result.get("consequences", "")
        print(f"  {consequences if consequences else '未提及'}", flush=True)
        
        # 期望改变
        print("\n【期望改变】", flush=True)
        desired_change = result.get("desired_change", "")
        print(f"  {desired_change if desired_change else '未提及'}", flush=True)
        
        # 附加备注
        additional_notes = result.get("additional_notes", "")
        if additional_notes:
            print("\n【附加备注】", flush=True)
            print(f"  {additional_notes}", flush=True)
        
        # 认知扭曲
        print("\n【认知扭曲】", flush=True)
        distortions = result.get("cognitive_distortions", [])
        if distortions:
            for distortion in distortions:
                print(f"  - {distortion}", flush=True)
        else:
            print("  未检测到", flush=True)
        
        # 临床评分
        print("\n【临床评分】", flush=True)
        scores = result.get("clinical_scores", {})
        print(f"  焦虑: {scores.get('anxiety_0_10', 0)}/10", flush=True)
        print(f"  抑郁: {scores.get('depression_0_10', 0)}/10", flush=True)
        print(f"  压力: {scores.get('stress_0_10', 0)}/10", flush=True)
        print(f"  反刍思维: {scores.get('rumination_0_10', 0)}/10", flush=True)
        print(f"  回避: {scores.get('avoidance_0_10', 0)}/10", flush=True)
        print(f"  自责: {scores.get('self_blame_0_10', 0)}/10", flush=True)
        
        # 风险评估
        print("\n【风险评估】", flush=True)
        risk = result.get("risk_assessment", {})
        risk_level = ["无", "低", "中", "高"][risk.get('self_harm_risk_0_3', 0)]
        print(f"  自伤风险: {risk_level} ({risk.get('self_harm_risk_0_3', 0)}/3)", flush=True)
        print(f"  危机标志: {'是 ⚠️' if risk.get('crisis_flag', False) else '否'}", flush=True)
        
        # 档案更新
        print("\n【档案更新】", flush=True)
        profile = result.get("profile_update", {})
        print(f"  趋势备注: {profile.get('trend_notes', '无')}", flush=True)
        print(f"  治疗建议: {profile.get('suggestions_to_therapist', '无')}", flush=True)
        
        # 完整JSON
        print("\n" + "="*80, flush=True)
        print("📋 完整评估JSON (CBT Daily Analysis Schema):", flush=True)
        print("="*80, flush=True)
        print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
        print("="*80 + "\n", flush=True)
    
    def get_assessment_history(self) -> List[Dict]:
        """获取所有评估历史记录"""
        return self.assessment_history
    
    def get_latest_assessment(self) -> Optional[Dict]:
        """获取最新的评估结果"""
        if self.assessment_history:
            return self.assessment_history[-1]
        return None
    
    def to_json(self, analysis_result: Dict) -> str:
        """将分析结果转换为JSON字符串"""
        return json.dumps(analysis_result, ensure_ascii=False, indent=2)
