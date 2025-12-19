import ollama
from config import OLLAMA_MODEL

INTENTS = [
    "BOOK_APPOINTMENT",
    "VIEW_APPOINTMENT",
    "CANCEL_APPOINTMENT",
    "REPORT_SYMPTOMS",
    "GREETING",
    "UNKNOWN"
]

def detect_intent(user_text):
    prompt = f"""
You are an AI hospital receptionist.

Classify the user's intent into ONE of the following categories:
{', '.join(INTENTS)}

User message:
\"\"\"{user_text}\"\"\"

Reply with ONLY the intent name.
"""

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        intent = response["message"]["content"].strip().upper()
        if intent in INTENTS:
            return intent
        return "UNKNOWN"
    except:
        return "UNKNOWN"
