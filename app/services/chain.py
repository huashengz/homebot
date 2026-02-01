import logging
import enum
import asyncio
from typing import AsyncGenerator
from app.services.chat.llm import OpenAILLM
from app.services.voice.asr import DashscopeASR
from app.services.voice.tts import DashscopeTTS
from app.log import get_logger

logger = get_logger(__name__)

class SpeechStep(enum.Enum):
    ASR = "asr"
    LLM = "llm"
    TTS = "tts"

class SpeechChain():
    """语音处理链"""

    def __init__(self):
        self.asr = DashscopeASR()
        self.tts = DashscopeTTS()
        self.llm = OpenAILLM()
        self.step = SpeechStep.ASR

    async def process(self):
        request_text_chunks = []
        async for text in self.asr.texts(timeout=2.0):
            logger.info(f"Recognized text chunk: {text}")
            request_text_chunks.append(text)
        transcript = ''.join(text for text in request_text_chunks)
        logger.info(f"Final transcript: {transcript}")

        # await self.asr.stop()
        self.step = SpeechStep.LLM

        async for text in self.llm.agenerate(prompt=transcript):
            logger.info(f"Generated text chunk: {text}")
            await self.tts.synthesize(text=text, is_final=False)
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