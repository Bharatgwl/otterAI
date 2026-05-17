import streamlit as st
import time
import os
import tempfile
from dotenv import load_dotenv

# ── safe imports (no whisper/torch at module level to avoid torchvision crash)
from utils.audio_processor import process_input, chunk_audio, convert_to_wav
from core.cloud_transcriber import cloud_transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Otter.ai — AI Video Assistant",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# AURORA NEBULA THEME
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Space+Mono:wght@400;700&display=swap');

/* ── tokens ── */
:root {
    --bg:          #04040d;
    --glass:       rgba(255,255,255,0.03);
    --border:      rgba(255,255,255,0.07);
    --p1: #a855f7;
    --p2: #ec4899;
    --p3: #06b6d4;
    --p4: #3b82f6;
    --text:   #f0f0ff;
    --text-2: #a0a0c8;
    --text-3: #50508a;
    --green:  #10b981;
    --amber:  #f59e0b;
    --radius:    16px;
    --radius-sm: 10px;
}

/* ── base ── */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background: var(--bg) !important; overflow-x: hidden; }

/* ── aurora orbs ── */
.stApp::before, .stApp::after {
    content: '';
    position: fixed;
    border-radius: 50%;
    filter: blur(130px);
    pointer-events: none;
    z-index: 0;
    animation: drift 20s ease-in-out infinite alternate;
}
.stApp::before {
    width: 700px; height: 700px;
    top: -250px; left: -200px;
    background: radial-gradient(circle, rgba(168,85,247,0.20) 0%, rgba(59,130,246,0.08) 60%, transparent 100%);
}
.stApp::after {
    width: 600px; height: 600px;
    bottom: -200px; right: -100px;
    background: radial-gradient(circle, rgba(236,72,153,0.16) 0%, rgba(6,182,212,0.08) 60%, transparent 100%);
    animation-delay: -10s;
    animation-direction: alternate-reverse;
}
@keyframes drift {
    0%   { transform: translate(0px,  0px)  scale(1);    }
    50%  { transform: translate(60px, 45px) scale(1.08); }
    100% { transform: translate(-30px,80px) scale(0.95); }
}

/* ── sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(6,6,22,0.88) !important;
    backdrop-filter: blur(24px) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"]::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--p1), var(--p2), var(--p3));
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── typography ── */
h1,h2,h3,h4,h5,h6 { font-family: 'Outfit', sans-serif !important; color: var(--text) !important; }

.hero-title {
    font-family: 'Outfit', sans-serif;
    font-size: clamp(2.2rem, 5vw, 3.8rem);
    font-weight: 900; line-height: 1.05; margin: 0;
    background: linear-gradient(110deg, #fff 0%, #d8b4fe 28%, #ec4899 60%, #06b6d4 100%);
    background-size: 200% auto;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    animation: shimmer 5s linear infinite;
}
@keyframes shimmer { to { background-position: 200% center; } }

.hero-sub {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem; color: var(--text-3);
    letter-spacing: 0.25em; text-transform: uppercase; margin-top: 0.6rem;
}

/* ── glassmorphism cards ── */
.card {
    background: var(--glass);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem; margin-bottom: 1rem;
    position: relative; overflow: hidden;
    transition: border-color 0.3s, box-shadow 0.3s, transform 0.2s;
}
.card:hover {
    border-color: rgba(168,85,247,0.35);
    box-shadow: 0 0 40px rgba(168,85,247,0.08), inset 0 0 30px rgba(168,85,247,0.03);
    transform: translateY(-2px);
}
.card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--p1), var(--p2), var(--p3), var(--p4), var(--p1));
    background-size: 300% 100%;
    animation: borderFlow 4s linear infinite;
    opacity: 0.75;
}
@keyframes borderFlow { to { background-position: 300% 0; } }
.card::after {
    content: ''; position: absolute;
    top: -60px; right: -60px;
    width: 160px; height: 160px;
    background: radial-gradient(circle, rgba(168,85,247,0.06) 0%, transparent 70%);
    border-radius: 50%; pointer-events: none;
}
.card-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem; font-weight: 700;
    letter-spacing: 0.2em; text-transform: uppercase;
    color: var(--text-3); margin-bottom: 0.85rem;
}
.card-content { font-size: 0.88rem; line-height: 1.75; color: var(--text-2); }

