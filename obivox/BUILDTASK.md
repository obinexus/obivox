# OBIVox Polyglot System - Complete Build & Deployment Guide

## System Overview

OBIVox is a consciousness-preserving bidirectional audio-text processing system that integrates:
- **NLM Framework**: Nsibidi Language Model with XYZ coordinate mapping
- **NLM-Atlas**: Geomorphic service discovery with adaptive tree balancing
- **OBIAI**: Data drift mitigation with 95.4% coherence threshold
- **Speech Variation Handling**: Lisp mitigation, stutter detection, accent preservation
- **Human-in-the-Loop**: Confirmation requests when confidence < 85%

## Complete Directory Structure

```bash
obivox/
├── include/obivox/
│   ├── core.h                    # Core API definitions
│   ├── tts/
│   │   ├── synthesis.h           # TTS interfaces
│   │   └── voice/
│   │       └── profiles.h        # Voice customization
│   ├── stt/
│   │   ├── recognition.h         # STT interfaces  
│   │   └── models/
│   │       └── whisper.h         # Whisper integration
│   ├── nlm/
│   │   ├── framework.h           # NLM Framework API
│   │   ├── nsibidi.h            # Nsibidi Language Model
│   │   └── atlas.h              # NLM-Atlas geomorphic schema
│   ├── codecs/
│   │   ├── audio/
│   │   │   ├── h264.h           # H.264 codec
│   │   │   ├── mp3.h            # MP3 codec
│   │   │   └── m4a.h            # M4A codec
│   │   └── compression/
│   │       └── hamming.h        # Hamming error correction
│   └── elf/
│       ├── loader.h             # OBIELF loader
│       └── linker.h             # Dynamic linking
├── src/
│   ├── core/
│   │   ├── engine/
│   │   │   ├── obivox_engine.c
│   │   │   └── obivox_nlm_core.c  # NLM integration
│   │   ├── utils/
│   │   └── memory/
│   ├── codecs/
│   │   ├── whisper/
│   │   │   └── whisper_codec.c
│   │   ├── coqui/
│   │   │   └── coqui_codec.c
│   │   ├── h264/
│   │   │   └── h264_codec.c
│   │   └── hamming/
│   │       └── hamming_elf.c
│   ├── nlm/
│   │   ├── bottom_up/
│   │   │   └── acoustic_processor.c
│   │   ├── top_down/
│   │   │   └── semantic_analyzer.c
│   │   └── phonetic/
│   │       ├── variation_detector.c
│   │       └── lisp_mitigation.c
│   ├── ffi/
│   │   ├── python_binding.c
│   │   ├── rust_binding.c
│   │   └── node_binding.c
│   └── elf/
│       ├── loader/
│       │   └── obielf_loader.c
│       └── linker/
│           └── dynamic_linker.c
├── plugins/
│   ├── linux/
│   │   ├── x86_64/
│   │   │   └── obivox.so
│   │   └── Makefile
│   ├── macos/
│   │   ├── universal/
│   │   │   └── obivox.dylib
│   │   └── Makefile
│   ├── windows/
│   │   ├── x64/
│   │   │   └── obivox.dll
│   │   └── Makefile.win
│   └── bsd/
│       └── Makefile
├── ffi/
│   ├── python/
│   │   ├── obivox/
│   │   │   ├── __init__.py
│   │   │   ├── nlm.py
│   │   │   └── codecs.py
│   │   └── setup.py
│   ├── rust/
│   │   ├── obivox-sys/
│   │   │   ├── Cargo.toml
│   │   │   └── src/lib.rs
│   │   └── build.rs
│   └── node/
│       ├── lib/
│       │   └── obivox.js
│       └── package.json
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/
│   ├── api/
│   ├── architecture/
│   └── guides/
├── Makefile               # Master build file
├── CMakeLists.txt        # CMake configuration
└── README.md             # This file
```

## Master Makefile

