import yt_dlp
from pydub import AudioSegment
import os

DOWNLOAD_DIR = "downloads/"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_audio_from_youtube(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    # cookie file — works locally on Windows, skipped on HF Spaces / Linux
    cookie_path = os.path.join(os.path.dirname(__file__), "..", "www.youtube.com_cookies.txt")
    cookie_path = os.path.normpath(cookie_path)

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }

    # only pass cookiefile if it actually exists
    if os.path.exists(cookie_path):
        ydl_opts["cookiefile"] = cookie_path

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        for ext in [".webm", ".m4a", ".mp4", ".opus"]:
            filename = filename.replace(ext, ".wav")
    return filename


def convert_to_wav(input_path: str) -> str:
    if isinstance(input_path, tuple):
        input_path = input_path[0]

    base_name = input_path.rsplit(".", 1)[0]
    output_file = f"{base_name}_converted.wav"

    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_file, format="wav")

    return output_file


def chunk_audio(wav_path: str, chunk_mins: int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_mins * 60 * 1000
    chunks = []
    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    return chunks


def process_input(source: str) -> list:
    if source.startswith("http") or source.startswith("https://"):
        print("Downloading audio from YouTube...")
        audio_path = download_audio_from_youtube(source)
        wav_path = audio_path  # already .wav after yt-dlp post-processor
    else:
        print("Using local audio file... Converting to WAV format if necessary...")
        audio_path = source
        wav_path = convert_to_wav(audio_path)

    print("Chunking audio into smaller segments...")
    chunks = chunk_audio(wav_path)
    print(f"Processing complete. Generated {len(chunks)} chunks.")
    return chunks
