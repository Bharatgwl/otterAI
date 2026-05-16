from utils.audio_processor import process_input
# from core.transcriber import         # ← local (slow)
from core.cloud_transcriber import cloud_transcribe_all     # ← cloud (fast)

# source = "https://youtu.be/-xSJA8-o6Eg?si=_vAOMc234TjEJ9zc"
source = "https://youtu.be/PN_YprabbxA?si=lXLyVhOGLrRAuJmA"
chunks = process_input(source)
transcription = cloud_transcribe_all(chunks, language="english")
print(transcription)
