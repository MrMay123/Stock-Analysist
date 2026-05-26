import asyncio
import logging
import os

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from agent import ReActAgent
from config import FEED_PRESETS
from llm import DeepSeekLLM
from tools import ToolExecutor, fetch_rss, get_stock_info

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def build_agent() -> ReActAgent:
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
    return ReActAgent(llm_client=llm, tool_executor=executor, max_steps=15)


def make_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(name, callback_data=name)]
        for name in FEED_PRESETS.keys()
    ]
    return InlineKeyboardMarkup(keyboard)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 *欢迎使用 AI 财经分析助手！*\n\n"
        "我会从多个财经媒体抓取最新新闻，\n"
        "分析相关股票行情，并给出市场看点。\n\n"
        "发送 /analyze 开始分析 📊",
        parse_mode="Markdown",
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📖 *使用说明*\n\n"
        "/analyze — 选择新闻源，开始分析\n"
        "/start   — 显示欢迎信息\n"
        "/help    — 显示此帮助\n\n"
        "每次分析约需 1-2 分钟，请耐心等待。",
        parse_mode="Markdown",
    )


async def cmd_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📡 请选择新闻源：",
        reply_markup=make_keyboard(),
    )


async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    selected = query.data
    feeds = FEED_PRESETS.get(selected)
    if not feeds:
        await query.edit_message_text("❌ 无效选择，请重新发送 /analyze")
        return

    await query.edit_message_text(
        f"⏳ 正在分析「{selected}」...\n\n"
        f"共 {len(feeds)} 个新闻源，预计需要 1-2 分钟，请稍候。"
    )

    feed_list = "\n".join(f"- {url}" for url in feeds)
    question = (
        f"请从以下 RSS 源获取最新财经新闻，"
        f"分析相关股票投资机会，并给出值得关注的市场看点：\n{feed_list}"
    )

    loop = asyncio.get_event_loop()
    agent = build_agent()
    result = await loop.run_in_executor(None, agent.run, question)

    if not result:
        await query.edit_message_text("❌ 分析失败，请稍后重试或检查 API 配置。")
        return

    header = f"📊 *财经分析报告 — {selected}*\n\n"
    full_text = header + result

    # Telegram 单条消息上限 4096 字符，超出则分段发送
    if len(full_text) <= 4096:
        await query.edit_message_text(full_text, parse_mode="Markdown")
    else:
        await query.edit_message_text(full_text[:4096], parse_mode="Markdown")
        remaining = full_text[4096:]
        while remaining:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=remaining[:4096],
                parse_mode="Markdown",
            )
            remaining = remaining[4096:]

    # 分析完毕后再次显示选择按钮，方便继续使用
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="继续分析？点击选择新闻源 👇",
        reply_markup=make_keyboard(),
    )


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("请在 .env 文件中设置 TELEGRAM_BOT_TOKEN")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("analyze", cmd_analyze))
    app.add_handler(CallbackQueryHandler(handle_selection))

    print("🤖 Bot 已启动，Ctrl+C 退出")
    app.run_polling()


if __name__ == "__main__":
    main()
