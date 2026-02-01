import os
import sys
import time
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.voice.tts import DashscopeTTS
from app.services.voice.mp3player import RealtimeMp3Player


async def test_tts():
    player = RealtimeMp3Player()
    player.start()
    tts = DashscopeTTS()
    text = "你好，今天天气不错，适合出去散步。"
    await tts.synthesize(text=text)
    text = "我今天心情很好，因为我完成了一个重要的项目。"
    await tts.synthesize(text=text, is_final=True)
    print(f"chunks size: {tts.queue.qsize()}")
    async for chunk in tts.chunks():
        player.write(chunk)
    await asyncio.sleep(1)
    player.stop()

    
if __name__ == '__main__':
    asyncio.run(test_tts())