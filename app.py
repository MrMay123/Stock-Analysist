import threading
import uuid
from flask import Flask, jsonify, render_template, request

from agent import ReActAgent
from config import FEED_PRESETS
from llm import DeepSeekLLM
from tools import ToolExecutor, fetch_rss, get_stock_info

app = Flask(__name__)

# In-memory job store: job_id -> {"status": ..., "result": ...}
jobs: dict[str, dict] = {}
jobs_lock = threading.Lock()


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


def run_agent_job(job_id: str, feeds: list[str]) -> None:
    with jobs_lock:
        jobs[job_id]["status"] = "running"

    feed_list = "\n".join(f"- {url}" for url in feeds)
    question = (
        f"请从以下 RSS 源获取最新财经新闻，"
        f"分析相关股票投资机会，并给出值得关注的市场看点：\n{feed_list}"
    )

    try:
        agent = build_agent()
        result = agent.run(question)
        with jobs_lock:
            jobs[job_id]["status"] = "done"
            jobs[job_id]["result"] = result or "未能生成报告，请检查网络或 API Key。"
    except Exception as e:
        with jobs_lock:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["result"] = f"分析出错: {e}"


@app.route("/")
def index():
    presets = list(FEED_PRESETS.keys())
    return render_template("index.html", presets=presets)


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(force=True)
    preset_name = data.get("preset")
    custom_urls = data.get("custom_urls", [])

    if preset_name and preset_name in FEED_PRESETS:
        feeds = FEED_PRESETS[preset_name]
    elif custom_urls:
        feeds = [u.strip() for u in custom_urls if u.strip()]
    else:
        return jsonify({"error": "请选择一个新闻源或输入自定义 URL"}), 400

    job_id = str(uuid.uuid4())
    with jobs_lock:
        jobs[job_id] = {"status": "pending", "result": None}

    thread = threading.Thread(target=run_agent_job, args=(job_id, feeds), daemon=True)
    thread.start()

    return jsonify({"job_id": job_id})


@app.route("/status/<job_id>")
def status(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "找不到该任务"}), 404
    return jsonify(job)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
