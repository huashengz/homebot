import os
import sys
import time
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.voice.tts import DashscopeTTS
from app.services.voice.mp3player import RealtimeMp3Player
from app.services.callback import ChainCallback


async def test_tts():
    # Create queues for callback
    text_queue = asyncio.Queue()
    audio_queue = asyncio.Queue()
    
    # Create callback
    callback = ChainCallback(text_queue, audio_queue)
    
    player = RealtimeMp3Player()
    player.start()
    tts = DashscopeTTS(callback)
    text = "你好，今天天气不错，适合出去散步。"
    await tts.synthesize(text=text)
    text = "我今天心情很好，因为我完成了一个重要的项目。"
    await tts.synthesize(text=text, is_final=True)
    print(f"chunks size: {audio_queue.qsize()}")
    while not audio_queue.empty():
        chunk, is_final = await audio_queue.get()
        if chunk:
            player.write(chunk)
    await asyncio.sleep(1)
    player.stop()

    
if __name__ == '__main__':
    asyncio.run(test_tts())