```makefile
# OBIVox Polyglot Build System with NLM Framework
# Supports: Linux, macOS, Windows, BSD
# Integrates: NLM-Atlas, OBIAI, Speech Variation Handling

PROJECT = obivox
VERSION = 1.0.0
NLM_VERSION = 2.0.0

# Compiler settings
CC = gcc
CXX = g++
RUSTC = cargo
PYTHON = python3
NODE = node
NASM = nasm

# Feature flags
CFLAGS = -Wall -O3 -fPIC -DNLM_FRAMEWORK -DOBIAI_DRIFT
CFLAGS += -DSPEECH_VARIATION_HANDLING -DHUMAN_IN_LOOP
CFLAGS += -DEPISTEMIC_THRESHOLD=0.954

# Directories
SRC_DIR = src
INC_DIR = include
BUILD_DIR = build
PLUGIN_DIR = plugins
FFI_DIR = ffi

# Platform detection
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    PLATFORM = linux
    SO_EXT = .so
    LDFLAGS = -shared -fPIC
    AUDIO_BACKEND = -lasound -lpulse
endif
ifeq ($(UNAME_S),Darwin)
    PLATFORM = macos
    SO_EXT = .dylib
    LDFLAGS = -dynamiclib
    AUDIO_BACKEND = -framework CoreAudio
endif
ifeq ($(findstring MINGW,$(UNAME_S)),MINGW)
    PLATFORM = windows
    SO_EXT = .dll
    LDFLAGS = -shared
    AUDIO_BACKEND = -lwinmm
endif
ifeq ($(UNAME_S),FreeBSD)
    PLATFORM = bsd
    SO_EXT = .so
    LDFLAGS = -shared -fPIC
    AUDIO_BACKEND = -loss
endif

# FFmpeg configuration
FFMPEG_LIBS = $(shell pkg-config --libs libavformat libavcodec libavutil libswresample)
FFMPEG_CFLAGS = $(shell pkg-config --cflags libavformat libavcodec)

# Whisper configuration  
WHISPER_LIBS = -lwhisper
WHISPER_CFLAGS = -I/usr/local/include/whisper

# Coqui TTS configuration
COQUI_LIBS = -lcoqui
COQUI_CFLAGS = -I/usr/local/include/coqui

# Source files
CORE_SRCS = $(wildcard $(SRC_DIR)/core/**/*.c)
NLM_SRCS = $(wildcard $(SRC_DIR)/nlm/**/*.c)
CODEC_SRCS = $(wildcard $(SRC_DIR)/codecs/**/*.c)
ELF_SRCS = $(wildcard $(SRC_DIR)/elf/**/*.c)
FFI_SRCS = $(wildcard $(SRC_DIR)/ffi/*.c)

ALL_SRCS = $(CORE_SRCS) $(NLM_SRCS) $(CODEC_SRCS) $(ELF_SRCS)

# Object files
OBJS = $(ALL_SRCS:$(SRC_DIR)/%.c=$(BUILD_DIR)/%.o)

# Final compilation flags
CFLAGS += -I$(INC_DIR) $(FFMPEG_CFLAGS) $(WHISPER_CFLAGS) $(COQUI_CFLAGS)
LDFLAGS += $(FFMPEG_LIBS) $(WHISPER_LIBS) $(COQUI_LIBS) $(AUDIO_BACKEND) -lpthread -lm

# Default target
all: directories core plugins ffi test

# Create directory structure
directories:
	@mkdir -p $(BUILD_DIR)/{core,nlm,codecs,elf,ffi}
	@mkdir -p $(BUILD_DIR)/{core/engine,core/utils,core/memory}
	@mkdir -p $(BUILD_DIR)/{nlm/bottom_up,nlm/top_down,nlm/phonetic}
	@mkdir -p $(BUILD_DIR)/{codecs/whisper,codecs/coqui,codecs/h264}
	@mkdir -p $(BUILD_DIR)/{elf/loader,elf/linker}

# Core library
core: $(BUILD_DIR)/libobivox$(SO_EXT)

$(BUILD_DIR)/libobivox$(SO_EXT): $(OBJS)
	@echo "Building core OBIVox library with NLM Framework..."
	$(CC) $(LDFLAGS) -o $@ $^
	@echo "✓ Core library built: $@"

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c -o $@ $<

# Platform-specific plugins
plugins: $(PLUGIN_DIR)/$(PLATFORM)/obivox$(SO_EXT)

$(PLUGIN_DIR)/$(PLATFORM)/obivox$(SO_EXT): $(BUILD_DIR)/libobivox$(SO_EXT)
	@echo "Building $(PLATFORM) plugin..."
	@mkdir -p $(PLUGIN_DIR)/$(PLATFORM)
	cp $< $@
	@echo "✓ $(PLATFORM) plugin built"

# FFI Bindings
ffi: python-ffi rust-ffi node-ffi

python-ffi:
	@echo "Building Python bindings..."
	cd $(FFI_DIR)/python && $(PYTHON) setup.py build_ext --inplace
	@echo "✓ Python bindings built"

rust-ffi:
	@echo "Building Rust bindings..."
	cd $(FFI_DIR)/rust/obivox-sys && $(CARGO) build --release
	@echo "✓ Rust bindings built"

node-ffi:
	@echo "Building Node.js bindings..."
	cd $(FFI_DIR)/node && npm install && npm run build
	@echo "✓ Node.js bindings built"

# Testing
test: unit-test integration-test codec-test

unit-test:
	@echo "Running unit tests..."
	$(CC) -o $(BUILD_DIR)/test_unit tests/unit/*.c -L$(BUILD_DIR) -lobivox
	$(BUILD_DIR)/test_unit
	@echo "✓ Unit tests passed"

integration-test:
	@echo "Running integration tests..."
	$(PYTHON) tests/integration/test_nlm_integration.py
	@echo "✓ Integration tests passed"

codec-test:
	@echo "Testing codec conversions..."
	@$(BUILD_DIR)/obivox-cli --test-codec whisper
	@$(BUILD_DIR)/obivox-cli --test-codec coqui
	@echo "✓ Codec tests passed"

# Installation
install:
	@echo "Installing OBIVox..."
ifeq ($(PLATFORM),linux)
	sudo cp $(BUILD_DIR)/libobivox.so /usr/local/lib/
	sudo cp -r $(INC_DIR)/obivox /usr/local/include/
	sudo ldconfig
else ifeq ($(PLATFORM),macos)
	cp $(BUILD_DIR)/libobivox.dylib /usr/local/lib/
	cp -r $(INC_DIR)/obivox /usr/local/include/
else ifeq ($(PLATFORM),bsd)
	sudo cp $(BUILD_DIR)/libobivox.so /usr/local/lib/
	sudo cp -r $(INC_DIR)/obivox /usr/local/include/
endif
	@echo "✓ Installation complete"

# Package generation
package: package-$(PLATFORM)

package-linux:
	@echo "Creating .deb package..."
	dpkg-buildpackage -b -uc
	@echo "✓ .deb package created"

package-macos:
	@echo "Creating .dmg package..."
	hdiutil create -volname OBIVox -srcfolder $(BUILD_DIR) OBIVox-$(VERSION).dmg
	@echo "✓ .dmg package created"

package-windows:
	@echo "Creating .msi installer..."
	candle.exe obivox.wxs
	light.exe -out OBIVox-$(VERSION).msi obivox.wixobj
	@echo "✓ .msi installer created"

package-bsd:
	@echo "Creating .pkg package..."
	pkg create -M +MANIFEST -r $(BUILD_DIR) -o obivox-$(VERSION).pkg
	@echo "✓ .pkg package created"

# Docker support
docker:
	docker build -t obivox:$(VERSION) .
	@echo "✓ Docker image built"

# Clean
clean:
	rm -rf $(BUILD_DIR)
	rm -rf $(PLUGIN_DIR)/*/obivox*
	cd $(FFI_DIR)/rust/obivox-sys && $(CARGO) clean
	@echo "✓ Build artifacts cleaned"

# Help
help:
	@echo "OBIVox Build System - Available targets:"
	@echo "  all           - Build everything"
	@echo "  core          - Build core library"
	@echo "  plugins       - Build platform plugins"
	@echo "  ffi           - Build all FFI bindings"
	@echo "  test          - Run all tests"
	@echo "  install       - Install system-wide"
	@echo "  package       - Create platform package"
	@echo "  docker        - Build Docker image"
	@echo "  clean         - Remove build artifacts"
	@echo ""
	@echo "Platform: $(PLATFORM)"
	@echo "Version: $(VERSION)"

.PHONY: all directories core plugins ffi test install package clean help
```

