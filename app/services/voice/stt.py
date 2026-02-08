"""
Aliyun Dashscope ASR Service
基于 Dashscope SDK 的语音识别服务
文档: https://help.aliyun.com/zh/model-studio/qwen-asr-realtime-python-sdk
"""
import time
import signal
import logging
import asyncio
from typing import List, AsyncGenerator

import dashscope
from dashscope.audio.asr import Recognition, RecognitionResult, RecognitionCallback

from app.config.settings import settings
from app.services.callback import ChainCallback
from app.log import get_logger

logger = get_logger(__name__)

dashscope.api_key = settings.ALIYUN_ACCESS_KEY
dashscope.base_websocket_api_url='wss://dashscope.aliyuncs.com/api-ws/v1/inference'


class ASRCallbackWrapper(RecognitionCallback):
    """ASR 回调处理"""

    def __init__(self, callback: ChainCallback):
        self.callback = callback

    def on_result(self, result) -> None:
        logger.info(f"ASR result: {result}")

    def on_error(self, result) -> None:
        logger.error(f"ASR error: {result}")

    def on_complete(self) -> None:
        logger.info("ASR recognition complete")

    def on_event(self, result: RecognitionResult) -> None:
        sentence = result.output.sentence
        is_final = sentence['sentence_end']
        text = sentence['text']
        logger.info(f"STT: {text}, {is_final}")
        self.callback.on_text(text, is_final=is_final)


class DashscopeSTT:
    """阿里云 Dashscope 语音识别"""

    def __init__(self, callback: ChainCallback):
        self.sample_rate = settings.AUDIO_SAMPLE_RATE
        self.model = "fun-asr-realtime"
        self.callback = ASRCallbackWrapper(callback)
        self.recognition = Recognition(
            model=self.model,
            format="wav",
            sample_rate=self.sample_rate,
            semantic_punctuation_enabled=False,
            callback=self.callback)
        self.recognition.SILENCE_TIMEOUT_S = 10
        self.started = False

    async def start(self):
        if not self.started:
            logger.info("Starting ASR recognition...")
            self.recognition.start()
            self.started = True
            logger.info("ASR recognition started")

    async def stop(self):
        if self.started:
            logger.info("Stopping ASR recognition...")
            self.recognition.stop()
            self.started = False
            logger.info("ASR recognition stopped")

    async def recognize(self, audio_bytes: bytes, is_final: bool = False):
        if not self.started:
            await self.start()
        try:
            self.recognition.send_audio_frame(audio_bytes)
        except Exception as e:
            raise e
        if is_final:
            await self.stop()
