#!/usr/bin/env python3
"""
main.py - OBIVox: thread-safe bidirectional STT <-> TTS pipeline skeleton.

Features:
- Accept WAV or MP4 input (MP4 audio extracted via ffmpeg)
- Thread-safe task tree: parent -> children -> join results
- Worker thread pool for STT and TTS
- Safety checks: confidence threshold, explicit confirmation
- Clear replace-points for real ASR/TTS model calls
"""

import os
import subprocess
import uuid
import wave
import threading
import queue
import shutil
from concurrent.futures import ThreadPoolExecutor, Future, wait
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict


# ---------------------------
# Configuration / constants
# ---------------------------

WORKDIR = "work"
os.makedirs(WORKDIR, exist_ok=True)

# For Production 
# from TTS.api import TTS
# tts = TTS(model_name="tts_models/en/ljspeech/glow-tts")
# tts.tts_to_file(text=text, file_path=out_path)

# import whisper
# model = whisper.load_model("small")
# result = model.transcribe(wav_path)
#text = result["text"]
# confidence: if model doesn't provide, compute a proxy, or run n-best



MAX_WORKERS = 4
ASR_CONFIDENCE_THRESHOLD = 0.60  # if model gives confidence lower than this -> fallback
TTS_OUTPUT_DIR = os.path.join(WORKDIR, "tts_out")
os.makedirs(TTS_OUTPUT_DIR, exist_ok=True)


# ---------------------------
# Utilities
# ---------------------------
def extract_audio_from_mp4(mp4_path: str, out_wav: str) -> None:
    """Use ffmpeg to extract audio to wav (mono, 16k). Requires ffmpeg installed."""
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg not found on PATH. Install ffmpeg.")
    cmd = [
        "ffmpeg", "-y", "-i", mp4_path,
        "-vn", "-ac", "1", "-ar", "16000",
        "-f", "wav", out_wav
    ]
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def ensure_wav(input_path: str) -> str:
    """If mp4 -> extract, if wav -> return. Output file path returned."""
    ext = os.path.splitext(input_path)[1].lower()
    if ext in (".wav",):
        return input_path
    out_wav = os.path.join(WORKDIR, f"{uuid.uuid4().hex}.wav")
    extract_audio_from_mp4(input_path, out_wav)
    return out_wav


# ---------------------------
# Task tree (parent-child)
# ---------------------------
@dataclass
class TaskResult:
    ok: bool
    text: Optional[str] = None
    confidence: Optional[float] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskNode:
    id: str
    kind: str               # "stt" or "tts" or "composite" etc.
    payload: Any            # e.g., wav path or text
    parent: Optional["TaskNode"] = None
    children: List["TaskNode"] = field(default_factory=list)
    result: Optional[TaskResult] = None
    lock: threading.Lock = field(default_factory=threading.Lock)
    completed: threading.Event = field(default_factory=threading.Event)

    def add_child(self, child: "TaskNode"):
        with self.lock:
            child.parent = self
            self.children.append(child)

    def set_result(self, result: TaskResult):
        with self.lock:
            self.result = result
            self.completed.set()

    def wait(self, timeout=None):
        self.completed.wait(timeout=timeout)
        return self.result


# ---------------------------
# Replaceable model hooks
# ---------------------------
def asr_transcribe_wav(wav_path: str) -> TaskResult:
    """
    Replace this stub with a real ASR call (Whisper / VOSK / other).
    Return TaskResult.ok True/False, text, confidence in [0,1].
    """
    # ======= STUB (mock) =======
    # For demonstration, pretend we transcribed something.
    fake_text = f"[mock transcription of {os.path.basename(wav_path)}]"
    fake_conf = 0.95
    return TaskResult(ok=True, text=fake_text, confidence=fake_conf)
    # ======= END STUB =======