/* ── badges ── */
.badge {
    display: inline-flex; align-items: center; gap: 0.3rem;
    padding: 0.22rem 0.7rem; border-radius: 100px;
    font-family: 'Space Mono', monospace;
    font-size: 0.58rem; font-weight: 700;
    letter-spacing: 0.12em; text-transform: uppercase;
}
.badge-purple { background: rgba(168,85,247,0.12); color: #c084fc; border: 1px solid rgba(168,85,247,0.25); box-shadow: 0 0 12px rgba(168,85,247,0.15); }
.badge-cyan   { background: rgba(6,182,212,0.10);  color: #22d3ee; border: 1px solid rgba(6,182,212,0.25);   box-shadow: 0 0 12px rgba(6,182,212,0.12); }
.badge-green  { background: rgba(16,185,129,0.10); color: #34d399; border: 1px solid rgba(16,185,129,0.25);  box-shadow: 0 0 12px rgba(16,185,129,0.12); }
.badge-orange { background: rgba(245,158,11,0.10); color: #fbbf24; border: 1px solid rgba(245,158,11,0.25);  box-shadow: 0 0 12px rgba(245,158,11,0.12); }
.badge-pink   { background: rgba(236,72,153,0.10); color: #f472b6; border: 1px solid rgba(236,72,153,0.25);  box-shadow: 0 0 12px rgba(236,72,153,0.12); }

/* ── inputs ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.9rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(168,85,247,0.6) !important;
    box-shadow: 0 0 0 3px rgba(168,85,247,0.12), 0 0 20px rgba(168,85,247,0.1) !important;
    background: rgba(168,85,247,0.04) !important;
}
.stTextInput > div > div > input::placeholder { color: var(--text-3) !important; }
.stSelectbox > div > div, .stSelectbox > div > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
    font-family: 'Outfit', sans-serif !important;
}

/* ── buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed 0%, #a855f7 45%, #ec4899 100%) !important;
    background-size: 200% 200% !important;
    color: white !important; border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important; font-size: 0.85rem !important;
    letter-spacing: 0.06em !important; padding: 0.65rem 1.6rem !important;
    transition: all 0.25s !important; text-transform: uppercase !important;
    animation: gradShift 4s ease infinite !important;
}
@keyframes gradShift {
    0%,100% { background-position: 0% 50%; }
    50%      { background-position: 100% 50%; }
}
.stButton > button:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 12px 35px rgba(168,85,247,0.45), 0 0 60px rgba(236,72,153,0.2) !important;
}
.stButton > button:active { transform: translateY(0) scale(0.99) !important; }

/* download button override */
[data-testid="stDownloadButton"] > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-2) !important;
    border-radius: var(--radius-sm) !important;
    font-size: 0.82rem !important; font-weight: 500 !important;
    text-transform: none !important; letter-spacing: 0 !important;
    animation: none !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(168,85,247,0.1) !important;
    border-color: rgba(168,85,247,0.4) !important;
    color: #c084fc !important;
    box-shadow: 0 4px 15px rgba(168,85,247,0.15) !important;
    transform: translateY(-1px) !important;
}

/* ── pipeline status ── */
.status-bar {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.65rem 1rem;
    background: rgba(255,255,255,0.025);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    margin: 0.3rem 0; font-size: 0.8rem;
    font-family: 'Outfit', sans-serif;
    transition: background 0.25s;
}
.status-bar:hover { background: rgba(255,255,255,0.04); }
.status-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dot-pending { background: var(--text-3); }
.dot-done    { background: var(--green);  box-shadow: 0 0 8px var(--green); }
.dot-active  { background: var(--p1); animation: sonar 1.4s ease-out infinite; }
@keyframes sonar {
    0%  { box-shadow: 0 0 0 0   rgba(168,85,247,0.7); }
    70% { box-shadow: 0 0 0 8px rgba(168,85,247,0);   }
    100%{ box-shadow: 0 0 0 0   rgba(168,85,247,0);   }
}

/* ── chat ── */
.chat-container {
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem;
    max-height: 460px; overflow-y: auto;
    margin-bottom: 1rem;
    backdrop-filter: blur(12px);
}
.chat-msg { margin-bottom: 1.1rem; display: flex; flex-direction: column; gap: 0.25rem; }
.chat-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.58rem; font-weight: 700;
    letter-spacing: 0.18em; text-transform: uppercase;
}
.chat-bubble {
    display: inline-block; padding: 0.75rem 1.1rem;
    border-radius: 14px; font-size: 0.88rem; line-height: 1.65;
    max-width: 88%; font-family: 'Outfit', sans-serif;
}
.user-label  { color: #c084fc; }
.bot-label   { color: #22d3ee; }
.user-bubble {
    background: linear-gradient(135deg, rgba(168,85,247,0.18), rgba(236,72,153,0.12));
    border: 1px solid rgba(168,85,247,0.3); align-self: flex-end;
    box-shadow: 0 4px 20px rgba(168,85,247,0.12);
}
.bot-bubble {
    background: linear-gradient(135deg, rgba(6,182,212,0.12), rgba(59,130,246,0.08));
    border: 1px solid rgba(6,182,212,0.25); align-self: flex-start;
    box-shadow: 0 4px 20px rgba(6,182,212,0.08);
}

/* ── transcript box ── */
.transcript-box {
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm); padding: 1.25rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.76rem; line-height: 1.9;
    max-height: 320px; overflow-y: auto;
    color: var(--text-3); white-space: pre-wrap; word-break: break-word;
}

/* ── misc overrides ── */
hr {
    border: none !important; height: 1px !important;
    background: linear-gradient(90deg, transparent, var(--border), transparent) !important;
    margin: 1.75rem 0 !important;
}
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--p1), var(--p2)) !important;
    border-radius: 100px !important;
}
.stSpinner > div { border-top-color: var(--p1) !important; }
[data-testid="stMarkdownContainer"] p { color: var(--text-2) !important; }
label {
    color: var(--text-3) !important; font-size: 0.78rem !important;
    font-family: 'Space Mono', monospace !important; letter-spacing: 0.05em !important;
}
[data-testid="stFileUploader"] {
    background: rgba(168,85,247,0.03) !important;
    border: 1px dashed rgba(168,85,247,0.25) !important;
    border-radius: var(--radius-sm) !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(168,85,247,0.5) !important;
    background: rgba(168,85,247,0.06) !important;
}
[data-testid="stRadio"] label { color: var(--text-2) !important; }
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
}
[data-testid="stExpander"] summary { color: var(--text-2) !important; }
.stAlert { border-radius: var(--radius-sm) !important; backdrop-filter: blur(10px) !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--p1), var(--p2));
    border-radius: 100px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# INTENT DETECTION  (mirrors main.py exactly)
