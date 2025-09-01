# OBIVox

**Bidirectional Knowledge Interface for Real-Time Learning**
Transform lectures, podcasts, and conversations into interactive knowledge sessions. OBIVox bridges the gap between spoken content and instant comprehension through intelligent audio processing.

## 🎯 What is OBIVox?

OBIVox is a thread-safe, bidirectional pipeline that converts between audio and text in real-time. Built for learners, researchers, and knowledge workers who need to:

- **Capture** spoken lectures and convert them to searchable text
- **Query** content through natural language
- **Generate** audio explanations from written material
- **Navigate** complex topics with instant audio/text switching

## 🚀 Key Features

### Thread-Safe Architecture
- Parent-child task trees for complex workflows
- Non-blocking concurrent processing
- Safety checks with confidence thresholds
- Graceful error handling and fallbacks

### Multi-Format Support
- WAV and MP4 audio input
- Automatic format conversion via FFmpeg
- Configurable sample rates and channels
- Extensible to other media formats

### Intelligent Processing
- Confidence-based verification
- User confirmation for low-confidence results
- Modular ASR/TTS backend support
- Ready for Whisper, VOSK, Coqui TTS integration

## 📚 Use Cases

**Lecture Capture**: Record entire lectures and get instant transcripts with timestamp mapping.

**Study Sessions**: Convert textbooks to audio for passive learning while commuting.

**Research Notes**: Dictate research observations and get formatted, searchable text.

**Knowledge Synthesis**: Feed in multiple sources and generate cohesive audio summaries.

## 🛠️ Installation

```bash
# Clone repository
git clone https://github.com/yourusername/obivox.git
cd obivox

# Create virtual environment (Python 3.10 recommended)
conda create -n obivox python=3.10
conda activate obivox

# Install dependencies
pip install -r requirements.txt

# Install system dependencies
sudo apt-get install ffmpeg portaudio19-dev  # Ubuntu/Debian
# brew install ffmpeg portaudio              # macOS
```

## 💡 Quick Start

```python
# Basic usage
python main.py lecture_recording.mp4

# The system will:
# 1. Extract audio from MP4
# 2. Transcribe speech to text
# 3. Verify transcription quality
# 4. Generate audio feedback
```

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Audio In   │────▶│  STT Worker  │────▶│   Text Out  │
│ (WAV/MP4)   │     │  (Whisper)   │     │  (Indexed)  │
└─────────────┘     └──────────────┘     └─────────────┘
                            │
                    ┌───────▼────────┐
                    │  Orchestrator  │
                    │  (Thread Pool) │
                    └───────┬────────┘
                            │
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Text In    │────▶│  TTS Worker  │────▶│  Audio Out  │
│ (Query/Doc) │     │ (Coqui/VITS) │     │   (WAV)     │
└─────────────┘     └──────────────┘     └─────────────┘
```

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Worker threads
MAX_WORKERS = 4

# Confidence thresholds
ASR_CONFIDENCE_THRESHOLD = 0.60

# Output directories
WORKDIR = "work"
TTS_OUTPUT_DIR = "work/tts_out"

# Model selection
ASR_MODEL = "whisper"  # or "vosk", "wav2vec2"
TTS_MODEL = "coqui"    # or "vits", "tacotron2"
```

## 🧪 Advanced Usage

### Custom Task Trees

```python
# Create complex workflows
root = TaskNode(id="lecture_process", kind="composite")
root.add_child(TaskNode(id="transcribe", kind="stt", payload=audio_path))
root.add_child(TaskNode(id="summarize", kind="llm", payload=transcription))
root.add_child(TaskNode(id="vocalize", kind="tts", payload=summary))
```

### Batch Processing

```python
# Process entire lecture series
for lecture in Path("lectures/").glob("*.mp4"):
    process_lecture(lecture, output_dir="transcripts/")
```

## 🎓 Learning Enhancement Features (Roadmap)

- [ ] Real-time keyword highlighting
- [ ] Automatic chapter detection
- [ ] Multi-speaker diarization
- [ ] Knowledge graph generation
- [ ] Flashcard creation from transcripts
- [ ] Speed-adjustable playback
- [ ] Language translation pipeline

## 🤝 Contributing

We welcome contributions! Areas of interest:

- Additional ASR/TTS model integrations
- Performance optimizations
- UI/UX improvements
- Educational feature plugins
- Documentation and tutorials

## 📄 License

MIT License - See LICENSE file for details

## 🌟 Acknowledgments

Built on the shoulders of giants:
- OpenAI Whisper for robust ASR
- Coqui TTS for natural speech synthesis
- FFmpeg for media handling
- The open-source ML community

---

**"All the knowledge of any topic at your fingertips"** - Transform how you learn, one conversation at a time.
