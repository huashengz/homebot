"""
Aliyun Dashscope TTS Service
基于 Dashscope API 的文本转语音服务
文档: https://help.aliyun.com/zh/model-studio/qwen-tts-api
"""
import asyncio
import base64
import logging
import threading
from typing import Optional, Dict, Any, AsyncGenerator

import dashscope
from dashscope.audio.tts_v2 import SpeechSynthesizer, ResultCallback
from app.config.settings import settings
from app.log import get_logger

logger = get_logger(__name__)

dashscope.api_key = settings.ALIYUN_ACCESS_KEY

class Callback(ResultCallback):

    def __init__(self, tts: 'DashscopeTTS'):
        self.tts = tts

    def on_data(self, data: bytes):
        if data:
            self.tts.put_nowait(data)

    def on_complete(self):
        logger.info("TTS synthesis complete")
        self.tts.put_nowait(None)

class DashscopeTTS:
    """阿里云 Dashscope 文本转语音"""

    def __init__(self):
        self.model = "cosyvoice-v3-flash"
        self.voice = "longanhuan"
        self.queue = asyncio.Queue(1000)
        self.callback = Callback(self)
        self.synthesizer = SpeechSynthesizer(
            model=self.model,
            voice=self.voice,
            callback=self.callback)

    def start(self):
        pass

    async def stop(self):
        self.synthesizer.async_streaming_complete()

    def put_nowait(self, data: bytes):
        self.queue.put_nowait(data)

    async def synthesize(self, text: str, is_final: bool = False):
        try:
            logger.info(f"synthesizing text: {text}")
            self.synthesizer.streaming_call(text=text)
            if is_final:
                await self.stop()
        except Exception as e:
            logger.error(f"Dashscope TTS error: {e}")

    async def chunks(self) -> AsyncGenerator[bytes, None]:
        while True:
            try:
                chunk = self.queue.get_nowait()
            except asyncio.QueueEmpty:
                await asyncio.sleep(0.1)
                continue
            if chunk is None:
                logger.info("Received TTS end signal")
                break
            yield chunk