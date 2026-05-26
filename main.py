from agent import ReActAgent
from config import FEED_PRESETS
from llm import DeepSeekLLM
from tools import ToolExecutor, fetch_rss, get_stock_info


def build_agent() -> tuple[ReActAgent, str]:
    """组装 ReAct Agent：LLM + 工具执行器 + 工具注册"""
    llm = DeepSeekLLM(model="deepseek-chat")

    executor = ToolExecutor()
    executor.register(
        name="fetch_rss",
        func=fetch_rss,
        description="fetch_rss[RSS_URL] — 获取指定 RSS 源的最新新闻文章列表",
    )
    executor.register(
        name="get_stock_info",
        func=get_stock_info,
        description="get_stock_info[股票代码] — 获取股票实时价格、涨跌幅、市值、PE等数据，如 get_stock_info[AAPL]",
    )

    agent = ReActAgent(llm_client=llm, tool_executor=executor, max_steps=15)

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


def format_question(feeds: list[str]) -> str:
    """将选定的 RSS 源转换为 agent 的问题描述"""
    feed_list = "\n".join(f"- {url}" for url in feeds)
    return (
        f"请从以下 RSS 源获取最新财经新闻，"
        f"分析相关股票投资机会，并给出值得关注的市场看点：\n{feed_list}"
    )


def main():
    print("=" * 60)
    print("   AI 财经新闻分析 Agent（ReAct 范式）")
    print("=" * 60)

    agent, preset_list = build_agent()

    while True:
        feeds = get_feeds_from_user(preset_list)
        if not feeds:
            print("未选择任何 RSS 源，请重试。")
            continue

        question = format_question(feeds)
        print(f"\n🚀 启动 ReAct Agent...")
        print(f"   RSS 源: {len(feeds)} 个")

        result = agent.run(question)

        print("\n" + "=" * 60)
        print("📊 财经分析报告")
        print("=" * 60)
        if result:
            print(result)
        else:
            print("未能生成报告，请检查网络或 API Key。")
        print("=" * 60)

        again = input("\n继续分析？(回车继续 / q 退出): ").strip()
        if again.lower() in ("q", "quit", "exit"):
            print("再见！")
            break


if __name__ == "__main__":
    main()
