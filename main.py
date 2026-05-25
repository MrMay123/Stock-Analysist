from agent import ReActAgent
from config import FEED_PRESETS
from llm import GeminiLLM
from tools import ToolExecutor, fetch_rss


def build_agent() -> tuple[ReActAgent, str]:
    """组装 ReAct Agent：LLM + 工具执行器 + 工具注册"""
    llm = GeminiLLM(model="gemini-2.0-flash")

    executor = ToolExecutor()
    executor.register(
        name="fetch_rss",
        func=fetch_rss,
        description="fetch_rss[RSS_URL] — 获取指定 RSS 源的最新新闻文章列表",
    )

    agent = ReActAgent(llm_client=llm, tool_executor=executor, max_steps=8)

    preset_list = "\n".join(f"  {i+1}. {name}" for i, name in enumerate(FEED_PRESETS))
    return agent, preset_list


def get_feeds_from_user(preset_list: str) -> list[str]:
    """让用户选择预设 RSS 源或输入自定义源"""
    preset_names = list(FEED_PRESETS.keys())
    print(f"\n📡 选择新闻源：")
    print(preset_list)
    print(f"  {len(preset_names)+1}. 自定义 RSS URL")

    choice = input("\n请选择 (输入数字): ").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(preset_names):
            selected = preset_names[idx]
            feeds = FEED_PRESETS[selected]
            print(f"✅ 已选择「{selected}」，包含 {len(feeds)} 个 RSS 源")
            return feeds
    except ValueError:
        pass

    # 自定义输入
    print("请每行输入一个 RSS URL（输入空行结束）：")
    feeds = []
    while True:
        line = input().strip()
        if not line:
            break
        feeds.append(line)
    return feeds


def format_question(topic: str, feeds: list[str]) -> str:
    """将用户输入转换为 agent 的问题描述"""
    feed_list = "\n".join(f"- {url}" for url in feeds)
    return (
        f"请从以下 RSS 源获取关于「{topic}」的最新新闻，"
        f"筛选相关文章并生成中文摘要（含标题、摘要、链接、相关度评分）：\n{feed_list}"
    )


def main():
    print("=" * 60)
    print("   AI 新闻摘要 Agent（ReAct 范式）")
    print("   框架参考: hello-agents 第四章 4.2.3")
    print("=" * 60)

    agent, preset_list = build_agent()

    while True:
        topic = input("\n🔍 请输入新闻主题（或 q 退出）: ").strip()
        if topic.lower() in ("q", "quit", "exit"):
            print("再见！")
            break
        if not topic:
            continue

        feeds = get_feeds_from_user(preset_list)
        if not feeds:
            print("未选择任何 RSS 源，请重试。")
            continue

        question = format_question(topic, feeds)
        print(f"\n🚀 启动 ReAct Agent...")
        print(f"   主题: {topic}")
        print(f"   RSS 源: {len(feeds)} 个")

        result = agent.run(question)

        print("\n" + "=" * 60)
        print("📰 新闻摘要结果")
        print("=" * 60)
        if result:
            print(result)
        else:
            print("未能生成摘要，请检查网络或 API Key。")
        print("=" * 60)


if __name__ == "__main__":
    main()
