import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class DeepSeekLLM:
    """DeepSeek LLM 客户端（兼容 OpenAI 格式）"""

    def __init__(self, model: str = "deepseek-chat"):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("请在 .env 文件中设置 DEEPSEEK_API_KEY")
        self._client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )
        self._model = model

    def think(self, messages: list[dict]) -> str | None:
        try:
            prompt = messages[-1]["content"]
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2048,
                temperature=0.2,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[LLM Error] {e}")
            return None
