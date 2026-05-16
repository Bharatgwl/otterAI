from pydub import AudioSegment
import os

INPUT_FILE = "./downloads/LangChain Components ｜ GenAI using LangChain ｜ Video 2 ｜ CampusX.wav_chunk_5.wav"       # change to your file
OUTPUT_DIR = "test_chunks"
CHUNK_SEC = 25
NUM_CHUNKS = 5

os.makedirs(OUTPUT_DIR, exist_ok=True)

audio = AudioSegment.from_wav(INPUT_FILE)
chunk_ms = CHUNK_SEC * 1000

for i in range(NUM_CHUNKS):
    start = i * chunk_ms
    end = start + chunk_ms
    chunk = audio[start:end]
    out_path = os.path.join(OUTPUT_DIR, f"chunk_{i+1}.wav")
    chunk.export(out_path, format="wav")
    print(f"Saved chunk {i+1}: {start//1000}s → {end//1000}s  →  {out_path}")

print(f"\nDone! {NUM_CHUNKS} chunks saved in '{OUTPUT_DIR}/'")