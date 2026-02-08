import logging
import traceback
import asyncio
from fastapi import APIRouter, WebSocket
from app.client import WebSocketClient
from app.services.chain import BotChain, Step
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


@router.websocket("/ws")
async def speech(websocket: WebSocket):
    client = WebSocketClient(websocket)
    chain = BotChain(client)
    await chain.start()
    await chain.process()
    try:
        async for data in client.input():
            pass
    except Exception as e:
        traceback.print_exc()
    finally:
        await chain.stop()