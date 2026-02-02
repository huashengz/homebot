import logging
import asyncio
from fastapi import APIRouter, WebSocket
from app.services.chain import SpeechChain, SpeechStep
from app.schemas import TurnDone
from app.log import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

@router.get("/models", tags=["LLM"])
async def list_models():
    models = ["qwen-plus"]
    return {"available_models": models}


def _make_tasks(websocket, chain):
    async def send_messages():
        while True:
            try:
                msg = await asyncio.wait_for(chain.message_queue.get(), timeout=0.1)
                await websocket.send_json(msg.model_dump())
            except asyncio.TimeoutError:
                await asyncio.sleep(0.05)
            except Exception:
                break

    async def send_audio():
        async for chunk in chain.output():
            await websocket.send_bytes(chunk)
        await websocket.send_json(TurnDone().model_dump())

    return asyncio.create_task(send_messages()), asyncio.create_task(send_audio())


@router.websocket("/ws")
async def speech(websocket: WebSocket):
    await websocket.accept()
    chain = None
    message_task = None
    output_task = None

    try:
        while True:
            data = await websocket.receive_bytes()
            if chain is None or (output_task and output_task.done() and chain.step != SpeechStep.ASR):
                if message_task:
                    message_task.cancel()
                    try:
                        await message_task
                    except asyncio.CancelledError:
                        pass
                chain = SpeechChain()
                message_task, output_task = _make_tasks(websocket, chain)
            if chain.step == SpeechStep.ASR:
                await chain.input([data])
    except Exception as e:
        logger.info(f"WebSocket stream ended: {e}")
    finally:
        if message_task:
            message_task.cancel()
            try:
                await message_task
            except asyncio.CancelledError:
                pass
        if output_task and not output_task.done():
            await output_task
        await websocket.close()