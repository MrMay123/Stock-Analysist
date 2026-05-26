REACT_PROMPT_TEMPLATE = """
请注意，你是一个专业的财经新闻分析智能助手，能够获取新闻并分析相关投资机会。

可用工具如下:
{tools}

请严格按照以下格式进行回应:

Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动，必须是以下格式之一:
- `fetch_rss[RSS_URL]`: 获取指定 RSS 源的最新新闻
- `get_stock_info[股票代码]`: 获取指定股票的实时行情（如 get_stock_info[AAPL]）
- `Finish[最终报告]`: 当你已收集足够信息，输出完整的分析报告

规则:
- 每次只调用一个工具
- 先逐一获取所有 RSS 源的新闻
- 从新闻中识别出被频繁提及或受影响的公司/股票代码
- 对 2-4 支最相关的股票调用 get_stock_info 获取实时数据
- 最后用 Finish 输出结构化报告

Finish 的报告必须包含以下三个部分（用中文输出）：

📰 相关新闻（只保留相关度 >= 6 的文章，最多 8 条）
每条格式：标题 | 2-3句摘要 | 链接 | 相关度(1-10)

📊 值得关注的股票（3-5支）
每条格式：股票代码 + 公司名 | 当前价格 | 涨跌幅 | 关注理由（结合新闻分析）

🔍 关键看点（3-5条）
基于新闻归纳出值得投资者关注的市场动态、风险或机会

现在，请开始解决以下问题:
Question: {question}
History:
{history}
"""

FEED_PRESETS = {
    "财经（综合）": [
        "https://finance.yahoo.com/news/rssindex",
        "https://feeds.reuters.com/reuters/businessNews",
        "https://feeds.marketwatch.com/marketwatch/topstories/",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    ],
    "财经（美股重点）": [
        "https://finance.yahoo.com/news/rssindex",
        "https://feeds.marketwatch.com/marketwatch/topstories/",
        "https://feeds.bloomberg.com/markets/news.rss",
        "https://www.cnbc.com/id/10000664/device/rss/rss.html",
    ],
    "科技": [
        "https://feeds.feedburner.com/TechCrunch",
        "https://www.wired.com/feed/rss",
        "https://feeds.reuters.com/reuters/technologyNews",
    ],
    "AI": [
        "https://feeds.feedburner.com/TechCrunch",
        "https://www.wired.com/feed/tag/artificial-intelligence/rss",
        "https://feeds.reuters.com/reuters/technologyNews",
    ],
    "全球头条": [
        "https://rss.cnn.com/rss/edition.rss",
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://feeds.reuters.com/reuters/topNews",
    ],
}
