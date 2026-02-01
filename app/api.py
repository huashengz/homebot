import logging
import asyncio
from fastapi import APIRouter, Request, WebSocket
from app.services.chain import SpeechChain
from app.log import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

    
@router.get("/models", tags=["LLM"])
async def list_models():
    # Placeholder for model listing logic
    models = ["qwen-plus", ]
    return {"available_models": models}

    


@router.websocket("/ws")
async def speech(websocket: WebSocket):
    await websocket.accept()
    chain = SpeechChain()

    async def text_output():
        async for chunk in chain.output():
            logger.info(f"Sending audio chunk of size: {len(chunk)} bytes")
            await websocket.send_text(chunk)
 
    asyncio.create_task(text_output())

    while True:
        try:
            data = await websocket.receive_bytes()
            logger.info(f"Received audio chunk of size: {len(data)} bytes")
            await chain.input([data])
        except Exception as e:
            logger.info(f"Audio input stream ended: {e}")
            break
    await websocket.close()