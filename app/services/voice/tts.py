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
from app.services.callback import ChainCallback
from app.config.settings import settings
from app.log import get_logger

logger = get_logger(__name__)

dashscope.api_key = settings.ALIYUN_ACCESS_KEY

class CallbackWrapper(ResultCallback):

    def __init__(self, callback: ChainCallback):
        self.callback = callback

    def on_data(self, data: bytes):
        if data:
            self.callback.on_audio(data, is_final=False)

    def on_complete(self):
        logger.info("TTS synthesis complete")
        self.callback.on_audio(b"", is_final=True)
        self.callback.on_audio_complete()

class DashscopeTTS:
    """阿里云 Dashscope 文本转语音"""

    def __init__(self, callback: ChainCallback):
        self.model = "cosyvoice-v3-flash"
        self.voice = "longanhuan"
        self.callbackwrap = CallbackWrapper(callback)
        self.synthesizer = SpeechSynthesizer(
            model=self.model,
            voice=self.voice,
            callback=self.callbackwrap)

    async def start(self):
        pass

    async def stop(self):
        self.synthesizer.async_streaming_complete()

    async def synthesize(self, text: str, is_final: bool = False):
        try:
            logger.info(f"synthesizing text: {text}")
            self.synthesizer.streaming_call(text=text)
            if is_final:
                await self.stop()
        except Exception as e:
            logger.error(f"Dashscope TTS error: {e}")