import os
import jinja2
import logging
from typing import AsyncGenerator
from openai import OpenAI
from app.config import settings
from app.log import get_logger

logger = get_logger(__name__)
current_dir = os.path.dirname(__file__)

class OpenAILLM:
    """阿里云 Dashscope LLM 服务"""

    def __init__(self, callback):
        self.callback = callback
        self.client = OpenAI(
            base_url=settings.OPENAI_BASE_URL,
            api_key=settings.OPENAI_API_KEY)
        self.history = []

    async def start(self):
        pass

    async def stop(self):
        pass

    async def load_prompt(self, q: str):
        prompt_file = os.path.join(current_dir, 'prompt.jinja')
        temp: jinja2.Template = jinja2.Template(open(prompt_file, 'r').read())
        return temp.render(q=q)

    async def agenerate(self, q: str, model: str = None) -> AsyncGenerator[str, None]:
        model = model or settings.OPENAI_MODEL
        answer = ""
        try:
            user_message = {"role": "user", "content": await self.load_prompt(q)}
            messages = [user_message]
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content is None:
                    continue
                answer += content
                yield content
            # self.history.append({"role": "user", "content": prompt})
            # self.history.append({"role": "assistant", "content": answer})
        except Exception as e:
            logger.error(f"LLM error: {e}")
            raise e