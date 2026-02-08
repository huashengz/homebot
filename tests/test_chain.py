import os
import sys
import time
import logging

import asyncio
import dashscope
import pyaudio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.chain import BotChain
from app.client import LocalClient
from app.schemas import Message, Step

logging.basicConfig(level=logging.INFO)


async def main():
    bot = BotChain(LocalClient())
    await bot.start()


if __name__ == '__main__':
    asyncio.run(main())