# ─────────────────────────────────────────────────────────────────────────────
CASUAL_TRIGGERS = {
    "hello", "hi", "hey", "hyy", "hii", "helo", "heyy", "yo",
    "bye", "goodbye", "see you", "see ya",
    "ok", "okay", "k",
    "thanks", "thank you", "thank u", "ty", "thx",
    "how are you", "how r u", "what's up", "wassup", "sup",
    "good morning", "good night", "good evening",
    "lol", "haha", "nice", "cool", "great", "awesome",
}
CONTENT_WORDS = {
    "summarize", "summary", "explain", "what", "who", "how",
    "when", "where", "why", "tell", "give", "list", "find",
    "key", "main", "point", "topic", "mention", "say", "said",
    "discuss", "advice", "tip", "strategy", "takeaway",
}

def is_casual(text: str) -> bool:
    cleaned = text.lower().strip().rstrip("!?.,\\'")
    if cleaned in CASUAL_TRIGGERS:
        return True
    for trigger in CASUAL_TRIGGERS:
        if cleaned.startswith(trigger + " ") or cleaned == trigger:
            return True
    words = cleaned.split()
    if len(words) <= 2 and not any(w in CONTENT_WORDS for w in words):
        return True
    return False

def casual_reply(text: str, title: str) -> str:
    q = text.lower()
    if any(w in q for w in ["thank", "thanks", "ty", "thx"]):
        return "You're welcome! Feel free to ask anything about the video."
    if any(w in q for w in ["bye", "goodbye", "see you", "see ya"]):
        return "Goodbye! Come back anytime. 👋"
    if any(w in q for w in ["hello", "hi", "hey", "hyy", "hii", "helo", "yo"]):
        return f'Hey! I\'ve analyzed "{title}". Ask me anything — summaries, key points, or specific topics.'
    if any(w in q for w in ["how are you", "wassup", "sup", "what's up"]):
        return "Ready to help! What would you like to know about the video?"
    if any(w in q for w in ["good morning", "good night", "good evening"]):
        return "Hey! Ask me anything about the video content."
    return "I'm here! Ask me anything about the video content."

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
for _k, _v in {
    "result": None,
    "chat_history": [],
    "pipeline_done": False,
    "pipeline_steps": {},
    "error": None,
    "uploaded_bytes": None,
    "uploaded_name": None,
}.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
PIPELINE_STEPS = [
    ("audio",      "🔊", "Audio Processing"),
    ("transcript", "📝", "Transcription"),
    ("title",      "🏷️",  "Title Generation"),
    ("summary",    "📋", "Summarisation"),
    ("extract",    "🔍", "Extraction"),
    ("rag",        "🧠", "RAG Engine"),
]