## Usage Examples

### Basic Usage

```bash
# Build the complete system
make all

# Convert audio with speech variation handling
obivox --input lecture_with_lisp.mp4 \
       --output transcript.txt \
       --nlm-mode adaptive \
       --preserve-accent 0.7 \
       --confidence-threshold 0.954

# Bidirectional conversion
obivox --bidirectional input.mp3 output.txt output_synthesized.wav

# With human-in-the-loop
obivox --input unclear_audio.m4a \
       --human-confirm \
       --min-confidence 0.85
```

### Python Integration

```python
import obivox

# Initialize with NLM framework
system = obivox.NLMSystem(
    coherence_threshold=0.954,
    enable_variations=True
)

# Process with speech variation handling
result = system.process_audio(
    "lecture.mp4",
    preserve_accent=0.7,
    mitigate_lisp=True
)

print(f"Transcription: {result.text}")
print(f"Confidence: {result.confidence}")
print(f"NLM Position: {result.nlm_coordinates}")
```

### Rust Integration

```rust
use obivox_sys::{OBIVoxSystem, NLMCoordinate};

fn main() {
    let mut system = OBIVoxSystem::new(0.954).unwrap();
    
    // Process with drift detection
    let result = system.process_bidirectional(
        "input.mp3",
        obivox::InputType::Audio
    ).unwrap();
    
    if result.confidence < 0.85 {
        // Request human validation
        system.request_human_feedback(&result);
    }
}
```

