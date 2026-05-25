import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


class GeminiLLM:
    """Gemini LLM 客户端（对应教程中的 HelloAgentsLLM）"""

    def __init__(self, model: str = "gemini-2.0-flash"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("请在 .env 文件中设置 GEMINI_API_KEY")
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def think(self, messages: list[dict]) -> str | None:
        """
        向 LLM 发送消息并获取回复文本。
        messages 格式: [{"role": "user", "content": "..."}]
        """
        try:
            prompt = messages[-1]["content"]
            response = self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=2048,
                ),
            )
            return response.text
        except Exception as e:
            print(f"[LLM Error] {e}")
            return None
