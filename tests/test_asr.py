import os
import sys
import logging
import asyncio
import pyaudio
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.voice.asr import DashscopeSTT

logging.basicConfig(level=logging.INFO)
asr = DashscopeSTT()

async def print_texts(asr: DashscopeSTT):
    print("Starting to print recognized texts...")
    async for text in asr.texts():
        if text is None:
            break
        print(f"Recognized: {text}")

async def test_asr():
    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True)
    start_time = time.time()
    while True:
        data = stream.read(3200, exception_on_overflow=False)
        await asr.recognize(data)
        await asyncio.sleep(0.1)
        if time.time() - start_time > 5:  # Run for 10 seconds
            await asr.stop()
            break

async def main():
    asr_task = asyncio.create_task(test_asr())
    print_task = asyncio.create_task(print_texts(asr))
    await asyncio.gather(asr_task, print_task)

if __name__ == '__main__':
    asyncio.run(main())