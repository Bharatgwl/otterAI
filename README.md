---
title: Otter.ai — AI Video Assistant
emoji: 🎬
colorFrom: purple
colorTo: pink
sdk: streamlit
sdk_version: "1.35.0"
app_file: app.py
pinned: false
license: mit
---

# 🎬 Otter.ai — AI Video Assistant

Transcribe, summarise, and chat with any YouTube video or audio file using AI.

## Features
- 🔊 **Audio Processing** — YouTube URLs or direct file uploads (MP4, MP3, WAV, M4A)
- 📝 **Cloud Transcription** — Groq Whisper API (fast, accurate, free tier available)
- 🌐 **Hinglish Support** — Transcribes and translates Hindi/Hinglish → English
- 📋 **AI Summarisation** — Structured meeting summaries via Mistral AI
- 🔍 **Smart Extraction** — Action items, key decisions, open questions
- 🧠 **RAG Chat** — Ask anything about the transcript with semantic search
- 💬 **Intent Detection** — Handles greetings and casual messages naturally

## Tech Stack
`Streamlit` · `Groq Whisper` · `Mistral AI` · `LangChain` · `ChromaDB` · `HuggingFace Embeddings` · `yt-dlp` · `pydub`

## Setup (local)
```bash
git clone https://huggingface.co/spaces/Bharatgwl/otter-ai
cd otter-ai
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
# Add your API keys to .env (see .env.example)
streamlit run app.py
```

## Environment Variables
Set these as **Space Secrets** (Settings → Variables and secrets):

| Key | Description |
|-----|-------------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) — free tier available |
| `MISTRAL_API_KEY` | [console.mistral.ai](https://console.mistral.ai) |
| `SARVAM_API_KEY` | Optional — for Hinglish local transcription |
