import pytest
from app.schemas import (
    Step, Role, Payload, Message, CMD, DeviceEvent,
    ChatRequest, ChatResponse, ChatHistory,
    VoiceRecognitionRequest, ContinuousVoiceRecognitionRequest,
    VoiceRecognitionResponse, TTSRequest, TTSResponse,
    TTSInfo, EngineList,
    WebSocketTextMessage, WebSocketVoiceMessage,
    WebSocketTextResponse, WebSocketVoiceResponse,
    HealthCheck, DetailedHealthCheck
)


def test_step_enum():
    """Test Step enum"""
    assert Step.STARTED == "started"
    assert Step.STOPPED == "stopped"
    assert Step.PAUSED == "paused"
    assert Step.ASR == "asr"
    assert Step.LLM == "llm"
    assert Step.TTS == "tts"


def test_role_enum():
    """Test Role enum"""
    assert Role.USER == "user"
    assert Role.ASSISTANT == "assistant"
    assert Role.SYSTEM == "system"


def test_cmd_enum():
    """Test CMD enum"""
    assert CMD.ON == "turn_on"
    assert CMD.OFF == "turn_off"


def test_payload_model():
    """Test Payload model"""
    payload = Payload(
        role=Role.USER,
        text_chunk="Hello",
        is_final=True
    )
    assert payload.role == Role.USER
    assert payload.text_chunk == "Hello"
    assert payload.is_final == True


def test_message_model():
    """Test Message model"""
    payload = Payload(role=Role.USER, text_chunk="Hello")
    message = Message(step=Step.ASR, data=payload)
    assert message.step == Step.ASR
    assert message.data == payload


def test_device_event_model():
    """Test DeviceEvent model"""
    event = DeviceEvent(cmd=CMD.ON, message="Turn on device")
    assert event.cmd == CMD.ON
    assert event.message == "Turn on device"


def test_chat_request_model():
    """Test ChatRequest model"""
    request = ChatRequest(content="Hello")
    assert request.content == "Hello"


def test_chat_response_model():
    """Test ChatResponse model"""
    response = ChatResponse(response="Hi there", session_id="test-session")
    assert response.response == "Hi there"
    assert response.session_id == "test-session"


def test_chat_history_model():
    """Test ChatHistory model"""
    history = ChatHistory(session_id="test-session", messages=[])
    assert history.session_id == "test-session"
    assert history.messages == []


def test_voice_recognition_request_model():
    """Test VoiceRecognitionRequest model"""
    request = VoiceRecognitionRequest(engine="aliyun", duration=5.0)
    assert request.engine == "aliyun"
    assert request.duration == 5.0


def test_continuous_voice_recognition_request_model():
    """Test ContinuousVoiceRecognitionRequest model"""
    request = ContinuousVoiceRecognitionRequest(engine="aliyun", timeout=10.0)
    assert request.engine == "aliyun"
    assert request.timeout == 10.0


def test_voice_recognition_response_model():
    """Test VoiceRecognitionResponse model"""
    response = VoiceRecognitionResponse(text="Hello", engine="aliyun")
    assert response.text == "Hello"
    assert response.engine == "aliyun"


def test_tts_request_model():
    """Test TTSRequest model"""
    request = TTSRequest(text="Hello", voice="xiaoyun", save_to_file=True)
    assert request.text == "Hello"
    assert request.voice == "xiaoyun"
    assert request.save_to_file == True


def test_tts_response_model():
    """Test TTSResponse model"""
    response = TTSResponse(voice_file="tts_output.wav", text="Hello")
    assert response.voice_file == "tts_output.wav"
    assert response.text == "Hello"


def test_tts_info_model():
    """Test TTSInfo model"""
    info = TTSInfo(voices=["xiaoyun", "xiaoya"])
    assert info.voices == ["xiaoyun", "xiaoya"]


def test_engine_list_model():
    """Test EngineList model"""
    engines = EngineList(engines=["aliyun", "google"])
    assert engines.engines == ["aliyun", "google"]


def test_websocket_text_message_model():
    """Test WebSocketTextMessage model"""
    message = WebSocketTextMessage(content="Hello")
    assert message.type == "text"
    assert message.content == "Hello"


def test_websocket_voice_message_model():
    """Test WebSocketVoiceMessage model"""
    message = WebSocketVoiceMessage(audio_path="test.wav", engine="aliyun", voice="xiaoyun")
    assert message.type == "voice"
    assert message.audio_path == "test.wav"
    assert message.engine == "aliyun"
    assert message.voice == "xiaoyun"


def test_websocket_text_response_model():
    """Test WebSocketTextResponse model"""
    response = WebSocketTextResponse(content="Hi there", session_id="test-session")
    assert response.type == "text_response"
    assert response.content == "Hi there"
    assert response.session_id == "test-session"


def test_websocket_voice_response_model():
    """Test WebSocketVoiceResponse model"""
    response = WebSocketVoiceResponse(
        text="Hello",
        response="Hi there",
        voice_file="tts_output.wav",
        session_id="test-session",
        engine_used="aliyun",
        voice="xiaoyun"
    )
    assert response.type == "voice_response"
    assert response.text == "Hello"
    assert response.response == "Hi there"
    assert response.voice_file == "tts_output.wav"
    assert response.session_id == "test-session"
    assert response.engine_used == "aliyun"
    assert response.voice == "xiaoyun"


def test_health_check_model():
    """Test HealthCheck model"""
    health = HealthCheck(status="ok")
    assert health.status == "ok"


def test_detailed_health_check_model():
    """Test DetailedHealthCheck model"""
    health = DetailedHealthCheck(
        status="ok",
        components={"api": "healthy", "services": "healthy"}
    )
    assert health.status == "ok"
    assert health.components == {"api": "healthy", "services": "healthy"}
