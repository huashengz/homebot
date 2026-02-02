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
from app.log import get_logger

logger = get_logger(__name__)

dashscope.api_key = settings.ALIYUN_ACCESS_KEY
dashscope.base_websocket_api_url='wss://dashscope.aliyuncs.com/api-ws/v1/inference'


class ASRCallback(RecognitionCallback):
    """ASR 回调处理"""

    def __init__(self, asr: 'DashscopeASR'):
        self.asr = asr

    def on_result(self, result) -> None:
        print(f"ASR result: {result}")

    def on_error(self, result) -> None:
        logger.error(f"ASR error: {result}")

    def on_complete(self) -> None:
        logger.info("ASR recognition complete")

    def on_event(self, result: RecognitionResult) -> None:
        sentence = result.output.sentence
        is_final = sentence['sentence_end']
        text = sentence['text']
        if is_final and text:
            self.asr.put_nowait(text)
        


class DashscopeASR:
    """阿里云 Dashscope 语音识别"""

    def __init__(self):
        self.sample_rate = settings.AUDIO_SAMPLE_RATE
        self.model = "fun-asr-realtime"
        self.callback = ASRCallback(self)
        self.queue = asyncio.Queue(1000)
        self.recognition = Recognition(
            model=self.model,
            format="pcm",
            sample_rate=self.sample_rate,
            semantic_punctuation_enabled=False,
            callback=self.callback)
        self.started = False

    async def start(self):
        if not self.started:
            logger.info("Starting ASR recognition...")
            self.recognition.start()
            self.started = True

    def put_nowait(self, text: str):
        self.queue.put_nowait(text)

    async def recognize(self, audio_bytes: bytes, is_final: bool = False):
        if not self.started:
            await self.start()
        self.recognition.send_audio_frame(audio_bytes)
        if is_final:
            await self.stop()

    async def stop(self):
        if self.started:
            logger.info("Stopping ASR recognition...")
            self.queue.put_nowait(None)
            self.recognition.stop()
            self.started = False

    async def texts(self, timeout: float = 2.0) -> AsyncGenerator[str, None]:
        last_received = None
        while True:
            try:
                text = self.queue.get_nowait()
            except asyncio.QueueEmpty:
                await asyncio.sleep(0.1)
                if last_received and (time.time() - last_received) > timeout:
                    logger.info("ASR texts timeout reached")
                    break
                continue
            if text is None:
                logger.info("Received ASR end signal")
                break
            if text:
                last_received = time.time()
                yield text