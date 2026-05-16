# import yt_dlp 
# from pydub import AudioSegment
# import os

# DOWNLOAD_DIR = "downloads/"
# os.makedirs(DOWNLOAD_DIR, exist_ok=True)
# def download_audio_from_youtube(url :str) ->str:
#     output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
#     ydl_opts = {
#         "format": "bestaudio/best",
#         "outtmpl": output_path,
#         "postprocessors": [
#             {
#                 "key": "FFmpegExtractAudio",
#                 "preferredcodec": "wav",
#                 "preferredquality": "192",
#             }
#         ],
#         "quiet": True,
#     }
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         info = ydl.extract_info(url, download=True)
#         filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")
#     return filename
# # def download_audio_from_youtube(url:str)->str:
# #     output_path  =os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
# #     ydl_opts = {
# #         'format': 'bestaudio/best',
# #         'outtmpl': output_path,
# #         'noplaylist': True,
# #         'cookiefile': 'cookies.txt',
# #         'postprocessors': [{
# #             'key': 'FFmpegExtractAudio',
# #             'preferredcodec': 'wav',
# #             'preferredquality': '192',
# #         }],
# #         # "outtml":'downloads/%(title)s.%(ext)s',
# #         'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
# #         "quiet": True
        
# #     }
# #     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
# #         info = ydl.extract_info(url, download=True)
# #         filename = ydl.prepare_filename(info).replace('.webm', '.wav').replace('.m4a', '.mp3')
# #     return filename

# # data = download_audio_from_youtube("https://youtu.be/Xl2CQWcoqbw?si=r8yhpGaWXTxnMLm0")

# # def convert_to_wav(input_path:str)->str:
# #     """_summary_

# #     Args:
# #         input_file (str): _description_

# #     Returns:
# #         str: _description_
# #     """
# #     output_file = os.path.splitext(input_path[0]+"_converted.wav")
# #     audio = AudioSegment.from_file(input_path)
# #     audio = audio.set_channels(1).set_frame_rate(16000)
# #     audio.export(output_file, format="wav")
# #     return output_file
# def convert_to_wav(input_path: str) -> str:
#     """
#     Converts an audio file to WAV format with 1 channel and 16000Hz frame rate.

#     Args:
#         input_path (str or tuple): The path to the input audio file.

#     Returns:
#         str: The path to the converted output WAV file.
#     """
#     # Fix for tuple issue: If yt-dlp returns a tuple, grab the first element
#     if isinstance(input_path, tuple):
#         input_path = input_path[0]
        
#     # Create the output filename safely using string splitting
#     # This splits on the LAST dot to remove the extension, then adds the new one
#     base_name = input_path.rsplit('.', 1)[0]
#     output_file = f"{base_name}_converted.wav"
    
#     # Process audio
#     audio = AudioSegment.from_file(input_path)
#     audio = audio.set_channels(1).set_frame_rate(16000)
#     audio.export(output_file, format="wav")
    
#     return output_file
# # final_data  = convert_to_wav(data)


# def chunk_audio(wav_path:str, chunk_mins:int=10)->list:
#     """_summary_

#     Args:
#         wav_path (str): _description_
#         chunk_length_ms (int, optional): _description_. Defaults to 30000.

#     Returns:
#         list: _description_
#     """
#     audio = AudioSegment.from_wav(wav_path)
#     chunk_ms = chunk_mins *60* 1000  # Convert seconds to milliseconds
#     chunks = []
#     for i ,start in enumerate(range(0, len(audio), chunk_ms)):
#         chunk = audio[start:start + chunk_ms]
#         chunk_path = f"{wav_path}_chunk_{i}.wav"
#         chunk.export(chunk_path, format="wav")
#         chunks.append(chunk_path)
#     return chunks

# # print(chunk_audio(final_data))

# def process_input(source:str)->list:
#     """_summary_

#     Args:
#         source (str): _description_

#     Returns:
#         list: _description_
#     """
#     if source.startswith("http") or source.startswith("https://"):
#         print("Downloading audio from YouTube...")
#         audio_path = download_audio_from_youtube(source)
#     else:
#         # audio_path = source
#         print("Using local audio file... Converting to WAV format if necessary...")
#         wav_path = convert_to_wav(audio_path)
#     print("Chunking audio into smaller segments...")
#     chunks = chunk_audio(wav_path)
#     print(f"Processing complete. Generated {len(chunks)} chunks.")
#     return chunks


import yt_dlp
from pydub import AudioSegment
import os

DOWNLOAD_DIR = "downloads/"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_audio_from_youtube(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        # ✅ Fix: pull cookies directly from your Chrome/Firefox session
        # "cookiefile": "cookies.txt",   # ✅ use exported file instead of browser
        'cookiefile': r"C:\Users\bhara\Desktop\Otter.ai\www.youtube.com_cookies.txt",
        # "cookiesfrombrowser": ("chrome",),  # fresh cookies, no expiry issues
        "js_runtimes": {"node": {}},
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        # yt-dlp renames the file after post-processing, handle all cases
        for ext in [".webm", ".m4a", ".mp4", ".opus"]:
            filename = filename.replace(ext, ".wav")
    return filename

# download_audio_from_youtube("https://youtu.be/Xl2CQWcoqbw?si=r8yhpGaWXTxnMLm0")
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
        wav_path = audio_path  # ✅ already converted to .wav by yt-dlp post-processor
    else:
        print("Using local audio file... Converting to WAV format if necessary...")
        audio_path = source           # ✅ Fix: was undefined before
        wav_path = convert_to_wav(audio_path)

    print("Chunking audio into smaller segments...")
    chunks = chunk_audio(wav_path)
    print(f"Processing complete. Generated {len(chunks)} chunks.")
    return chunks