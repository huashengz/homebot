import os
import sys
import time
import logging

import asyncio
import dashscope
import pyaudio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.chat.llm import OpenAILLM
from app.services.voice.tts import DashscopeTTS
from app.services.chain import SpeechChain
from app.services.voice.mp3player import RealtimeMp3Player

logging.basicConfig(level=logging.INFO)

player = RealtimeMp3Player()
chain = SpeechChain()

async def speak():
    player.start()
    async for chunk in chain.output():
        player.write(chunk)
    await asyncio.sleep(0.5)  # wait for the player to finish
    player.stop()

async def mic_input():
    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True)
    start_time = time.time()
    while True:
        data = stream.read(3200, exception_on_overflow=False)
        await chain.input([data])
        await asyncio.sleep(0.1)
        if time.time() - start_time > 5:  # Run for 10 seconds
            break


async def main():
    llm_task = asyncio.create_task(mic_input())
    speak_task = asyncio.create_task(speak())
    await asyncio.gather(llm_task, speak_task)


if __name__ == '__main__':
    asyncio.run(main())