import re
from typing import Optional

from config import REACT_PROMPT_TEMPLATE
from llm import DeepSeekLLM
from tools import ToolExecutor


class ReActAgent:
    """
    ReAct 智能体实现（Reasoning + Acting）
    参考: datawhalechina/hello-agents 第四章 4.2.3
    循环: Thought → Action → Observation → Thought → ...
    """

    def __init__(self, llm_client: DeepSeekLLM, tool_executor: ToolExecutor, max_steps: int = 8):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history: list[str] = []

    def run(self, question: str) -> Optional[str]:
        """
        主循环：给定问题，反复执行 Thought-Action-Observation 直到 Finish。
        """
        self.history = []
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1
            print(f"\n{'='*50}")
            print(f"  第 {current_step} 步")
            print(f"{'='*50}")

            # 1. 构造 prompt
            prompt = REACT_PROMPT_TEMPLATE.format(
                tools=self.tool_executor.getAvailableTools(),
                question=question,
                history="\n".join(self.history) if self.history else "（无）",
            )

            # 2. LLM 推理
            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(messages=messages)

            if not response_text:
                print("❌ LLM 未返回有效响应，终止。")
                break

            # 3. 解析 Thought 和 Action
            thought, action = self._parse_output(response_text)

            if thought:
                print(f"🤔 Thought: {thought}")

            if not action:
                print("⚠️  未解析到 Action，终止。")
                break

            # 4. 执行 Action
            if action.startswith("Finish"):
                finish_match = re.match(r"Finish\[(.*)\]", action, re.DOTALL)
                if finish_match:
                    final_answer = finish_match.group(1).strip()
                    print(f"\n✅ 完成！\n")
                    return final_answer
                else:
                    print("⚠️  Finish 格式解析失败。")
                    break

            tool_name, tool_input = self._parse_action(action)

            if not tool_name:
                print(f"⚠️  无法解析 Action 格式: {action}")
                self.history.append(f"Action: {action}")
                self.history.append("Observation: Action 格式错误，请使用 tool_name[input] 格式。")
                continue

            print(f"🔧 Action: {tool_name}[{tool_input}]")

            # 5. 调用工具
            tool_fn = self.tool_executor.getTool(tool_name)
            if tool_fn is None:
                observation = f"错误：未找到工具 '{tool_name}'，可用工具: {self.tool_executor.getAvailableTools()}"
            else:
                observation = tool_fn(tool_input)

            # 截断过长的 observation 显示（实际完整内容写入 history）
            preview = observation[:200] + "..." if len(observation) > 200 else observation
            print(f"👀 Observation: {preview}")

            # 6. 记录本轮 Action + Observation 到历史
            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")

        print(f"\n⛔ 已达最大步数 ({self.max_steps})，流程结束。")
        return None

    def _parse_output(self, text: str) -> tuple[Optional[str], Optional[str]]:
        """解析 LLM 输出中的 Thought 和 Action"""
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)
        action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)

        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip().strip("`").strip() if action_match else None
        return thought, action

    def _parse_action(self, action_text: str) -> tuple[Optional[str], str]:
        """解析 Action 字符串，格式: ToolName[input]"""
        match = re.match(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
        if match:
            return match.group(1), match.group(2)
        return None, ""
