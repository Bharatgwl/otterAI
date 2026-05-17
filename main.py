from dotenv import load_dotenv
from utils.audio_processor import process_input
from core.cloud_transcriber import cloud_transcribe_all
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain

# ── Intent detection ────────────────────────────────────────────────────────
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
    cleaned = text.lower().strip().rstrip("!?.,'")
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
        return "Goodbye! Come back anytime if you have more questions. 👋"
    if any(w in q for w in ["hello", "hi", "hey", "hyy", "hii", "helo", "yo"]):
        return f'Hey! I\'ve analyzed "{title}". Ask me anything — summaries, key points, or specific topics.'
    if any(w in q for w in ["how are you", "wassup", "sup", "what's up"]):
        return "Ready to help! What would you like to know about the video?"
    if any(w in q for w in ["good morning", "good night", "good evening"]):
        return "Hey! Ask me anything about the video content."
    return "I'm here! Ask me anything about the video content."


load_dotenv()

def run_pipeline(source: str, language: str = "english", engine: str = "cloud") -> dict:
    print("starting AI Video Assistant")

    chunks = process_input(source)

    # if function is cloud transcriber, it will handle both english and hinglish (translating to english while transcribing)
    
    transcript = ""
    engine = engine.lower().strip()

    if engine == "local":
        print("Using local transcription (Whisper / Sarvam).")
        transcript = transcribe_all(chunks, language=language)
    else:
        if language.lower() == "hinglish":
            print("Using cloud transcription (Groq AI) for Hinglish audio...")
        else:
            print("Using cloud transcription (Groq AI) for English audio...")
        transcript = cloud_transcribe_all(chunks, language=language)
    print(f"raw transcription (first 300 characters ) {transcript[:300]}")

    title = generate_title(transcript)

    summary = summarize(transcript)

    action_item = extract_action_items(transcript)

    decisions = extract_key_decisions(transcript)
    questions = extract_questions(transcript)
    
    rag_chain = build_rag_chain(transcript)

    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_item,
        "key_decisions": decisions,
        "open_questions": questions,
        "rag_chain": rag_chain,
    }

if __name__ == "__main__":
    # CLI entry point
    source = input("Enter YouTube URL or local file path: ").strip()
    language = input("Language (english/hinglish): ").strip() or "english"
    engine = input("Engine (cloud/local): ").strip() or "cloud"
    result = run_pipeline(source, language, engine)

    print("\n" + "=" * 60)
    print(f"📌 Title: {result['title']}")
    print(f"\n📋 Summary:\n{result['summary']}")
    print(f"\n✅ Action Items:\n{result['action_items']}")
    print(f"\n🔑 Key Decisions:\n{result['key_decisions']}")
    print(f"\n❓ Open Questions:\n{result['open_questions']}")
    print("=" * 60)

    # Phase 2 — Chat with your meeting via RAG
    print("\n💬 Chat with your meeting (type 'exit' to quit)\n")
    rag_chain = result["rag_chain"]
    title = result["title"]

    while True:
        question = input("You: ").strip()
        if question.lower() in ["exit", "quit", "q"]:
            print("👋 Goodbye!")
            break
        if not question:
            continue

        if is_casual(question):
            answer = casual_reply(question, title)
        else:
            answer = rag_chain.invoke(question)
            if "could not find" in answer.lower():
                answer = (
                    "I couldn't find that in the transcript. "
                    "Try rephrasing, or ask about a specific topic from the video."
                )

        print(f"\n🤖 Assistant: {answer}\n")