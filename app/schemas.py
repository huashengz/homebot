import time
from typing import Literal, Optional
from enum import Enum
from pydantic import BaseModel


class Step(str, Enum):
    STARTED = "started"
    STOPPED = "stopped"
    PAUSED = "paused"

    ASR = "asr"
    LLM = "llm"
    TTS = "tts"



class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Payload(BaseModel):
    role: Optional[Role] = None
    text_chunk: Optional[str] = None
    audio_chunk: Optional[bytes] = None
    is_final: bool = False
    dttm: float = time.time()

    
class Message(BaseModel):
    step: Step
    data: Optional[Payload] = None


class CMD(str, Enum):
    ON = "turn_on"
    OFF = "turn_off"

   
class DeviceEvent(BaseModel):
    cmd: CMD
    message: str