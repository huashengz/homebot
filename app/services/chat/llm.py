import logging
from typing import AsyncGenerator
from openai import OpenAI
from app.config import settings
from app.log import get_logger

logger = get_logger(__name__)

class OpenAILLM:
    """阿里云 Dashscope LLM 服务"""

    def __init__(self):
        self.client = OpenAI(
            base_url=settings.OPENAI_BASE_URL,
            api_key=settings.OPENAI_API_KEY)
        self.history = []

    def get_system_message(self) -> dict:
        system_prompt = """
            你是一个有帮助的助手。请用中文回答用户的问题。回答必须非常简洁。因为我们是在一个语音对话场景中。
        """
        return {"role": "system", "content": system_prompt}

    async def agenerate(self, prompt: str, model: str = None) -> AsyncGenerator[str, None]:
        model = model or settings.OPENAI_MODEL
        answer = ""
        try:
            user_message = {"role": "user", "content": prompt}
            messages = [self.get_system_message()] + self.history[-5:] + [user_message]
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )
            for chunk in response:
                content = chunk.choices[0].delta.content
                answer += content
                yield content
            self.history.append({"role": "user", "content": prompt})
            self.history.append({"role": "assistant", "content": answer})
        except Exception as e:
            logger.error(f"LLM error: {e}")
            raise e