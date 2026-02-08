import enum
import time
import logging
import asyncio
from collections.abc import Coroutine
from typing import AsyncGenerator, List
from contextlib import suppress

from app.services.chat.llm import OpenAILLM
from app.services.voice.stt import DashscopeSTT
from app.services.voice.tts import DashscopeTTS
from app.schemas import Step, Role, Payload, Message
from app.services.callback import ChainCallback
from app.client import BaseClient

logger = logging.getLogger(__name__)


class BotState:
    """收集 ASR 结果并定期发送给 LLM 进行处理"""

    def __init__(self, callback: ChainCallback):
        self.callback = callback
        self.latest_received_texts: List[Payload] = []
        self.latest_received_audios: List[Payload] = []

    async def collect(self):
        stt_task = asyncio.create_task(self.collect_stt_texts())
        tts_task = asyncio.create_task(self.collect_tts_audios())
        await asyncio.gather(stt_task, tts_task)

    async def clear(self):
        self.latest_received_texts.clear()
        self.latest_received_audios.clear()

    async def collect_stt_texts(self):
        while True:
            try:
                result = self.callback.text_queue.get_nowait()
                text, is_final = result
                logger.info(f"collect text: {text}")
            except asyncio.QueueEmpty:
                await asyncio.sleep(0.05)
                continue
            text_payload = Payload(role=Role.USER, text_chunk=text, is_final=is_final)
            self.latest_received_texts.append(text_payload)

    async def collect_tts_audios(self):
        while True:
            try:
                audio_bytes, is_final = self.callback.audio_queue.get_nowait()
            except asyncio.QueueEmpty:
                await asyncio.sleep(0.1)
                continue
            audio_payload = Payload(role=Role.ASSISTANT, audio_chunk=audio_bytes, is_final=is_final)
            self.latest_received_audios.append(audio_payload)

    async def stream_query(self) -> AsyncGenerator[str, None]:
        while True:
            full_text = ""
            if len(self.latest_received_texts) > 0:
                last_payload = self.latest_received_texts[-1]
                wait_seconds = time.time() - last_payload.dttm
                if (last_payload.is_final and wait_seconds > 1) or wait_seconds > 3:
                    full_text = "".join([p.text_chunk for p in self.latest_received_texts])
                    logger.info(f"Stream Query: {full_text}")
                    self.latest_received_texts.clear()
                    if full_text:
                        yield full_text
            else:
                logger.info(f"Stream Query: beat")
                await asyncio.sleep(0.05)


class BotChain:
    """STT -> LLM -> TTS"""

    def __init__(self, client: BaseClient):
        self.step: Step = Step.STARTED
        self.client = client

        self.text_queue: asyncio.Queue[tuple[str, bool]] = asyncio.Queue(maxsize=1000)
        self.audio_queue: asyncio.Queue[tuple[bytes, bool]] = asyncio.Queue(maxsize=1000)

        self.callback = ChainCallback(self.text_queue, self.audio_queue)

        self.stt = DashscopeSTT(self.callback)
        self.tts = DashscopeTTS(self.callback)
        self.llm = OpenAILLM(self.callback)
        self.state: BotState = BotState(self.callback)
        self.tasks: List[asyncio.tasks.Task] = []

    async def start(self):
        logger.info("Starting BotChain...")
        await self.client.connect()
        self.step = Step.ASR

        receive_task = asyncio.create_task(self.process_audio_receive())
        generate_task = asyncio.create_task(self.process_llm_generate())
        state_task = asyncio.create_task(self.state.collect())
        
        self.tasks.append(receive_task)
        self.tasks.append(generate_task)
        self.tasks.append(state_task)
        try:
            await asyncio.wait(self.tasks)
        except asyncio.CancelledError:
            logger.info("Cancelling BotChain...")
            for task in self.tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*self.tasks, return_exceptions=True)
        finally:
            await self.stop()

    async def stop(self):
        logger.info("Stopping BotChain...")
        await self.client.close()
        await self.state.clear()
        await self.stt.stop()
        await self.tts.stop()
        await self.llm.stop()
        self.tasks.clear()

    async def process_audio_receive(self):
        try:
            logger.info("Starting to receive audio data from client")
            async for data in self.client.input():
                await self.stt.ensure_started()
                if self.step == Step.ASR:
                    await self.stt.recognize(data, is_final=False)
                    await asyncio.sleep(0.005)
                else:
                    await asyncio.sleep(0.05)
                    continue
        except Exception as e:
            logger.error(f"Error receiving audio data: {e}")
        logger.info("Stopped receiving audio data from client")

    async def process_llm_generate(self):
        logger.info("Starting LLM generation process")
        try:
            async for query in self.state.stream_query():
                logger.info(f"User Query: {query}")
                await self.stt.stop()
                # await self.state.clear()
                self.step = Step.LLM
                async for text_chunk in self.llm.agenerate(query):
                    message = Message(
                        cmd=Step.LLM, 
                        data=Payload(
                            role=Role.ASSISTANT, 
                            text_chunk=text_chunk, 
                            is_final=False))
                    await self.client.output(message)
                self.step = Step.ASR
        except Exception as e:
            logger.error(f"Error in speech chain: {e}")
        finally:
            await self.stop()
        logger.info("LLM generation process ended")

    async def process_text_synthesize(self):
        pass

    async def run_forever(self):
        try:
            await self.start()
        except Exception as e:
            logger.error(f"Error in speech chain: {e}")
        finally:
            await self.stop()

