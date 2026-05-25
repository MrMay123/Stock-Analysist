import feedparser
from typing import Callable, Optional


def fetch_rss(url: str) -> str:
    """获取并解析 RSS feed，返回文章列表文本"""
    try:
        feed = feedparser.parse(url.strip(), request_headers={"User-Agent": "NewsAgent/1.0"})

        if not feed.entries:
            return f"[fetch_rss] 未获取到文章，请检查 URL: {url}"

        source_name = feed.feed.get("title", url)
        lines = [f"来源: {source_name}  ({len(feed.entries[:15])} 篇)"]

        for entry in feed.entries[:15]:
            title = entry.get("title", "无标题").strip()
            link = entry.get("link", "")
            published = entry.get("published", entry.get("updated", ""))
            summary = (
                entry.get("summary", entry.get("description", ""))
                .replace("<p>", "").replace("</p>", "")
                .replace("<b>", "").replace("</b>", "")
                [:200]
            )
            lines.append(f"\n标题: {title}\n链接: {link}\n时间: {published}\n摘要: {summary}")

        return "\n".join(lines)

    except Exception as e:
        return f"[fetch_rss] 错误: {e}"


class ToolExecutor:
    """工具注册与执行器（按教程4.2.3结构）"""

    def __init__(self):
        self._tools: dict[str, Callable[[str], str]] = {}
        self._descriptions: dict[str, str] = {}

    def register(self, name: str, func: Callable[[str], str], description: str) -> None:
        self._tools[name] = func
        self._descriptions[name] = description

    def getTool(self, name: str) -> Optional[Callable[[str], str]]:
        return self._tools.get(name)

    def getAvailableTools(self) -> str:
        return "\n".join(f"- {name}: {desc}" for name, desc in self._descriptions.items())
