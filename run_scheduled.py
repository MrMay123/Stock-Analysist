"""Non-interactive entrypoint for scheduled runs (GitHub Actions).

Combines a fixed set of RSS presets, runs the ReAct agent once, and pushes
the resulting report to Telegram. A Telegram push failure is logged but does
not fail the job, since the analysis itself already succeeded by that point.
"""
import sys

from config import FEED_PRESETS
from main import build_agent, format_question
from telegram_notify import send_telegram_message

PRESET_NAMES = ["财经（综合）", "财经（美股重点）"]


def collect_feeds() -> list[str]:
    """Merge the configured presets into a deduplicated feed list, preserving order."""
    seen = set()
    feeds = []
    for name in PRESET_NAMES:
        for url in FEED_PRESETS[name]:
            if url not in seen:
                seen.add(url)
                feeds.append(url)
    return feeds


def main() -> int:
    feeds = collect_feeds()
    print(f"抓取 {len(feeds)} 个 RSS 源，来自预设: {', '.join(PRESET_NAMES)}")

    agent, _ = build_agent()
    question = format_question(feeds)
    result = agent.run(question)

    if not result:
        print("未能生成报告，请检查网络或 API Key。", file=sys.stderr)
        return 1

    print(result)

    if send_telegram_message(result):
        print("Telegram 推送成功")
    else:
        print("Telegram 推送失败，请查看上方日志", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