def tts_synthesize_to_wav(text: str, out_path: str) -> TaskResult:
    """
    Replace this stub with a real TTS call (Coqui TTS / VITS / other).
    Synthesize text to out_path (wav) and return TaskResult with metadata.
    """
    # ======= STUB (mock) =======
    # Generate a silent WAV of 1s to act as placeholder.
    with wave.open(out_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00\x00" * 16000)
    return TaskResult(ok=True, text=text, confidence=1.0, extra={"out": out_path})
    # ======= END STUB =======


# ---------------------------
# Safety / verification helpers
# ---------------------------
def safety_check_asr(result: TaskResult) -> bool:
    """Return True if safe to proceed (confidence high enough)."""
    if result.confidence is None:
        return False
    return result.confidence >= ASR_CONFIDENCE_THRESHOLD


def require_user_confirmation(prompt_text: str) -> bool:
    """
    In a headless server you'd implement a UI/telegram/email confirmation flow.
    For now, console prompt (blocking) for safety-critical operations.
    """
    resp = input(f"Confirm action? {prompt_text} (y/N): ").strip().lower()
    return resp in ("y", "yes")


# ---------------------------
# Worker functions
# ---------------------------
def worker_stt(node: TaskNode) -> TaskResult:
    wav_path = node.payload
    try:
        result = asr_transcribe_wav(wav_path)
    except Exception as e:
        return TaskResult(ok=False, text=None, confidence=0.0, extra={"error": str(e)})
    node.set_result(result)
    return result


def worker_tts(node: TaskNode) -> TaskResult:
    text = node.payload
    out_wav = os.path.join(TTS_OUTPUT_DIR, f"{node.id}.wav")
    try:
        result = tts_synthesize_to_wav(text, out_wav)
    except Exception as e:
        return TaskResult(ok=False, text=None, confidence=0.0, extra={"error": str(e)})
    node.set_result(result)
    return result


# ---------------------------
# Orchestration layer
# ---------------------------
class Orchestrator:
    def __init__(self, max_workers=MAX_WORKERS):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.futures: List[Future] = []
        self.root_tasks: List[TaskNode] = []
        self.shutdown_event = threading.Event()

    def submit_task(self, node: TaskNode) -> Future:
        if node.kind == "stt":
            fut = self.executor.submit(worker_stt, node)
        elif node.kind == "tts":
            fut = self.executor.submit(worker_tts, node)
        else:
            # For composite nodes handle in-line or via separate worker
            fut = self.executor.submit(self._handle_composite, node)
        self.futures.append(fut)
        return fut

    def _handle_composite(self, node: TaskNode) -> TaskResult:
        """
        Example composite: parent receives WAV -> STT -> spawn TTS child -> collect.
        This shows parent-child spawn and join logic.
        """
        # parent expects payload = wav_path
        wav_path = node.payload
        stt_child = TaskNode(id=f"{node.id}.stt", kind="stt", payload=wav_path, parent=node)
        node.add_child(stt_child)
        stt_fut = self.submit_task(stt_child)
        # Wait for STT
        stt_res = stt_child.wait()
        if not stt_res or not stt_res.ok:
            node.set_result(TaskResult(ok=False, extra={"reason": "stt_failed"}))
            return node.result
        # Safety check
        if not safety_check_asr(stt_res):
            # Low confidence: ask for confirmation / fallback
            confirmed = require_user_confirmation(f"Low confidence ({stt_res.confidence:.2f}) for text: {stt_res.text}")
            if not confirmed:
                node.set_result(TaskResult(ok=False, extra={"reason": "user_rejected_low_conf"}))
                return node.result
        # Spawn TTS child to speak back the transcription
        tts_child = TaskNode(id=f"{node.id}.tts", kind="tts", payload=stt_res.text, parent=node)
        node.add_child(tts_child)
        tts_fut = self.submit_task(tts_child)
        # Wait for TTS
        tts_res = tts_child.wait()
        if not tts_res or not tts_res.ok:
            node.set_result(TaskResult(ok=False, extra={"reason": "tts_failed"}))
            return node.result
        # Compose final result
        node.set_result(TaskResult(ok=True, text=stt_res.text, confidence=stt_res.confidence, extra={"tts_out": tts_res.extra.get("out")}))
        return node.result

    def shutdown(self):
        self.shutdown_event.set()
        # wait for current futures to complete gracefully
        wait(self.futures, timeout=5.0)
        self.executor.shutdown(wait=True)


# ---------------------------
# Example main flow
# ---------------------------
def main_process(input_path: str):
    orch = Orchestrator(max_workers=4)
    root = TaskNode(id=str(uuid.uuid4()), kind="composite", payload=None)
    orch.root_tasks.append(root)

    # Prepare wav if needed
    wav_path = ensure_wav(input_path)
    root.payload = wav_path

    # Submit composite: does stt -> tts (spawn children)
    fut = orch.submit_task(root)

    # Wait for completion
    result = root.wait(timeout=60)
    if not result:
        print("Timeout or no result.")
    else:
        print("ROOT RESULT:", result)
        if result.ok:
            print("Transcribed text:", result.text)
            print("TTS file:", result.extra.get("tts_out"))

    orch.shutdown()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python main.py <input.wav|input.mp4>")
        sys.exit(1)
    inpath = sys.argv[1]
    main_process(inpath)
