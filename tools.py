import feedparser
import yfinance as yf
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


def get_stock_info(ticker: str) -> str:
    """获取股票实时行情和基本面数据"""
    try:
        symbol = ticker.strip().upper()
        stock = yf.Ticker(symbol)
        info = stock.info

        name = info.get("longName") or info.get("shortName", symbol)
        currency = info.get("currency", "USD")
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
        market_cap = info.get("marketCap")
        pe_ratio = info.get("trailingPE")
        week_high = info.get("fiftyTwoWeekHigh")
        week_low = info.get("fiftyTwoWeekLow")
        sector = info.get("sector", "N/A")
        analyst_target = info.get("targetMeanPrice")

        if not current_price:
            return f"[get_stock_info] 未能获取 {symbol} 的行情数据，请确认股票代码正确"

        change_pct = ((current_price - prev_close) / prev_close * 100) if prev_close else None
        change_str = f"{change_pct:+.2f}%" if change_pct is not None else "N/A"

        market_cap_str = f"${market_cap/1e9:.1f}B" if market_cap else "N/A"
        pe_str = f"{pe_ratio:.1f}" if pe_ratio else "N/A"
        target_str = f"{currency} {analyst_target:.2f}" if analyst_target else "N/A"
        range_str = f"{week_low} - {week_high}" if week_low and week_high else "N/A"

        return (
            f"股票: {symbol} ({name})\n"
            f"当前价格: {currency} {current_price:.2f}  涨跌幅: {change_str}\n"
            f"市值: {market_cap_str}  市盈率(PE): {pe_str}\n"
            f"52周区间: {range_str}\n"
            f"分析师目标价: {target_str}\n"
            f"所属板块: {sector}"
        )

    except Exception as e:
        return f"[get_stock_info] 错误: {e}"


class ToolExecutor:
    """工具注册与执行器"""

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
