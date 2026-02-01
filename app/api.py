import logging
import asyncio
from fastapi import APIRouter, Request, WebSocket
from app.services.chain import SpeechChain, SpeechStep
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
            await websocket.send_bytes(chunk)
 
    output_task = asyncio.create_task(text_output())

    try:
        while chain.step == SpeechStep.ASR:
            data = await websocket.receive_bytes()
            await chain.input([data])
    except Exception as e:
        logger.info(f"Audio input stream ended: {e}")
    finally:
        await output_task
        await websocket.close()