## Deployment

### Linux

```bash
# Install dependencies
sudo apt-get install libavformat-dev libavcodec-dev libwhisper-dev

# Build and install
make && sudo make install

# Create systemd service
sudo cp obivox.service /etc/systemd/system/
sudo systemctl enable obivox
```

### macOS

```bash
# Install dependencies
brew install ffmpeg whisper coqui-tts

# Build and package
make && make package-macos
```

### Windows

```powershell
# Build with Visual Studio
msbuild OBIVox.sln /p:Configuration=Release

# Create installer
make package-windows
```

## Testing

```bash
# Run complete test suite
make test

# Test speech variation handling
./test_variations.sh samples/lisp_speech.wav

# Test NLM coordinate mapping
python tests/test_nlm_mapping.py

# Test OBIAI drift detection
./test_drift_mitigation --drift-level 0.4
```

## Performance Metrics

- **STT Latency**: < 500ms (with variation handling)
- **TTS Latency**: < 200ms
- **Coherence Maintenance**: 95.4% under drift
- **Memory Usage**: < 512MB
- **CPU Cores**: 4-8 threads
- **Speech Variation Detection**: > 90% accuracy

## Contributing

See CONTRIBUTING.md for guidelines on:
- Code style
- Testing requirements
- Documentation standards
- Pull request process

## License

OBINexus NT Open Access License (MIT-based)
See LICENSE.md for full terms.

## Support

- GitHub Issues: github.com/obinexus/obivox/issues
- Documentation: docs.obinexus.org/obivox
- Email: support@obinexus.org

---

*Computing from the Heart. Building with Purpose. Running with Heart.*