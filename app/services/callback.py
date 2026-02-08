import logging
import asyncio
from app.log import get_logger

logger = get_logger(__name__)


class ChainCallback:
    """ASR 回调处理"""

    def __init__(self, text_queue: asyncio.Queue, audio_queue: asyncio.Queue):
        self.text_queue = text_queue
        self.audio_queue = audio_queue

    def on_text(self, text: str, is_final: bool) -> None:
        if text:
            try:
                self.text_queue.put_nowait((text, is_final))
            except asyncio.QueueFull:
                logger.warning("Message queue is full, dropping text: %s", text)
            except Exception:
                raise

    def on_text_complete(self) -> None:
        logger.info("ASR recognition complete")

    def on_audio(self, audio_bytes: bytes, is_final: bool) -> None:
        if audio_bytes:
            try:
                self.audio_queue.put_nowait((audio_bytes, is_final))
            except asyncio.QueueFull:
                logger.warning("Audio queue is full, dropping audio chunk of size: %d", len(audio_bytes))

    def on_audio_complete(self) -> None:
        logger.info("TTS synthesis complete")

