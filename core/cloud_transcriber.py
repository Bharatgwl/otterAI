"""
Cloud-based Whisper transcription using Groq API.

Drop-in replacement for core/transcriber.py — same function signatures.

Advantages over local Whisper:
  ✅ Uses whisper-large-v3 (far more accurate than 'small')
  ✅ Runs on Groq's LPU hardware (extremely fast)
  ✅ Free tier available (https://console.groq.com)
  ✅ No GPU required on your machine

Usage:
  # In test.py, just swap the import:
  # from core.transcriber import transcribe_all       ← local
  from core.cloud_transcriber import transcribe_all    # ← cloud
"""

import os
# pyrefly: ignore [missing-import]
from groq import Groq
from pydub import AudioSegment
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Models: "whisper-large-v3" (best accuracy, supports translate)
#         "whisper-large-v3-turbo" (faster, slightly less accurate)
#         "distil-whisper-large-v3-en" (fastest, English-only)
WHISPER_MODEL = os.getenv("CLOUD_WHISPER_MODEL", "whisper-large-v3-turbo")
TRANSLATE_MODEL = os.getenv("CLOUD_TRANSLATE_MODEL", "whisper-large-v3")
MAX_FILE_SIZE_MB = 25  # Groq's free-tier upload limit

_client = None


def _get_client():
    """Initialize and cache the Groq client."""
    global _client
    if _client is None:
        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY not found. "
                "Add it to your .env file:  GROQ_API_KEY=gsk_..."
            )
        _client = Groq(api_key=GROQ_API_KEY)
        print(f"✅ Groq client ready  (model: {WHISPER_MODEL})")
    return _client




def _compress_for_upload(audio_path: str) -> tuple[str, bool]:
    """
    If the WAV file exceeds Groq's 25 MB limit, compress it to MP3.

    Returns:
        (path_to_upload, was_compressed)
    """
    file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)

    if file_size_mb <= MAX_FILE_SIZE_MB:
        return audio_path, False

    print(
        f"  ⚠ File is {file_size_mb:.1f} MB (limit {MAX_FILE_SIZE_MB} MB). "
        f"Compressing to MP3..."
    )
    audio = AudioSegment.from_file(audio_path)
    compressed_path = audio_path.rsplit(".", 1)[0] + "_compressed.mp3"
    audio.export(compressed_path, format="mp3", bitrate="64k")

    new_size_mb = os.path.getsize(compressed_path) / (1024 * 1024)
    print(f"  ✅ Compressed: {file_size_mb:.1f} MB → {new_size_mb:.1f} MB")
    return compressed_path, True



def transcribe_audio_chunk(chunk_path: str, translate: bool = False) -> str:
    """
    Transcribe a single audio chunk using Groq's cloud Whisper API.

    Args:
        chunk_path (str): Path to the audio chunk file.
        translate (bool, optional): If True, translates any language → English.
                                    Defaults to False.

    Returns:
        str: Transcribed (or translated) text.
    """
    client = _get_client()
    upload_path, was_compressed = _compress_for_upload(chunk_path)

    with open(upload_path, "rb") as f:
        file_data = f.read()

    filename = os.path.basename(upload_path)

    model = TRANSLATE_MODEL if translate else WHISPER_MODEL

    if translate:
        result = client.audio.translations.create(
            file=(filename, file_data),
            model=model,
            response_format="text",
        )
    else:
        result = client.audio.transcriptions.create(
            file=(filename, file_data),
            model=model,
            response_format="text",
        )

    # Clean up the temporary compressed file
    if was_compressed and os.path.exists(upload_path):
        os.remove(upload_path)

    return result


def cloud_transcribe_all(chunks: list, language: str = "english") -> str:
    """
    Transcribe all audio chunks and return the concatenated text.

    Args:
        chunks (list): List of file paths to audio chunks.
        language (str, optional): "hinglish" to translate to English, otherwise transcribe.

    Returns:
        str: Full transcription text.
    """
    full_transcription = ""
    translate = language.lower() == "hinglish"
    for i, chunk in enumerate(chunks):
        print(f"☁ Transcribing chunk {i + 1}/{len(chunks)}: {os.path.basename(chunk)}")
        transcription = transcribe_audio_chunk(chunk, translate)
        full_transcription += transcription + " "
    print("✅ Full transcription completed.")
    return full_transcription
