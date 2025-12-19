# import json
# import ollama

# from config import OLLAMA_MODEL

# INTENT_SCHEMA = {
#     "book_appointment": ["name", "age", "gender", "phone", "email", "department", "doctor", "date", "time", "reason"],
#     "view_appointment": ["phone"],
#     "cancel_appointment": ["phone"],
#     "general_query": []
# }

# SYSTEM_PROMPT = """
# You are an AI healthcare receptionist.
# Your job is to classify user intent and extract structured fields.

# Return ONLY valid JSON.
# Do not explain.
# Do not add extra text.

# Allowed intents:
# - book_appointment
# - view_appointment
# - cancel_appointment
# - general_query

# If a field is missing, return it as null.
# """

# def analyze_message(user_text):
#     prompt = f"""
# User message:
# \"\"\"{user_text}\"\"\"

# Return JSON in this format:
# {{
#   "intent": "<intent_name>",
#   "slots": {{
#     "name": null,
#     "age": null,
#     "gender": null,
#     "phone": null,
#     "email": null,
#     "department": null,
#     "doctor": null,
#     "date": null,
#     "time": null,
#     "reason": null
#   }}
# }}
# """

#     try:
#         response = ollama.chat(
#             model=OLLAMA_MODEL,
#             messages=[
#                 {"role": "system", "content": SYSTEM_PROMPT},
#                 {"role": "user", "content": prompt}
#             ]
#         )

#         raw = response["message"]["content"].strip()
#         parsed = json.loads(raw)

#         intent = parsed.get("intent", "general_query")
#         slots = parsed.get("slots", {})

#         if intent not in INTENT_SCHEMA:
#             intent = "general_query"

#         return intent, slots

#     except:
#         return "general_query", {}


# from enum import Enum

# class Intent(Enum):
#     BOOK_APPOINTMENT = "book_appointment"
#     VIEW_APPOINTMENT = "view_appointment"
#     CANCEL_APPOINTMENT = "cancel_appointment"
#     GREETING = "greeting"
#     UNKNOWN = "unknown"

# class State(Enum):
#     IDLE = "idle"
#     BOOK_NAME = "book_name"
#     VIEW_PHONE = "view_phone"
#     CANCEL_PHONE = "cancel_phone"

# def route_intent_to_state(intent: Intent):
#     if intent == Intent.BOOK_APPOINTMENT:
#         return State.BOOK_NAME
#     if intent == Intent.VIEW_APPOINTMENT:
#         return State.VIEW_PHONE
#     if intent == Intent.CANCEL_APPOINTMENT:
#         return State.CANCEL_PHONE
#     return State.IDLE

from enum import Enum

class Action(Enum):
    BOOK_APPOINTMENT = "book_appointment"
    VIEW_APPOINTMENT = "view_appointment"
    CANCEL_APPOINTMENT = "cancel_appointment"
    REPORT_SYMPTOMS = "report_symptoms"
    UNKNOWN = "unknown"

class RouterResult:
    def __init__(self, action, next_state, slots=None, message=None):
        self.action = action
        self.next_state = next_state
        self.slots = slots or {}
        self.message = message

def route_intent(intent, slots):
    intent = intent.lower()

    if intent == "book_appointment":
        return RouterResult(
            action=Action.BOOK_APPOINTMENT,
            next_state="BOOK_NAME",
            slots=slots
        )

    if intent == "view_appointment":
        return RouterResult(
            action=Action.VIEW_APPOINTMENT,
            next_state="VIEW_PHONE",
            slots=slots
        )

    if intent == "cancel_appointment":
        return RouterResult(
            action=Action.CANCEL_APPOINTMENT,
            next_state="CANCEL_PHONE",
            slots=slots
        )

    if intent == "report_symptoms":
        return RouterResult(
            action=Action.REPORT_SYMPTOMS,
            next_state="SYMPTOM_INPUT",
            slots=slots
        )

    return RouterResult(
        action=Action.UNKNOWN,
        next_state="IDLE",
        message="I can help you book, view, cancel appointments or report symptoms."
    )
