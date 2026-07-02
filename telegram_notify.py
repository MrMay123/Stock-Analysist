"""Minimal Telegram Bot API sender for scheduled reports."""
import os
import time

import requests

TELEGRAM_API_BASE = "https://api.telegram.org"
MAX_MESSAGE_LENGTH = 4096


def send_telegram_message(text: str, *, timeout: float = 10.0) -> bool:
    """Send `text` to the configured Telegram chat, splitting on the 4096-char limit."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("[telegram_notify] TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID 未配置，跳过推送")
        return False

    api_url = f"{TELEGRAM_API_BASE}/bot{bot_token}/sendMessage"
    chunks = [
        text[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(text), MAX_MESSAGE_LENGTH)
    ] or [text]

    all_ok = True
    for index, chunk in enumerate(chunks, start=1):
        payload = {"chat_id": chat_id, "text": chunk, "disable_web_page_preview": True}
        try:
            response = requests.post(api_url, json=payload, timeout=timeout)
        except requests.exceptions.RequestException as e:
            print(f"[telegram_notify] 第 {index}/{len(chunks)} 段请求异常: {e}")
            all_ok = False
        else:
            if not (response.status_code == 200 and response.json().get("ok")):
                print(
                    f"[telegram_notify] 第 {index}/{len(chunks)} 段发送失败: "
                    f"HTTP {response.status_code} {response.text}"
                )
                all_ok = False

        if index < len(chunks):
            time.sleep(1)

    return all_ok
