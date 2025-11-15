#!/usr/bin/env python
"""
AI 功能测试脚本
测试 OpenAI 或 Anthropic API 是否正确配置
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def test_openai():
    """测试 OpenAI 配置"""
    print("\n" + "="*60)
    print("🧪 OpenAI 配置测试")
    print("="*60)

    # 检查库
    try:
        from openai import OpenAI
        print("✓ OpenAI 库已安装")
    except ImportError:
        print("✗ OpenAI 库未安装")
        print("  安装命令: pip install openai")
        return False

    # 检查 API 密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("✗ OPENAI_API_KEY 环境变量未设置")
        print("  请设置: export OPENAI_API_KEY='your-key-here'")
        return False

    print(f"✓ API Key 已找到: {api_key[:10]}...{api_key[-4:]}")

    # 测试连接
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        print("⏳ 测试 API 连接...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是一个有帮助的助手"},
                {"role": "user", "content": "你好，说个简短的问候"}
            ],
            max_tokens=50,
        )

        reply = response.choices[0].message.content
        print(f"✓ API 连接成功!")
        print(f"  模型回复: {reply[:100]}...")
        return True

    except Exception as e:
        print(f"✗ API 连接失败: {type(e).__name__}: {e}")
        return False


def test_anthropic():
    """测试 Anthropic 配置"""
    print("\n" + "="*60)
    print("🧪 Anthropic (Claude) 配置测试")
    print("="*60)

    # 检查库
    try:
        from anthropic import Anthropic
        print("✓ Anthropic 库已安装")
    except ImportError:
        print("✗ Anthropic 库未安装")
        print("  安装命令: pip install anthropic")
        return False

    # 检查 API 密钥
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("✗ ANTHROPIC_API_KEY 环境变量未设置")
        print("  请设置: export ANTHROPIC_API_KEY='your-key-here'")
        return False

    print(f"✓ API Key 已找到: {api_key[:10]}...{api_key[-4:]}")

    # 测试连接
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)

        print("⏳ 测试 API 连接...")
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            messages=[
                {"role": "user", "content": "你好，说个简短的问候"}
            ]
        )

        reply = response.content[0].text
        print(f"✓ API 连接成功!")
        print(f"  模型回复: {reply[:100]}...")
        return True

    except Exception as e:
        print(f"✗ API 连接失败: {type(e).__name__}: {e}")
        return False


def test_agent_conversation():
    """测试 AgentConversation 类"""
    print("\n" + "="*60)
    print("🧪 AgentConversation 初始化测试")
    print("="*60)

    try:
        from backend.agents.agent_conversation import AgentConversation

        print("✓ AgentConversation 类已导入")

        # 尝试使用 OpenAI
        print("\n📝 测试 OpenAI 模式...")
        try:
            agent_openai = AgentConversation(model_type="openai")
            if agent_openai.use_ai:
                print(f"✓ OpenAI Agent 初始化成功，模型: {agent_openai.ai_model}")

                # 测试会话
                greeting = agent_openai.start_session("test_user")
                print(f"  欢迎语: {greeting[:50]}...")
            else:
                print("⚠ OpenAI Agent 未启用（API密钥可能缺失）")
        except Exception as e:
            print(f"✗ OpenAI Agent 初始化失败: {e}")

        # 尝试使用 Anthropic
        print("\n📝 测试 Anthropic 模式...")
        try:
            agent_anthropic = AgentConversation(model_type="anthropic")
            if agent_anthropic.use_ai:
                print(f"✓ Anthropic Agent 初始化成功，模型: {agent_anthropic.ai_model}")

                # 测试会话
                greeting = agent_anthropic.start_session("test_user")
                print(f"  欢迎语: {greeting[:50]}...")
            else:
                print("⚠ Anthropic Agent 未启用（API密钥可能缺失）")
        except Exception as e:
            print(f"✗ Anthropic Agent 初始化失败: {e}")

        return True

    except ImportError as e:
        print(f"✗ 无法导入 AgentConversation: {e}")
        return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


def test_full_conversation():
    """测试完整对话流程"""
    print("\n" + "="*60)
    print("🧪 完整对话流程测试")
    print("="*60)

    try:
        from backend.agents.agent_conversation import AgentConversation

        # 选择模型
        model_type = "openai" if os.getenv("OPENAI_API_KEY") else "anthropic"
        if not os.getenv(f"{model_type.upper()}_API_KEY"):
            print("✗ 没有可用的 API 密钥")
            return False

        print(f"📝 使用模型: {model_type}")

        agent = AgentConversation(model_type=model_type)

        if not agent.use_ai:
            print("⚠ AI 未启用，使用回退模式")
            return False

        # 开始会话
        print("\n开始模拟对话...")
        greeting = agent.start_session("test_user")
        print(f"助手: {greeting[:100]}...")

        # 模拟用户输入
        test_inputs = [
            "我今天感到很焦虑",
            "大概 8 分吧",
            "工作项目的截止日期",
            "我觉得我无法完成它",
            "我开始回避任何与项目相关的任务",
        ]

        for user_input in test_inputs:
            print(f"\n用户: {user_input}")
            response = agent.process_user_input(user_input)
            print(f"助手: {response[:100]}...")

            if agent.is_session_ended():
                print("\n✓ 会话已结束")
                break

        # 强制结束
        if not agent.is_session_ended():
            print("\n用户: 完成")
            closing = agent.process_user_input("完成")
            print(f"助手: {closing[:100]}...")

        print("\n✓ 完整对话流程测试成功!")
        return True

    except Exception as e:
        print(f"✗ 对话测试失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("🤖 CBT Therapy Assistant - AI 功能测试")
    print("="*60)

    results = {}

    # 1. 测试 OpenAI
    results["OpenAI"] = test_openai()

    # 2. 测试 Anthropic
    results["Anthropic"] = test_anthropic()

    # 3. 测试 AgentConversation
    results["AgentConversation"] = test_agent_conversation()

    # 4. 测试完整对话（可选，需要可用的API）
    if results["OpenAI"] or results["Anthropic"]:
        print("\n")
        input("按 Enter 继续测试完整对话流程（或 Ctrl+C 跳过）...")
        results["Full Conversation"] = test_full_conversation()

    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)

    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")

    print("\n" + "="*60)

    if any(results.values()):
        print("✓ 至少有一个 AI 服务配置成功！")
        print("\n您可以现在运行:")
        print("  python -m backend.main")
        print("  然后访问 http://localhost:8000")
    else:
        print("✗ 没有 AI 服务配置成功")
        print("\n请检查:")
        print("  1. 是否已安装 openai 或 anthropic 库")
        print("  2. 是否已设置 API 密钥环境变量")
        print("  3. 是否已重启应用（修改环境变量后需重启）")

    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹ 测试被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ 测试发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
