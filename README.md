# AnyBot - Voice Chatbot

A modern FastAPI + LangChain voice chatbot with real-time WebSocket communication.

## Features

- 🤖 **AI Chat**: Powered by LangChain and OpenAI
- 🎤 **Voice Input**: Aliyun ASR speech-to-text (Chinese optimized)
- 🔊 **Voice Output**: Text-to-speech synthesis
- 🔄 **Real-time Communication**: WebSocket-based chat interface
- ⚡ **Modern Architecture**: Async FastAPI with proper dependency injection
- 🔧 **Configurable**: Environment-based configuration
- 🇨🇳 **Aliyun Only**: Exclusive Aliyun ASR integration for Chinese language
- 🎙️ **Microphone Support**: Direct microphone recording and continuous recognition
- 🐳 **Container Ready**: Docker support included

## Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key (for AI functionality)
- Optional: Microphone for voice input

### Installation

#### Method 1: Automated Setup (Recommended)

1. **Clone and setup**:
```bash
git clone <repository-url>
cd anybot
```

2. **Run automated setup**:
```bash
python setup.py
```

3. **Fix LangChain (if needed)**:
```bash
python fix_langchain.py
```

4. **Configure environment**:
```bash
# Edit .env file with your API keys
cp .env.example .env
```

#### Method 2: Manual Setup

1. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### Running the Application

#### Method 1: VS Code (Recommended)

1. **Open in VS Code**:
```bash
code anybot.code-workspace
# or
code .
```

2. **Use launch configurations**:
- Press `F5` and select "🚀 Run FastAPI"
- Or press `Ctrl+Shift+P` → "Tasks: Run Task" → "🚀 Start FastAPI Server"

#### Method 2: Command Line

```bash
uvicorn app.main:app --reload
```

#### Method 3: Docker

```bash
docker-compose up -d
```

### Access the Application

- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/api/v1/ws/chat/{client_id}
- **Health Check**: http://localhost:8000/health
- **Available Engines**: http://localhost:8000/api/v1/voice/engines

### VS Code Configuration

The project includes comprehensive VS Code configuration:

#### Launch Configurations (`F5`)
- `🚀 Run FastAPI` - Start development server
- `🔍 Debug FastAPI` - Debug mode
- `🧪 Run Tests` - Run all tests
- `🔬 Debug Tests` - Debug tests with pdb
- `🤖 Test LangChain` - Test LangChain integration
- `🎤 Test Aliyun ASR` - Test Aliyun ASR integration
- `🔧 Fix LangChain` - Fix LangChain import issues
- `⚡ Format Code` - Format with Black
- `📋 Sort Imports` - Sort imports with isort

#### Tasks (`Ctrl+Shift+P` → "Tasks: Run Task")
- `🚀 Start FastAPI Server` - Start server
- `🧪 Run All Tests` - Run pytest with coverage
- `🔧 Full Quality Check` - Format, lint, type check, and test
- `📦 Install Dependencies` - Install project dependencies
- `🐳 Docker Build/Run` - Docker operations

#### Extensions
The project recommends these VS Code extensions (auto-prompted on first open):
- Python extension pack
- Code formatting tools (Black, isort)
- Linting tools (flake8, mypy)
- Git integration tools
- Docker support
- Spell checker

## API Endpoints

### Health Check
- `GET /health` - Basic health check
- `GET /api/v1/health` - Detailed component health status

### Chat API
- `POST /api/v1/chat/` - Send text message
- `GET /api/v1/chat/history/{session_id}` - Get chat history

### Voice API
- `POST /api/v1/voice/recognize-file` - Recognize speech from uploaded audio file
- `POST /api/v1/voice/recognize-microphone` - Recognize speech from microphone (fixed duration)
- `POST /api/v1/voice/recognize-microphone-continuous` - Continuous microphone recognition with silence detection
- `POST /api/v1/voice/tts/synthesize` - Synthesize speech from text using Aliyun TTS
- `GET /api/v1/voice/engines` - List available ASR engines
- `GET /api/v1/voice/tts/info` - Get TTS service information and available voices

### WebSocket
- `WS /api/v1/ws/chat/{client_id}` - Real-time chat with voice support

## WebSocket Message Format

### Text Message
```json
{
  "type": "text",
  "content": "Hello, how are you?"
}
```

