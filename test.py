from utils.audio_processor import process_input
from core.cloud_transcriber import cloud_transcribe_all
from core.transcriber import transcribe_all

source = "https://youtu.be/-xSJA8-o6Eg?si=HcvXpWH-7DLq6axV"
# source = "https://youtu.be/-xSJA8-o6Eg?si=bQQ3m2wlaSapYERB"
language = "hinglish"  # Change to "english" for English
engine = "cloud"  # "cloud" or "local"
chunks = process_input(source)
if engine == "local":
	transcription = transcribe_all(chunks, language=language)
else:
	transcription = cloud_transcribe_all(chunks, language=language)
print(transcription)

    