def set_step(key: str, state: str):
    st.session_state.pipeline_steps[key] = state

def render_step(icon: str, label: str, key: str):
    s   = st.session_state.pipeline_steps.get(key, "pending")
    dot = "dot-active" if s == "active" else ("dot-done" if s == "done" else "dot-pending")
    st.markdown(
        f'<div class="status-bar"><div class="status-dot {dot}"></div>'
        f'<span>{icon}&nbsp;{label}</span></div>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="hero-title" style="font-size:1.5rem;line-height:1.2">🎬 Otter<br><span style="-webkit-text-fill-color:#a855f7">.ai</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="hero-sub">Meeting Intelligence</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown('<span class="badge badge-purple">Source</span>', unsafe_allow_html=True)
    input_mode = st.radio(
        "Input type", ["YouTube URL", "Local File"],
        horizontal=True, label_visibility="collapsed",
    )

    source_url = ""
    if input_mode == "YouTube URL":
        source_url = st.text_input(
            "url", placeholder="https://youtu.be/...",
            label_visibility="collapsed",
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload audio/video",
            type=["mp4", "mp3", "wav", "m4a", "webm", "mkv"],
            label_visibility="collapsed",
        )
        # Persist bytes in session so they survive st.rerun()
        if uploaded_file is not None:
            st.session_state.uploaded_bytes = uploaded_file.read()
            st.session_state.uploaded_name  = uploaded_file.name

    st.markdown("---")
    st.markdown('<span class="badge badge-cyan">Settings</span>', unsafe_allow_html=True)
    language = st.selectbox("Language", ["english", "hinglish"], index=0)
    engine   = st.selectbox("Engine", ["cloud (Groq)", "local (Whisper)"], index=0)

    run_btn = st.button("⚡  Analyse", use_container_width=True)

    if st.session_state.pipeline_done or st.session_state.pipeline_steps:
        st.markdown("---")
        st.markdown('<span class="badge badge-green">Pipeline Status</span>', unsafe_allow_html=True)
        for _key, _icon, _label in PIPELINE_STEPS:
            render_step(_icon, _label, _key)

    if st.session_state.error:
        st.markdown("---")
        st.error(st.session_state.error)

# ─────────────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">AI Video Assistant</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Transcribe · Summarise · Chat with your meetings</div>',
    unsafe_allow_html=True,
)
st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE
# ─────────────────────────────────────────────────────────────────────────────
if run_btn:
    has_url  = input_mode == "YouTube URL" and bool(source_url.strip())
    has_file = input_mode == "Local File"  and st.session_state.uploaded_bytes is not None

    if not has_url and not has_file:
        st.error("Please provide a YouTube URL or upload a file.")
    else:
        st.session_state.update({
            "result": None,
            "chat_history": [],
            "pipeline_done": False,
            "pipeline_steps": {},
            "error": None,
        })

        status = st.empty()
        use_cloud = "cloud" in engine

        try:
            # ── Step 1: Audio ─────────────────────────────────────────────
            set_step("audio", "active")
            status.info("🔊 Processing audio…")

            if has_file:
                suffix   = os.path.splitext(st.session_state.uploaded_name)[1] or ".wav"
                tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                tmp_file.write(st.session_state.uploaded_bytes)
                tmp_file.close()
                tmp_path = tmp_file.name

                if suffix.lower() != ".wav":
                    wav_path = convert_to_wav(tmp_path)
                    os.unlink(tmp_path)
                else:
                    wav_path = tmp_path

                chunks = chunk_audio(wav_path)
            else:
                chunks = process_input(source_url.strip())

            set_step("audio", "done")

            # ── Step 2: Transcription ──────────────────────────────────────
            set_step("transcript", "active")
            status.info(f"📝 Transcribing via {'Groq Cloud' if use_cloud else 'Whisper Local'}…")

            if use_cloud:
                transcript = cloud_transcribe_all(chunks, language=language)
            else:
                # lazy import to avoid torchvision crash on Streamlit startup
                from core.transcriber import transcribe_all
                transcript = transcribe_all(chunks, language=language)

            set_step("transcript", "done")

            # ── Step 3: Title ──────────────────────────────────────────────
            set_step("title", "active")
            status.info("🏷️ Generating title…")
            title = generate_title(transcript)
            set_step("title", "done")

            # ── Step 4: Summary ────────────────────────────────────────────
            set_step("summary", "active")
            status.info("📋 Summarising…")
            summary = summarize(transcript)
            set_step("summary", "done")

            # ── Step 5: Extraction ─────────────────────────────────────────
            set_step("extract", "active")
            status.info("🔍 Extracting action items, decisions & questions…")
            action_items = extract_action_items(transcript)
            decisions    = extract_key_decisions(transcript)
            questions    = extract_questions(transcript)
            set_step("extract", "done")

            # ── Step 6: RAG ────────────────────────────────────────────────
            set_step("rag", "active")
            status.info("🧠 Building RAG engine…")
            rag_chain = build_rag_chain(transcript)
            set_step("rag", "done")

            st.session_state.result = {
                "title":          title,
                "transcript":     transcript,
                "summary":        summary,
                "action_items":   action_items,
                "key_decisions":  decisions,
                "open_questions": questions,
                "rag_chain":      rag_chain,
            }
            st.session_state.pipeline_done = True
            status.success("✅ Analysis complete!")
            time.sleep(0.7)
            status.empty()
            st.rerun()

        except Exception as e:
            for _k, _, _ in PIPELINE_STEPS:
                if st.session_state.pipeline_steps.get(_k) == "active":
                    st.session_state.pipeline_steps[_k] = "pending"
            st.session_state.error = f"Pipeline error: {e}"
            status.error(f"❌ {e}")

