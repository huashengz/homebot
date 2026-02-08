import sys
import time
import logging
import asyncio
import numpy
import pyaudio
import pvporcupine
import audioop
from fastapi import WebSocket
from typing import AsyncGenerator
from app.services.voice.mp3player import RealtimeMp3Player
from app.config.settings import settings

from app.schemas import Message

logger = logging.getLogger(__name__)


class BaseClient:

    async def stt_input(self) -> AsyncGenerator[bytes, None]:
        raise NotImplementedError

    async def tts_input(self) -> AsyncGenerator[str, None]:
        raise NotImplementedError

    async def llm_output(self, message: Message):
        raise NotImplementedError

    async def heartbeat(self):
        raise NotImplementedError

    async def connect(self):
        raise NotImplementedError
    
    async def close(self):
        raise NotImplementedError

        
class WebSocketClient(BaseClient):

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    async def stt_input(self) -> AsyncGenerator[bytes, None]:
        while True:
            data = await self.websocket.receive_bytes()
            yield data

    async def llm_output(self, message: Message):
        await self.websocket.send_json(message.model_dump())

    async def heartbeat(self):
        pass

    async def connect(self):
        await self.websocket.accept()

    async def close(self):
        await self.websocket.close()

    
class LocalClient(BaseClient):

    def __init__(self, rms_threshold: int = 300, enable_wakeword: bool = False):
        super().__init__()
        # RMS threshold for audio (16-bit PCM). Frames with RMS below
        # this value will be filtered out in `input()`.
        self.rms_threshold = rms_threshold
        self.mic = pyaudio.PyAudio()
        self.stream = self.mic.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            # frames_per_buffer=3200,
            input=True)
        self.porcupine = pvporcupine.create(
            access_key=settings.PICOVOICE_ACCESS_KEY,
            keyword_paths=[settings.PICOVOICE_CUSTOM_PPN],
            model_path=settings.PICOVOICE_ZH_MODEL)
        self.player = RealtimeMp3Player()
        self.last_active_time = time.time()
        self.enable_wakeword = enable_wakeword

    async def detect(self):
        if self.enable_wakeword:
            await self.wakeword_listen()
        else:
            await self.keyboard_enter()

    async def wakeword_listen(self):
        logger.info("Listening for wake word...")
        while True:
            pcm = self.stream.read(self.porcupine.frame_length, exception_on_overflow=False)
            pcm = numpy.frombuffer(pcm, dtype=numpy.int16)
            keyword_index = self.porcupine.process(pcm)
            if keyword_index >= 0:
                logger.info("Wake word detected!")
                self.last_active_time = time.time()
                break  
            else:
                await asyncio.sleep(0.05)

    async def keyboard_enter(self):
        logger.info("Enter Any Key...")
        while True:
            input()
            self.last_active_time = time.time()
            break

    async def stt_input(self) -> AsyncGenerator[bytes, None]:
        while True:
            await self.detect()
            while True:
                data = self.stream.read(3200, exception_on_overflow=False)
                # idata = numpy.frombuffer(data, dtype=numpy.int16)
                # fdata = idata.astype(numpy.float32) / 32768.0
                # rms = numpy.sqrt(numpy.mean(fdata ** 2))

                # rms = audioop.rms(data, 2)
                rms = 500

                if rms > self.rms_threshold:
                    logger.info(f"rms - {rms}")
                    self.last_active_time = time.time()
                    yield data
                    await asyncio.sleep(0.05)
                else:
                    await asyncio.sleep(0.05)

                if time.time() - self.last_active_time > 1:
                    await asyncio.sleep(0.1)
                    
                if time.time() - self.last_active_time > 10:
                    logger.info("no speech detected, break")
                    break

    async def llm_output(self, message: Message):
        if message.data.text_chunk:
            print(f"{message.data.text_chunk}", end="", flush=True)
            self.last_active_time = time.time()
        elif message.data.audio_chunk:
            self.player.write(message.data.audio_chunk)
            self.last_active_time = time.time()
        else:
            pass
        
    async def heartbeat(self):
        pass

    async def connect(self):
        self.player.start()

    async def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.mic.terminate()
        self.player.stop()

    

    

    

