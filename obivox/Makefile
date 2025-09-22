# OBIVox Master Build Pipeline
# Polyglot system supporting C, Rust, and FFI integration

PROJECT := obivox
VERSION := 1.0.0
BUILD_DIR := build
TARGET_PLATFORMS := linux macos windows bsd

# Compiler settings
CC := gcc
RUSTC := rustc
CARGO := cargo
NASM := nasm

# FFmpeg configuration
FFMPEG_LIBS := -lavformat -lavcodec -lavutil -lswresample -lswscale
FFMPEG_CFLAGS := $(shell pkg-config --cflags libavformat libavcodec)

# Platform detection
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    PLATFORM := linux
    SO_EXT := .so
    LDFLAGS := -shared -fPIC
endif
ifeq ($(UNAME_S),Darwin)
    PLATFORM := macos
    SO_EXT := .dylib
    LDFLAGS := -dynamiclib
endif
ifeq ($(findstring MINGW,$(UNAME_S)),MINGW)
    PLATFORM := windows
    SO_EXT := .dll
    LDFLAGS := -shared
endif

# Core components
CORE_SOURCES := \
    src/core/obivox_engine.c \
    src/ffmpeg/ffmpeg_pipeline.c \
    src/nlm/phonetic_analyzer.c \
    src/nlm/bottom_up_processor.c \
    src/nlm/top_down_processor.c \
    src/elf/obielf_linker.c

RUST_SOURCES := \
    src/rust/lib.rs \
    src/rust/engine.rs \
    src/rust/plugins.rs \
    src/rust/ffi.rs

# Build targets
.PHONY: all clean test install package

all: $(BUILD_DIR)/libobivox$(SO_EXT) $(BUILD_DIR)/obivox-cli plugins

# Core C library
$(BUILD_DIR)/libobivox$(SO_EXT): $(CORE_SOURCES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(LDFLAGS) $(FFMPEG_CFLAGS) -O3 -Wall -o $@ $^ $(FFMPEG_LIBS)
	@echo "✓ Built core OBIVox library"

# Rust components
$(BUILD_DIR)/libobivox_rust.a: $(RUST_SOURCES)
	@mkdir -p $(BUILD_DIR)
	cd src/rust && $(CARGO) build --release
	cp target/release/libobivox_rust.a $(BUILD_DIR)/
	@echo "✓ Built Rust components"

# CLI tool with --obiai flag support
$(BUILD_DIR)/obivox-cli: src/cli/main.c $(BUILD_DIR)/libobivox$(SO_EXT)
	$(CC) -o $@ $< -L$(BUILD_DIR) -lobivox -lpthread
	@echo "✓ Built OBIVox CLI"

# Plugin system
plugins: whisper-plugin coqui-plugin

whisper-plugin:
	@mkdir -p $(BUILD_DIR)/plugins
	$(CC) $(LDFLAGS) -o $(BUILD_DIR)/plugins/whisper$(SO_EXT) \
		src/plugins/whisper/whisper_wrapper.c -lwhisper
	@echo "✓ Built Whisper plugin"

coqui-plugin:
	@mkdir -p $(BUILD_DIR)/plugins
	$(CC) $(LDFLAGS) -o $(BUILD_DIR)/plugins/coqui$(SO_EXT) \
		src/plugins/coqui/coqui_wrapper.c -lcoqui
	@echo "✓ Built Coqui TTS plugin"

# OBIELF integration
obielf-modules:
	$(NASM) -f elf64 src/elf/codec_loader.asm -o $(BUILD_DIR)/codec_loader.o
	$(LD) -o $(BUILD_DIR)/codec_loader.elf $(BUILD_DIR)/codec_loader.o
	@echo "✓ Built OBIELF codec modules"

# Platform packages
package-linux:
	@mkdir -p packages/deb/DEBIAN
	@mkdir -p packages/deb/usr/bin
	@mkdir -p packages/deb/usr/lib
	cp $(BUILD_DIR)/obivox-cli packages/deb/usr/bin/
	cp $(BUILD_DIR)/libobivox.so packages/deb/usr/lib/
	echo "Package: obivox" > packages/deb/DEBIAN/control
	echo "Version: $(VERSION)" >> packages/deb/DEBIAN/control
	echo "Architecture: amd64" >> packages/deb/DEBIAN/control
	echo "Maintainer: OBINexus <dev@obinexus.org>" >> packages/deb/DEBIAN/control
	echo "Description: Bidirectional audio-text processing system" >> packages/deb/DEBIAN/control
	dpkg-deb --build packages/deb obivox_$(VERSION)_amd64.deb
	@echo "✓ Created .deb package"

package-macos:
	@mkdir -p packages/macos/OBIVox.app/Contents/MacOS
	@mkdir -p packages/macos/OBIVox.app/Contents/Frameworks
	cp $(BUILD_DIR)/obivox-cli packages/macos/OBIVox.app/Contents/MacOS/
	cp $(BUILD_DIR)/libobivox.dylib packages/macos/OBIVox.app/Contents/Frameworks/
	cp resources/Info.plist packages/macos/OBIVox.app/Contents/
	hdiutil create -volname OBIVox -srcfolder packages/macos/OBIVox.app OBIVox-$(VERSION).dmg
	@echo "✓ Created .dmg package"

package-windows:
	@mkdir -p packages/windows
	cp $(BUILD_DIR)/obivox-cli.exe packages/windows/
	cp $(BUILD_DIR)/obivox.dll packages/windows/
	candle.exe -o packages/windows/obivox.wixobj resources/installer.wxs
	light.exe -o OBIVox-$(VERSION).msi packages/windows/obivox.wixobj
	@echo "✓ Created .msi installer"

# Test suite
test: test-unit test-integration test-codecs

test-unit:
	$(CC) -o $(BUILD_DIR)/test_unit tests/unit/*.c -L$(BUILD_DIR) -lobivox
	$(BUILD_DIR)/test_unit
	@echo "✓ Unit tests passed"

test-integration:
	python3 tests/integration/test_pipeline.py
	@echo "✓ Integration tests passed"

test-codecs:
	@for codec in whisper coqui; do \
		$(BUILD_DIR)/obivox-cli --test-codec $$codec && \
		echo "✓ $$codec codec test passed" || exit 1; \
	done

# Installation
install:
ifeq ($(PLATFORM),linux)
	sudo cp $(BUILD_DIR)/obivox-cli /usr/local/bin/
	sudo cp $(BUILD_DIR)/libobivox.so /usr/local/lib/
	sudo ldconfig
endif
ifeq ($(PLATFORM),macos)
	cp $(BUILD_DIR)/obivox-cli /usr/local/bin/
	cp $(BUILD_DIR)/libobivox.dylib /usr/local/lib/
endif
	@echo "✓ OBIVox installed successfully"

# Docker build for cross-platform
docker-build:
	docker build -t obivox:$(VERSION) .
	@echo "✓ Docker image built"

# Clean
clean:
	rm -rf $(BUILD_DIR) packages
	cd src/rust && $(CARGO) clean
	@echo "✓ Cleaned build artifacts"

# Development helpers
dev-setup:
	pip install -r requirements.txt
	cargo install cargo-watch
	@echo "✓ Development environment ready"

watch:
	cargo watch -x "build --release" -w src/rust

# Documentation
docs:
	doxygen Doxyfile
	cd docs && mkdocs build
	@echo "✓ Documentation generated"

.DEFAULT_GOAL := all