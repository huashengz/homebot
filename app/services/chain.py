import logging
import enum
import asyncio
from typing import AsyncGenerator
from app.services.chat.llm import OpenAILLM
from app.services.voice.asr import DashscopeASR
from app.services.voice.tts import DashscopeTTS
from app.schemas import SentenceComplete, TextContent
from app.log import get_logger

logger = get_logger(__name__)

class SpeechStep(enum.Enum):
    ASR = "asr"
    LLM = "llm"
    TTS = "tts"

class SpeechChain():
    def __init__(self):
        self.asr = DashscopeASR()
        self.tts = DashscopeTTS()
        self.llm = OpenAILLM()
        self.step = SpeechStep.ASR
        self.message_queue: asyncio.Queue = asyncio.Queue()

    def _put_message(self, msg):
        try:
            self.message_queue.put_nowait(msg)
        except asyncio.QueueFull:
            pass

    async def process(self):
        request_text_chunks = []
        async for text in self.asr.texts(timeout=2.0):
            if not request_text_chunks:
                self._put_message(SentenceComplete())
            logger.info(f"Recognized text chunk: {text}")
            request_text_chunks.append(text)
        transcript = ''.join(request_text_chunks)
        logger.info(f"Final transcript: {transcript}")

        self.step = SpeechStep.LLM
        reply_chunks = []
        async for text in self.llm.agenerate(prompt=transcript):
            reply_chunks.append(text)
            await self.tts.synthesize(text=text, is_final=False)
        full_reply = ''.join(reply_chunks)
        if full_reply:
            self._put_message(TextContent(content=full_reply))
        await self.tts.synthesize(text="", is_final=True)
        self.step = SpeechStep.TTS

    async def input(self, audio_stream) -> None:
        """处理输入音频流"""
        for audio_chunk in audio_stream:
            if self.step != SpeechStep.ASR:
                await asyncio.sleep(0.1)
                continue
            logger.info(f"Processing audio chunk of size: {len(audio_chunk)} bytes")
            await self.asr.recognize(audio_chunk)

    async def output(self) -> AsyncGenerator[bytes, None]:
        asyncio.create_task(self.process())
        async for chunk in self.tts.chunks():
            yield chunk
        # self.step = SpeechStep.ASR