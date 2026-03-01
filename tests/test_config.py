import pytest
import os
from app.config import get_settings


def test_settings_loading():
    """Test that settings are loaded correctly"""
    settings = get_settings()
    assert settings.PROJECT_NAME == "AnyBot"
    assert settings.VERSION == "0.1.0"
    assert settings.DESCRIPTION == "A FastAPI + LangChain voice chatbot"


def test_required_settings():
    """Test that required settings are present"""
    settings = get_settings()
    assert settings.OPENAI_API_KEY
    assert settings.ALIYUN_ACCESS_KEY_ID
    assert settings.ALIYUN_ACCESS_KEY_SECRET
    assert settings.ALIYUN_ASR_APP_KEY
    assert settings.PICOVOICE_ACCESS_KEY
    assert settings.PICOVOICE_CUSTOM_PPN
    assert settings.PICOVOICE_ZH_MODEL
    assert settings.HOMEASSISTANT_ENDPOINT
    assert settings.HOMEASSISTANT_TOKEN


def test_settings_property():
    """Test that ALIYUN_ACCESS_KEY property works"""
    settings = get_settings()
    assert settings.ALIYUN_ACCESS_KEY == settings.ALIYUN_ACCESS_KEY_ID
