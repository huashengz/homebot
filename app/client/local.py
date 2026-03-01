#!/usr/bin/env python3
"""
Console client for AnyBot

This script provides a command-line interface to interact with the AnyBot server.
It allows users to send text messages and receive responses from the AI chatbot.
"""

import argparse
import asyncio
import sys
import time
import logging
import numpy
import pyaudio
import pvporcupine
import audioop
from fastapi import WebSocket
from typing import AsyncGenerator, Optional

from app.services.voice.mp3player import RealtimeMp3Player
from app.config.settings import settings
from app.schemas import Message
from app.services.chain import BotChain
from app.client.base import BaseClient


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description="Local client for AnyBot")
parser.add_argument("--speech")

class LocalClient(BaseClient):

    def __init__(self, rms_threshold: int = 300):
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

    async def detect(self):
        logger.info("Listening for wake word... (Press Enter to start recording)")
        # Create a task to listen for keyboard input
        async def listen_for_enter():
            input()
            return True
        
        enter_task = asyncio.create_task(listen_for_enter())
        
        try:
            while True:
                # Check if Enter was pressed
                if enter_task.done():
                    logger.info("Enter key pressed!")
                    self.last_active_time = time.time()
                    break
                
                # Listen for wake word
                pcm = self.stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                pcm = numpy.frombuffer(pcm, dtype=numpy.int16)
                keyword_index = self.porcupine.process(pcm)
                if keyword_index >= 0:
                    logger.info("Wake word detected!")
                    self.last_active_time = time.time()
                    break  
                else:
                    await asyncio.sleep(0.05)
        finally:
            # Cancel the enter task if it's still running
            if not enter_task.done():
                enter_task.cancel()
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

    async def start(self):
        self.player.start()

    async def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.mic.terminate()
        self.player.stop()


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AnyBot Console Client")
    args = parser.parse_args()

    client = LocalClient()
    try:
        print("Starting AnyBot local client...")
        print("Press Enter to start recording, and speak into the microphone")
        print("The client will automatically detect when you stop speaking")
        print("Type 'exit' to quit")
        
        # Create a BotChain instance with this client
        from app.services.chain import BotChain
        chain = BotChain(client)
        
        # Start the BotChain
        await chain.start()
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Close the client
        await chain.stop()


if __name__ == "__main__":
    asyncio.run(main())