# ─────────────────────────────────────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    # title card
    st.markdown(f"""
    <div class="card">
        <div class="card-title">📌 Session Title</div>
        <div style="font-family:'Outfit',sans-serif;font-size:1.35rem;font-weight:800;
                    background:linear-gradient(110deg,#fff,#d8b4fe 60%,#ec4899);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;">
            {r['title']}
        </div>
    </div>""", unsafe_allow_html=True)

    # summary + transcript
    col1, col2 = st.columns([3, 2], gap="medium")
    with col1:
        st.markdown(f"""
        <div class="card">
            <div class="card-title">📋 Summary</div>
            <div class="card-content">{r['summary']}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        with st.expander("📝 Full Transcript", expanded=False):
            st.markdown(
                f'<div class="transcript-box">{r["transcript"]}</div>',
                unsafe_allow_html=True,
            )
        st.download_button(
            label="⬇️ Download Transcript",
            data=r["transcript"],
            file_name=f"{r['title']}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # action items | decisions | questions
    c1, c2, c3 = st.columns(3, gap="medium")
    for col, key, label in [
        (c1, "action_items",   "✅ Action Items"),
        (c2, "key_decisions",  "🔑 Key Decisions"),
        (c3, "open_questions", "❓ Open Questions"),
    ]:
        with col:
            st.markdown(f"""
            <div class="card">
                <div class="card-title">{label}</div>
                <div class="card-content">{r[key]}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Chat ──────────────────────────────────────────────────────────────────
    st.markdown(
        '<div style="font-family:\'Outfit\',sans-serif;font-size:1.15rem;'
        'font-weight:800;margin-bottom:1rem;color:var(--text)">💬 Chat with your Meeting</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.chat_history:
        html = '<div class="chat-container">'
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                html += (
                    '<div class="chat-msg" style="align-items:flex-end">'
                    '<span class="chat-label user-label">You</span>'
                    f'<div class="chat-bubble user-bubble">{msg["content"]}</div>'
                    '</div>'
                )
            else:
                html += (
                    '<div class="chat-msg" style="align-items:flex-start">'
                    '<span class="chat-label bot-label">🤖 Assistant</span>'
                    f'<div class="chat-bubble bot-bubble">{msg["content"]}</div>'
                    '</div>'
                )
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card" style="text-align:center;padding:2.5rem">
            <div style="font-size:2rem;margin-bottom:0.5rem">💬</div>
            <div style="color:var(--text-3);font-size:0.85rem">
                Ask anything about your meeting transcript
            </div>
        </div>""", unsafe_allow_html=True)

    with st.form(key="chat_form", clear_on_submit=True):
        chat_col, btn_col = st.columns([5, 1], gap="small")
        with chat_col:
            user_input = st.text_input(
                "question",
                placeholder="What were the key takeaways? (Enter to send)",
                label_visibility="collapsed",
            )
        with btn_col:
            send_btn = st.form_submit_button("Send →", use_container_width=True)

    if send_btn and user_input.strip():
        question = user_input.strip()
        if is_casual(question):
            answer = casual_reply(question, r["title"])
        else:
            with st.spinner("Thinking…"):
                answer = r["rag_chain"].invoke(question)
            if "could not find" in answer.lower():
                answer = (
                    "I couldn't find that in the transcript. "
                    "Try rephrasing, or ask about a specific topic from the video."
                )
        st.session_state.chat_history.append({"role": "user",      "content": question})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# EMPTY STATE
# ─────────────────────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;
                justify-content:center;padding:5rem 2rem;text-align:center">
        <div style="font-size:4rem;margin-bottom:1rem;
                    filter:drop-shadow(0 0 30px rgba(168,85,247,0.5))">🎬</div>
        <div style="font-family:'Outfit',sans-serif;font-size:1.5rem;
                    font-weight:800;color:var(--text);margin-bottom:0.5rem">
            Ready to Analyse
        </div>
        <div style="color:var(--text-3);font-size:0.875rem;
                    max-width:420px;line-height:1.75">
            Paste a YouTube URL or upload a local file in the sidebar,
            choose your language &amp; engine, then hit
            <strong style="color:var(--text-2)">Analyse</strong>.
        </div>
        <div style="margin-top:2rem;display:flex;gap:0.75rem;flex-wrap:wrap;justify-content:center">
            <span class="badge badge-purple">Cloud · Groq Whisper</span>
            <span class="badge badge-cyan">Local · Whisper</span>
            <span class="badge badge-orange">Hinglish → English</span>
            <span class="badge badge-green">RAG Chat</span>
        </div>
        <div style="margin-top:0.75rem;display:flex;gap:0.75rem;flex-wrap:wrap;justify-content:center">
            <span class="badge badge-purple">YouTube URLs</span>
            <span class="badge badge-pink">MP4 · MP3 · WAV · M4A</span>
        </div>
    </div>""", unsafe_allow_html=True)