### Voice Message
```json
{
  "type": "voice",
  "audio_path": "/path/to/audio.wav",
  "engine": "aliyun",
  "voice": "xiaoyun"
}
```

### Response
```json
{
  "type": "text_response",
  "content": "I'm doing well, thank you!",
  "session_id": "client123"
}
```

### Voice Response
```json
{
  "type": "voice_response",
  "text": "你好",
  "response": "您好！很高兴为您服务！",
  "voice_file": "tts_output_1234567890.wav",
  "session_id": "client123",
  "engine_used": "aliyun",
  "voice": "xiaoyun"
}
```

## ASR Engines

### Available Engines

1. **Aliyun ASR** (Recommended for Chinese)
   - High accuracy for Chinese language
   - Requires Alibaba Cloud credentials
   - Real-time and batch processing support

2. **Google Speech Recognition**
   - Multi-language support
   - Requires internet connection
   - Good general accuracy

3. **CMU Sphinx** (Offline)
   - Works without internet
   - Limited language support
   - Basic accuracy

### Engine Selection

The system supports automatic engine selection (`auto`) which prefers Aliyun ASR when configured and available.

Example usage:
```python
# Use specific engine
await voice_service.process_voice_input("audio.wav", engine="aliyun")

# Auto selection
await voice_service.process_voice_input("audio.wav", engine="auto")
```

## Development

### Code Quality

```bash
# Format code
black app/
isort app/

# Lint
flake8 app/

# Type checking
mypy app/

# Run tests
pytest
```

### Project Structure

```
anybot/
├── app/
│   ├── api/                 # API routes
│   │   └── v1/              # API version 1
│   │       ├── endpoints/   # Individual endpoints
│   │       │   ├── health.py    # Health check endpoints
│   │       │   ├── chat.py      # Chat endpoints
│   │       │   └── voice.py     # Voice endpoints
│   │       └── api.py       # API router
│   ├── config/              # Configuration
│   │   └── settings.py      # Settings
│   ├── core/                # Core functionality
│   ├── devices/             # Device management
│   │   ├── base.py          # Base device class
│   │   ├── manager.py       # Device manager
│   │   └── xiaomi_cuco_switch.py # Xiaomi Cuco switch
│   ├── services/            # Business logic
│   │   ├── chat/            # Chat services
│   │   │   ├── llm.py       # LLM integration
│   │   │   └── prompt.jinja # Prompt template
│   │   ├── voice/           # Speech processing
│   │   │   ├── __init__.py  # Voice service init
│   │   │   ├── mp3player.py # MP3 player
│   │   │   ├── stt.py       # Speech-to-text
│   │   │   └── tts.py       # Text-to-speech
│   │   ├── __init__.py      # Services init
│   │   ├── callback.py      # Callbacks
│   │   └── chain.py         # Bot chain
│   ├── models/              # Data models
│   ├── utils/               # Utilities
│   ├── static/              # Static files
│   │   └── index.html       # Web interface
│   ├── __init__.py          # App init
│   ├── api.py               # Main API router
│   ├── client.py            # WebSocket client
│   ├── log.py               # Logging configuration
│   ├── main.py              # FastAPI application
│   └── schemas.py           # Pydantic models
├── client/                  # Client applications
│   ├── bot.py               # Bot client
│   └── console.py           # Console client
├── resources/               # Resources
│   ├── porcupine_params_zh.pv # Porcupine model
│   └── 豆豆_zh_mac_v4_0_0.ppn  # Custom wake word
├── tests/                   # Tests
│   ├── test_asr.py          # ASR tests
│   ├── test_chain.py        # Chain tests
│   ├── test_tts.py          # TTS tests
│   └── test_xiaomi_power.py # Xiaomi power tests
├── .env                     # Environment variables
├── .env.example             # Environment template
├── .gitignore               # Git ignore file
├── Dockerfile               # Dockerfile
├── README.md               # This file
├── docker-compose.yml       # Docker Compose file
├── pyproject.toml           # Project configuration
├── requirements.txt         # Dependencies
└── setup.py                 # Setup script
```

## Configuration

Key environment variables:

### OpenAI Configuration
- `OPENAI_API_KEY`: Required for AI functionality
- `OPENAI_MODEL`: AI model to use (default: gpt-3.5-turbo)
- `OPENAI_TEMPERATURE`: Response creativity (0.0-1.0)
- `OPENAI_MAX_TOKENS`: Maximum response length

