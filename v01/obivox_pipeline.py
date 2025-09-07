#!/usr/bin/env python3
"""
OBIVox SST -> TTS prototype
m4a/mp3 -> text -> synthetic m4a
"""

import sys
import subprocess
import whisper
from TTS.api import TTS
from pathlib import Path

def convert_to_wav(infile: Path) -> Path:
    wavfile = infile.with_suffix(".wav")
    subprocess.run([
        "ffmpeg", "-y", "-i", str(infile),
        "-ar", "16000", "-ac", "1", str(wavfile)
    ], check=True)
    return wavfile

def transcribe_audio(wavfile: Path) -> str:
    model = whisper.load_model("base")  # pick "small"/"medium" if GPU is decent
    result = model.transcribe(str(wavfile))
    return result["text"].strip()

def synthesize_speech(text: str, outfile: Path):
    tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
    tts.tts_to_file(text=text, file_path=str(outfile.with_suffix(".wav")))
    # convert wav -> m4a
    subprocess.run([
        "ffmpeg", "-y", "-i", str(outfile.with_suffix(".wav")),
        str(outfile.with_suffix(".m4a"))
    ], check=True)

def main():
    if len(sys.argv) < 2:
        print("Usage: python obivox_pipeline.py input_audio.m4a|.mp3")
        sys.exit(1)

    infile = Path(sys.argv[1])
    wavfile = convert_to_wav(infile)
    text = transcribe_audio(wavfile)
    print("Transcription:", text)

    outfile = infile.parent / (infile.stem + "_revoiced")
    synthesize_speech(text, outfile)
    print("Output saved as:", outfile.with_suffix(".m4a"))

if __name__ == "__main__":
    main()
