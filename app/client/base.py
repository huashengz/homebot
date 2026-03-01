from app.schemas import Message
from typing import AsyncGenerator


class BaseClient:

    async def stt_input(self) -> AsyncGenerator[bytes, None]:
        raise NotImplementedError

    async def tts_input(self) -> AsyncGenerator[str, None]:
        raise NotImplementedError

    async def llm_output(self, message: Message):
        raise NotImplementedError

    async def heartbeat(self):
        raise NotImplementedError

    async def start(self):
        raise NotImplementedError
    
    async def stop(self):
        raise NotImplementedError

    async def run(self):
        raise NotImplementedError