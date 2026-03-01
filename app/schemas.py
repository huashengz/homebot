import time
from typing import Literal, Optional, List
from enum import Enum
from pydantic import BaseModel, Field


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


# Chat Models
class ChatRequest(BaseModel):
    content: str = Field(..., description="Message content")


class ChatResponse(BaseModel):
    response: str = Field(..., description="Chat response")
    session_id: str = Field(..., description="Session ID")


class ChatHistory(BaseModel):
    session_id: str = Field(..., description="Session ID")
    messages: List[dict] = Field(default_factory=list, description="Chat messages")


# Voice Models
class VoiceRecognitionRequest(BaseModel):
    engine: str = Field(default="aliyun", description="ASR engine")
    duration: float = Field(default=5.0, description="Recording duration in seconds")


class ContinuousVoiceRecognitionRequest(BaseModel):
    engine: str = Field(default="aliyun", description="ASR engine")
    timeout: float = Field(default=10.0, description="Timeout in seconds")


class VoiceRecognitionResponse(BaseModel):
    text: str = Field(..., description="Recognized text")
    engine: str = Field(..., description="ASR engine used")


class TTSRequest(BaseModel):
    text: str = Field(..., description="Text to synthesize")
    voice: str = Field(default="xiaoyun", description="Voice name")
    save_to_file: bool = Field(default=False, description="Save to file")


class TTSResponse(BaseModel):
    voice_file: str = Field(..., description="Path to synthesized voice file")
    text: str = Field(..., description="Original text")


class TTSInfo(BaseModel):
    voices: List[str] = Field(..., description="Available voices")


class EngineList(BaseModel):
    engines: List[str] = Field(..., description="Available ASR engines")


# WebSocket Models
class WebSocketTextMessage(BaseModel):
    type: Literal["text"] = "text"
    content: str = Field(..., description="Message content")


class WebSocketVoiceMessage(BaseModel):
    type: Literal["voice"] = "voice"
    audio_path: str = Field(..., description="Path to audio file")
    engine: str = Field(default="aliyun", description="ASR engine")
    voice: str = Field(default="xiaoyun", description="Voice name")


class WebSocketTextResponse(BaseModel):
    type: Literal["text_response"] = "text_response"
    content: str = Field(..., description="Response content")
    session_id: str = Field(..., description="Session ID")


class WebSocketVoiceResponse(BaseModel):
    type: Literal["voice_response"] = "voice_response"
    text: str = Field(..., description="Original text")
    response: str = Field(..., description="Response content")
    voice_file: str = Field(..., description="Path to voice file")
    session_id: str = Field(..., description="Session ID")
    engine_used: str = Field(..., description="ASR engine used")
    voice: str = Field(..., description="Voice name")


# Health Models
class HealthCheck(BaseModel):
    status: str = Field(..., description="Health status")


class DetailedHealthCheck(BaseModel):
    status: str = Field(..., description="Overall health status")
    components: dict = Field(..., description="Component health statuses")