### Aliyun Configuration
- `ALIYUN_ACCESS_KEY_ID`: Alibaba Cloud access key ID
- `ALIYUN_ACCESS_KEY_SECRET`: Alibaba Cloud access key secret
- `ALIYUN_REGION_ID`: Alibaba Cloud region (default: cn-shanghai)
- `ALIYUN_ASR_APP_KEY`: Aliyun ASR application key
- `ALIYUN_ASR_ENABLE`: Enable Aliyun ASR service

### Audio Configuration
- `AUDIO_SAMPLE_RATE`: Audio processing sample rate (16000)
- `AUDIO_CHANNELS`: Audio channels (1)
- `AUDIO_CHUNK_SIZE`: Audio chunk size (1024)
- `UPLOAD_DIR`: Directory for file uploads

### System Configuration
- `LANGCHAIN_VERBOSE`: Enable verbose logging
- `MAX_UPLOAD_SIZE`: Maximum file upload size (10MB)

## Voice Features

### Speech-to-Text (ASR)
- **Aliyun ASR Only**: Professional Chinese speech recognition with high accuracy
- **File Recognition**: Support for WAV, MP3, FLAC audio formats
- **Real-time Microphone**: Direct microphone recording and recognition
- **Continuous Recording**: Advanced microphone with silence detection
- **Cloud-based Processing**: No local dependencies, reduced complexity

### Text-to-Speech (TTS)
- **Aliyun TTS**: Professional Chinese speech synthesis
- **Multiple Voices**: Support for xiaoyun, xiaoya, xiaowang, xiaomeng, xiaoxiao, xiaochen
- **High Quality**: 16kHz sample rate, WAV/MP3 output formats
- **Cloud-based Processing**: Consistent quality across platforms

### Aliyun ASR Setup (Required)

1. **Create Alibaba Cloud Account**
   ```bash
   # Get credentials from Alibaba Cloud console
   # 1. Go to AccessKey Management
   # 2. Create AccessKey ID and Secret
   # 3. Enable NLS (Natural Language Service)
   # 4. Create ASR application and get AppKey
   ```

2. **Configure Environment**
   ```bash
   export ALIYUN_ACCESS_KEY="your_access_key_id"
   export ALIYUN_ACCESS_KEY_SECRET="your_access_key_secret"
   export ALIYUN_ASR_APP_KEY="your_asr_app_key"
   export ALIYUN_ASR_ENABLE=true
   ```

3. **Install Dependencies**
   ```bash
   python fix_dependencies.py
   ```

4. **Test Services**
   ```bash
   # Test file recognition
   curl -X POST "http://localhost:8000/api/v1/voice/recognize-file" \
        -F "file=@test.wav" \
        -F "engine=aliyun"
   
   # Test microphone recognition
   curl -X POST "http://localhost:8000/api/v1/voice/recognize-microphone" \
        -F "engine=aliyun" \
        -F "duration=5.0"
   
   # Test continuous recognition
   curl -X POST "http://localhost:8000/api/v1/voice/recognize-microphone-continuous" \
        -F "engine=aliyun" \
        -F "timeout=10.0"
   
   # Test TTS synthesis
   curl -X POST "http://localhost:8000/api/v1/voice/tts/synthesize" \
        -F "text=你好，欢迎使用阿里云语音服务" \
        -F "voice=xiaoyun" \
        -F "save_to_file=true"
   
   # Get TTS info
   curl "http://localhost:8000/api/v1/voice/tts/info"
   ```

2. **Configure Environment**
   ```bash
   export ALIYUN_ACCESS_KEY="your_access_key_id"
   export ALIYUN_ACCESS_KEY_SECRET="your_access_key_secret"
   export ALIYUN_ASR_APP_KEY="your_asr_app_key"
   export ALIYUN_ASR_ENABLE=true
   ```

3. **Test the Service**
   ```bash
   # Upload audio file for testing
   curl -X POST "http://localhost:8000/api/v1/voice/recognize-file" \
        -F "file=@test.wav" \
        -F "engine=aliyun"
   ```

## Docker

Build and run with Docker:

```bash
# Build
docker build -t anybot .

# Run
docker run -p 8000:8000 --env-file .env anybot
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run quality checks
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions, please create an issue in the repository.